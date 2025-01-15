"""
The Client module contains the main classes used to interact with the Arraylake service.
For asyncio interaction, use the #AsyncClient. For regular, non-async interaction, use the #Client.

**Example usage:**

```python
from arraylake import Client
client = Client()
repo = client.get_repo("my-org/my-repo")
```
"""
# mypy: disable-error-code="name-defined"
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Literal, Optional, Union
from urllib.parse import urlparse
from uuid import UUID

from arraylake.asyn import sync
from arraylake.compute.services import AsyncComputeClient, ComputeClient
from arraylake.config import config
from arraylake.exceptions import BucketNotFoundError
from arraylake.log_util import get_logger
from arraylake.repos import _raise_if_zarr_v3
from arraylake.repos.icechunk.utils import (
    _raise_if_no_icechunk,
    icechunk_repo_from_repo_model,
)
from arraylake.repos.v1.chunkstore import (
    Chunkstore,
    mk_chunkstore_from_bucket_config,
    mk_chunkstore_from_uri,
)
from arraylake.repos.v1.metastore import HttpMetastore, HttpMetastoreConfig
from arraylake.token import get_auth_handler
from arraylake.types import (
    DBID,
    Author,
    BucketResponse,
    HmacAuth,
    LegacyBucketResponse,
    NewBucket,
    OrgActions,
)
from arraylake.types import Repo as RepoModel
from arraylake.types import (
    RepoActions,
    RepoKind,
    RepoOperationMode,
    RepoOperationStatusResponse,
    S3Credentials,
)

logger = get_logger(__name__)

_VALID_NAME = r"(\w[\w\.\-_]+)"

_DEFAULT_NEW_REPO_KIND = RepoKind.V1


def _parse_org_and_repo(org_and_repo: str) -> tuple[str, str]:
    expr = f"{_VALID_NAME}/{_VALID_NAME}"
    res = re.fullmatch(expr, org_and_repo)
    if not res:
        raise ValueError(f"Not a valid repo identifier: `{org_and_repo}`. " "Should have the form `[ORG]/[REPO]`.")
    org, repo_name = res.groups()
    return org, repo_name


def _validate_org(org_name: str):
    if not re.fullmatch(_VALID_NAME, org_name):
        raise ValueError(f"Invalid org name: `{org_name}`.")


def _default_service_uri() -> str:
    return config.get("service.uri", "https://api.earthmover.io")


def _default_token() -> Optional[str]:
    return config.get("token", None)


@dataclass
class AsyncClient:
    """Asyncio Client for interacting with ArrayLake

    Args:
        service_uri:
            [Optional] The service URI to target.
        token:
            [Optional] API token for service account authentication.
    """

    service_uri: str = field(default_factory=_default_service_uri)
    token: Optional[str] = field(default_factory=_default_token, repr=False)

    def __post_init__(self):
        if self.token is not None and not self.token.startswith("ema_"):
            raise ValueError("Invalid token provided. Tokens must start with ema_")
        if not self.service_uri.startswith("http"):
            raise ValueError("service uri must start with http")

    def _metastore_for_org(self, org: str) -> HttpMetastore:
        _validate_org(org)
        return HttpMetastore(HttpMetastoreConfig(self.service_uri, org, self.token))

    async def list_repos(self, org: str) -> Sequence[RepoModel]:
        """List all repositories for the specified org

        Args:
            org: Name of the org
        """

        mstore = self._metastore_for_org(org)
        repo_models = await mstore.list_databases()
        return repo_models

    @staticmethod
    def _use_delegated_credentials(bucket: Union[BucketResponse, LegacyBucketResponse, None]) -> bool:
        """Check if the bucket is using delegated credentials."""
        if (
            isinstance(bucket, BucketResponse)
            and bucket.auth_config
            and bucket.auth_config.method == "customer_managed_role"
            and bucket.platform == "s3"
            and config.get("chunkstore.use_delegated_credentials", True)
        ):
            return True
        return False

    @staticmethod
    def _use_hmac_credentials(bucket: Union[BucketResponse, LegacyBucketResponse, None]) -> bool:
        """Check if the bucket is using HMAC credentials."""
        if isinstance(bucket, BucketResponse) and isinstance(bucket.auth_config, HmacAuth) and bucket.platform != "gs":
            return True
        return False

    async def _get_s3_delegated_credentials(self, org: str, repo_name: str) -> S3Credentials:
        """Get delegated credentials for a S3 bucket.

        Args:
            org: Name of the organization.
            repo_name: Name of the repository.

        Returns:
            S3Credentials: Temporary credentials for the S3 bucket.
        """
        mstore = self._metastore_for_org(org)
        s3_creds = await mstore.get_s3_bucket_credentials(repo_name)
        return s3_creds

    async def _get_hmac_credentials(self, bucket: BucketResponse) -> S3Credentials:
        """Get HMAC credentials for a object store bucket.

        Args:
            bucket: BucketResponse object containing the bucket nickname.

        Returns:
            S3Credentials: HMAC credentials for the S3 bucket.
        """
        # We must check these again or else mypy freaks out
        assert isinstance(bucket, BucketResponse)
        assert isinstance(bucket.auth_config, HmacAuth)
        return S3Credentials(
            aws_access_key_id=bucket.auth_config.access_key_id,
            aws_secret_access_key=bucket.auth_config.secret_access_key,
            aws_session_token=None,
            expiration=None,
        )

    async def _maybe_get_credentials_for_icechunk(self, bucket: BucketResponse, org: str, repo_name: str) -> S3Credentials | None:
        """Checks if the bucket is configured for delegated or HMAC credentials and gets the
        credentials if it is configured.

        Returns None if delegated or HMAC credentials are not configured for the bucket.
        """
        if self._use_delegated_credentials(bucket):
            return await self._get_s3_delegated_credentials(org, repo_name)
        elif self._use_hmac_credentials(bucket):
            return await self._get_hmac_credentials(bucket)
        return None

    # TODO: move init_chunkstore out of client to V1 Repo
    async def _init_chunkstore(
        self, repo_id: DBID, bucket: Union[BucketResponse, LegacyBucketResponse, None], org: str, repo_name: str
    ) -> Chunkstore:
        inline_threshold_bytes = int(config.get("chunkstore.inline_threshold_bytes", 0))
        fetch_credentials_func = None
        cache_key: tuple[Any, ...] = ()
        if bucket is None:
            chunkstore_uri = config.get("chunkstore.uri")
            if chunkstore_uri is None:
                raise ValueError("Chunkstore uri is None. Please set it using: `arraylake config set chunkstore.uri URI`.")
            if chunkstore_uri.startswith("s3"):
                client_kws = config.get("s3", {})
            elif chunkstore_uri.startswith("gs"):
                client_kws = config.get("gs", {})
            else:
                raise ValueError(f"Unsupported chunkstore uri: {chunkstore_uri}")
            return mk_chunkstore_from_uri(chunkstore_uri, inline_threshold_bytes, **client_kws)
        else:
            # TODO: for now, we just punt and use the s3 namespace for server-managed
            # bucket configs. This should be generalized to support GCS.
            client_kws = config.get("s3", {})
            # Check if the bucket is using delegated credentials
            if self._use_delegated_credentials(bucket):
                # If it is, pass the `_get_s3_delegated_credentials` function to the chunkstore
                fetch_credentials_func = partial(self._get_s3_delegated_credentials, org, repo_name)  # noqa
                # Add the org, repo_name, and function name to the cache key
                cache_key = (org, repo_name, fetch_credentials_func.func.__name__)
            elif self._use_hmac_credentials(bucket):
                # We must check these again or else mypy freaks out
                assert isinstance(bucket, BucketResponse)
                assert isinstance(bucket.auth_config, HmacAuth)
                # Add the HMAC creds to the client kwargs
                # we must do a copy of the kwargs so we don't modify the config directly
                client_kws = client_kws.copy()
                # note that all supported platforms use the key words aws_access_key_id and aws_secret_access_key
                client_kws.update(
                    {"aws_access_key_id": bucket.auth_config.access_key_id, "aws_secret_access_key": bucket.auth_config.secret_access_key}
                )
            return mk_chunkstore_from_bucket_config(
                bucket,
                repo_id,
                inline_threshold_bytes,
                fetch_credentials_func,  # type: ignore
                cache_key,
                **client_kws,
            )

    async def get_repo_object(self, name: str) -> RepoModel:
        """Get the repo configuration object.

        See `get_repo` for an instantiated repo.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
        """
        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)

        repo_model = await mstore.get_database(repo_name)
        return repo_model

    async def get_repo(
        self, name: str, *, checkout: Optional[bool] = None, read_only: bool = False
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Get a repo by name

        Args:
            name:
                Full name of the repo (of the form [ORG]/[REPO])
            checkout:
                Automatically checkout the repo after instantiation.
                Defaults to True for V1 repos and False for icechunk repos.
            read_only:
                Open the repo in read-only mode.

        Returns:
            A V1 AsyncRepo object or an IcechunkRepository object.
        """
        org, repo_name = _parse_org_and_repo(name)
        repo_model = await self.get_repo_object(name)

        mstore = HttpMetastore(HttpMetastoreConfig(self.service_uri, org, self.token))

        user = await mstore.get_user()
        author: Author = user.as_author()

        if repo_model.kind == RepoKind.V1:
            import arraylake.repos.v1.repo as repo_v1

            # Set checkout to True if it is None
            checkout = True if checkout is None else checkout

            db = await mstore.open_database(repo_name)
            cstore = await self._init_chunkstore(repo_model.id, repo_model.bucket, org, repo_name)

            arepo = repo_v1.AsyncRepo(db, cstore, name, author)
            if checkout:
                await arepo.checkout(for_writing=(not read_only))
            return arepo

        elif repo_model.kind == RepoKind.V2:
            # Set checkout to False if it is None
            # TODO: how should be handle read only and checkouts for icechunk repos?
            checkout = False if checkout is None else checkout

            _raise_if_no_icechunk()
            if not isinstance(repo_model.bucket, BucketResponse):
                raise ValueError("The bucket on the catalog object must be a BucketResponse for Icechunk V2 repos!")
            credentials = await self._maybe_get_credentials_for_icechunk(bucket=repo_model.bucket, org=org, repo_name=repo_name)
            return await icechunk_repo_from_repo_model(repo_model=repo_model, prefix=None, s3_credentials=credentials)

        else:
            raise ValueError(f"Invalid repo kind: {repo_model.kind}")

    async def _set_repo_status(
        self, qualified_repo_name: str, mode: RepoOperationMode, message: str | None = None
    ) -> RepoOperationStatusResponse:
        """Sets the repo status to the given mode.

        Args:
            qualified_repo_name: Full name of the repo (of the form [ORG]/[REPO])
            mode: The mode to set the repo to.
            message: Optional message to associate with the mode change.

        Returns:
            RepoOperationStatusResponse object containing mode change outputs.
        """
        org, repo_name = _parse_org_and_repo(qualified_repo_name)
        mstore = self._metastore_for_org(org)
        return await mstore.set_repo_status(repo_name, mode, message)

    async def get_or_create_repo(
        self,
        name: str,
        *,
        checkout: Optional[bool] = None,
        bucket_config_nickname: Optional[str] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Get a repo by name. Create the repo if it doesn't already exist.

        Args:
            name:
                Full name of the repo (of the form [ORG]/[REPO])
            checkout:
                Whether to checkout the repo after instantiation.
                If the repo does not exist, checkout is ignored.
                Ignored if specified for a Icechunk repo.
            bucket_config_nickname:
                The created repo will use this bucket for its chunks.
                If the repo exists, bucket_config_nickname is ignored.
            kind:
                The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix:
                Optional prefix for Icechunk store. Only used for Icechunk V2 repos.
                If not provided, the repo ID will be used.

        Returns:
            A V1 AsyncRepo object or IcechunkRepository
        """
        org, repo_name = _parse_org_and_repo(name)
        repos = [r for r in await self.list_repos(org) if r.name == repo_name]
        if repos:
            (repo,) = repos
            if bucket_config_nickname:
                if repo.bucket and bucket_config_nickname != repo.bucket.nickname:
                    raise ValueError(
                        f"This repo exists, but the provided {bucket_config_nickname=} "
                        f"does not match the configured bucket_config_nickname {repo.bucket.nickname!r}."
                    )
                elif not repo.bucket:
                    raise ValueError(
                        "This repo exists, but does not have a bucket config attached. Please remove the bucket_config_nickname argument."
                    )
                else:
                    return await self.get_repo(name, checkout=checkout)
            return await self.get_repo(name, checkout=checkout)
        else:
            return await self.create_repo(name, bucket_config_nickname=bucket_config_nickname, kind=kind, prefix=prefix)

    async def create_repo(
        self, name: str, *, bucket_config_nickname: Optional[str] = None, kind: Optional[RepoKind] = None, prefix: Optional[str] = None
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Create a new repo

        Args:
            name:
                Full name of the repo to create (of the form [ORG]/[REPO])
            bucket_config_nickname:
                An optional bucket to use for the chunkstore
            kind:
                The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix:
                Optional prefix for Icechunk store. Only used for Icechunk V2 repos.
                If not provided, the repo ID will be used.
        """
        # Check that we can import the correct repo type
        if kind is None:
            kind = _DEFAULT_NEW_REPO_KIND

        if kind == RepoKind.V1:
            _raise_if_zarr_v3()
            import arraylake.repos.v1.repo as repo_v1
        elif kind == RepoKind.V2:
            _raise_if_no_icechunk()
        else:
            raise ValueError(f"Invalid repo kind: {kind}")

        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)

        repo_model = await mstore.create_database(repo_name, bucket_config_nickname, kind=kind)
        user = await mstore.get_user()
        author: Author = user.as_author()

        if kind == RepoKind.V1:
            repos = [repo for repo in await mstore.list_databases() if repo.name == repo_name]
            if len(repos) != 1:
                raise ValueError(f"Error creating repository `{name}`.")
            repo = repos[0]

            cstore = await self._init_chunkstore(repo.id, repo.bucket, org, repo_name)

            arepo = repo_v1.AsyncRepo(repo_model, cstore, name, author)
            await arepo.checkout()
            return arepo

        elif kind == RepoKind.V2:
            if not isinstance(repo_model.bucket, BucketResponse):
                raise ValueError("The bucket on the catalog object must be a BucketResponse for Icechunk V2 repos!")
            credentials = await self._maybe_get_credentials_for_icechunk(bucket=repo_model.bucket, org=org, repo_name=repo_name)
            return await icechunk_repo_from_repo_model(repo_model=repo_model, prefix=prefix, s3_credentials=credentials)

    async def delete_repo(self, name: str, *, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a repo

        Args:
            name: Full name of the repo to delete (of the form [ORG]/[REPO])
            imsure, imreallysure: confirm you intend to delete this bucket config
        """

        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)
        await mstore.delete_database(repo_name, imsure=imsure, imreallysure=imreallysure)

    async def _bucket_id_for_nickname(self, mstore: HttpMetastore, nickname: str) -> UUID:
        buckets = await mstore.list_bucket_configs()
        bucket_id = next((b.id for b in buckets if b.nickname == nickname), None)
        if not bucket_id:
            raise BucketNotFoundError(nickname)
        return bucket_id

    def _make_bucket_config(self, *, nickname: str, uri: str, extra_config: dict | None, auth_config: dict | None) -> dict:
        if not nickname:
            raise ValueError("nickname must be specified if uri is provided.")

        # unpack optionals
        if extra_config is None:
            extra_config = {}
        if auth_config is None:
            auth_config = {"method": "anonymous"}

        # parse uri and get prefix
        res = urlparse(uri)
        platform: Literal["s3", "gs", "s3-compatible"] | None = "s3" if res.scheme == "s3" else "gs" if res.scheme == "gs" else None
        if platform == "s3" and extra_config.get("endpoint_url"):
            platform = "s3-compatible"
        if platform not in ["s3", "gs", "s3-compatible"]:
            raise ValueError(f"Invalid platform {platform} for uri {uri}")
        name = res.netloc
        prefix = res.path[1:] if res.path.startswith("/") else res.path  # is an empty string if not specified

        if "method" not in auth_config or auth_config["method"] not in ["customer_managed_role", "anonymous", "hmac"]:
            raise ValueError("invalid auth_config, must provide method key of customer_managed_role, anonymous, or HMAC")

        return dict(
            platform=platform,
            name=name,
            prefix=prefix,
            nickname=nickname,
            extra_config=extra_config,
            auth_config=auth_config,
        )

    async def create_bucket_config(
        self, *, org: str, nickname: str, uri: str, extra_config: dict | None = None, auth_config: dict | None = None
    ) -> BucketResponse:
        """Create a new bucket config entry

        NOTE: This does not create any actual buckets in the object store.

        Args:
            org: Name of the org
            nickname: bucket nickname (example: ours3-bucket`)
            uri: The URI of the object store, of the form
                platform://bucket_name[/prefix].
            extra_config: dictionary of additional config to set on bucket config
            auth_config: dictionary of auth parameters, must include "method" key, default is `{"method": "anonymous"}`
        """
        validated = NewBucket(**self._make_bucket_config(nickname=nickname, uri=uri, extra_config=extra_config, auth_config=auth_config))
        mstore = self._metastore_for_org(org)
        bucket = await mstore.create_bucket_config(validated)
        return bucket

    async def set_default_bucket_config(self, *, org: str, nickname: str) -> None:
        """Set the organization's default bucket for any new repos

        Args:
            nickname: Nickname of the bucket config to set as default.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        await mstore.set_default_bucket_config(bucket_id)

    async def get_bucket_config(self, *, org: str, nickname: str) -> BucketResponse:
        """Get a bucket's configuration

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to retrieve.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        bucket = await mstore.get_bucket_config(bucket_id)
        return bucket

    async def list_bucket_configs(self, org: str) -> list[BucketResponse]:
        """List all bucket config entries

        Args:
            org: Name of the organization.
        """
        mstore = self._metastore_for_org(org)
        return await mstore.list_bucket_configs()

    async def list_repos_for_bucket_config(self, *, org: str, nickname: str) -> list[RepoModel]:
        """List repos using a given bucket

        Args:
            org: Name of the org
            nickname: Nickname of the bucket configuration.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        buckets = await mstore.list_repos_for_bucket_config(bucket_id)
        return buckets

    async def delete_bucket_config(self, *, org: str, nickname: str, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a bucket config entry

        NOTE: If a bucket config is in use by one or more repos, it cannot be
        deleted. This does not actually delete any buckets in the object store.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to delete.
            imsure, imreallysure: confirm you intend to delete this bucket config
        """
        if not (imsure and imreallysure):
            raise ValueError("imsure and imreallysure must be set to True")
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        await mstore.delete_bucket_config(bucket_id)

    async def login(self, *, browser: bool = False) -> None:
        """Login to ArrayLake

        Args:
            org: Name of the org (only required if your default organization uses SSO)
            browser: if True, open the browser to the login page
        """
        handler = get_auth_handler()
        await handler.login(browser=browser)

    async def logout(self) -> None:
        """Log out of ArrayLake

        Args:
            org: Name of the org (only required if your default organization uses SSO)
            browser: if True, open the browser to the logout page
        """
        handler = get_auth_handler()
        await handler.logout()

    async def get_api_client_id_from_token(self, org: str, token: str) -> str:
        """Fetch the user ID corresponding to the provided token"""
        mstore = self._metastore_for_org(org)
        user_id = await mstore.get_api_client_id_from_token(token)
        return user_id

    async def get_permission_check(self, org: str, principal_id: str, resource: str, action: OrgActions | RepoActions) -> bool:
        """Verify whether the provided principal has permission to perform the
        action against the resource"""
        mstore = self._metastore_for_org(org)
        is_approved = await mstore.get_permission_check(principal_id, resource, action)
        return is_approved


@dataclass
class Client:
    """Client for interacting with ArrayLake.

    Args:
        service_uri (str): [Optional] The service URI to target.
        token (str): [Optional] API token for service account authentication.
    """

    service_uri: Optional[str] = None
    token: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        if self.token is None:
            self.token = config.get("token", None)
        if self.service_uri is None:
            self.service_uri = config.get("service.uri")

        self.aclient = AsyncClient(self.service_uri, token=self.token)

    def list_repos(self, org: str) -> Sequence[RepoModel]:
        """List all repositories for the specified org

        Args:
            org: Name of the org
        """

        repo_list = sync(self.aclient.list_repos, org)
        return repo_list

    def get_repo(self, name: str, *, checkout: Optional[bool] = None, read_only: bool = False) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Get a repo by name

        Args:
            name:
                Full name of the repo (of the form [ORG]/[REPO])
            checkout:
                Automatically checkout the repo after instantiation.
                Ignored if specified for a Icechunk repo.
            read_only:
                Open the repo in read-only mode.
        """

        arepo = sync(self.aclient.get_repo, name, checkout=checkout, read_only=read_only)
        # We don't have access to the repo kind and we must be environment agnostic
        try:
            from icechunk import Repository as IcechunkRepository

            if isinstance(arepo, IcechunkRepository):
                return arepo
            else:
                raise ValueError("Output repo is not an IcechunkRepository, but icechunk is in the environment!")
        except ImportError:
            return arepo.to_sync_repo()

    def get_or_create_repo(
        self,
        name: str,
        *,
        checkout: Optional[bool] = None,
        bucket_config_nickname: Optional[str] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
    ) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Get a repo by name. Create the repo if it doesn't already exist.

        Args:
            name:
                Full name of the repo (of the form [ORG]/[REPO])
            checkout:
                Whether to checkout the repo after instantiation.
                If the repo does not exist, checkout is ignored.
                Ignored if specified for a Icechunk repo.
            bucket_config_nickname:
                The created repo will use this bucket for its chunks.
                If the repo exists, bucket_config_nickname is ignored.
            kind:
                The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix:
                Optional prefix for Icechunk store. Only used for Icechunk repos.
                If not provided, the repo ID will be used.
        """
        arepo = sync(
            self.aclient.get_or_create_repo,
            name,
            bucket_config_nickname=bucket_config_nickname,
            checkout=checkout,
            kind=kind,
            prefix=prefix,
        )
        # We don't have access to the repo kind and we must be environment agnostic
        try:
            from icechunk import Repository as IcechunkRepository

            if isinstance(arepo, IcechunkRepository):
                return arepo
            else:
                raise ValueError("Output repo is not an IcechunkRepository, but icechunk is in the environment!")
        except ImportError:
            return arepo.to_sync_repo()

    def create_repo(
        self,
        name: str,
        *,
        bucket_config_nickname: Optional[str] = None,
        kind: Optional[RepoKind] = None,
    ) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Create a new repo

        Args:
            name: Full name of the repo to create (of the form [ORG]/[REPO])
            bucket_config_nickname: An optional bucket to use for the chunkstore
            kind: the kind of repo to create (`v1` or `icechunk`)
        """

        arepo = sync(self.aclient.create_repo, name, bucket_config_nickname=bucket_config_nickname, kind=kind)
        if kind == RepoKind.V2:
            return arepo
        return arepo.to_sync_repo()

    def delete_repo(self, name: str, *, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a repo

        Args:
            name: Full name of the repo to delete (of the form [ORG]/[REPO])
        """

        return sync(self.aclient.delete_repo, name, imsure=imsure, imreallysure=imreallysure)

    def create_bucket_config(
        self, *, org: str, nickname: str, uri: str, extra_config: dict | None = None, auth_config: dict | None = None
    ) -> BucketResponse:
        """Create a new bucket config entry

        NOTE: This does not create any actual buckets in the object store.

        Args:
            org: Name of the org
            nickname: bucket nickname (example: our-s3-bucket)
            uri: The URI of the object store, of the form
                platform://bucket_name[/prefix].
            extra_config: dictionary of additional config to set on bucket config
            auth_config: dictionary of auth parameters, must include "method" key, default is `{"method": "anonymous"}`
        """
        return sync(
            self.aclient.create_bucket_config, org=org, nickname=nickname, uri=uri, extra_config=extra_config, auth_config=auth_config
        )

    def set_default_bucket_config(self, *, org: str, nickname: str) -> None:
        """Set the organization's default bucket config for any new repos

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to set as default.
        """
        return sync(self.aclient.set_default_bucket_config, org=org, nickname=nickname)

    def get_bucket_config(self, *, org: str, nickname: str) -> BucketResponse:
        """Get a bucket's configuration

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to retrieve.
        """
        return sync(self.aclient.get_bucket_config, org=org, nickname=nickname)

    def list_bucket_configs(self, org: str) -> list[BucketResponse]:
        """List all buckets for the specified org

        Args:
            org: Name of the org
        """
        return sync(self.aclient.list_bucket_configs, org)

    def list_repos_for_bucket_config(self, *, org: str, nickname: str) -> list[repo_v1.Repo | IcechunkRepository]:  # noqa
        """List repos using a given bucket config

        Args:
            org: Name of the org
            nickname: Nickname of the bucket.
        """
        return sync(self.aclient.list_repos_for_bucket_config, org=org, nickname=nickname)

    def delete_bucket_config(self, *, org: str, nickname: str, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a bucket config entry

        NOTE: If a bucket config is in use by one or more repos, it cannot be
        deleted. This does not actually delete any buckets in the object store.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to delete.
            imsure, imreallysure: confirm you intend to delete this bucket config
        """
        return sync(self.aclient.delete_bucket_config, org=org, nickname=nickname, imsure=imsure, imreallysure=imreallysure)

    def login(self, *, browser: bool = False) -> None:
        """Login to ArrayLake

        Args:
            org: Name of the org (only required if your default organization uses SSO)
            browser: if True, open the browser to the login page
        """
        return sync(self.aclient.login, browser=browser)

    def logout(self) -> None:
        """Log out of ArrayLake

        Args:
            org: Name of the org (only required if your default organization uses SSO)
            browser: if True, open the browser to the logout page
        """
        return sync(self.aclient.logout)

    def get_services(self, org: str) -> ComputeClient:
        """Get the compute client services for the given org.

        Args:
            org: Name of the org
        """
        return AsyncComputeClient(service_uri=self.aclient.service_uri, token=self.aclient.token, org=org).to_sync_client()

from __future__ import annotations

import importlib
from enum import Enum

from arraylake.log_util import get_logger
from arraylake.types import BucketResponse, LegacyBucketResponse
from arraylake.types import Repo as RepoModel
from arraylake.types import S3Credentials

logger = get_logger(__name__)

###
# TODO:
# Store the prefix in the metastore alongside the ID
###

ICECHUNK_REQUIRED_ENV_VARS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]


class CredentialType(Enum):
    ANONYMOUS = "anonymous"
    ENV = "env"
    PROVIDED = "provided"


def _raise_if_no_icechunk():
    """Check if icechunk is available in the environment and raise an error if it is not.

    Icechunk is required to interact with a V2 repo.
    """
    if not importlib.util.find_spec("icechunk"):
        raise ImportError("Icechunk not found in the environment! Icechunk repos are not supported.")


def _get_credential_type(credentials: S3Credentials | None) -> CredentialType:
    """Determines the credential type based on the given credentials.

    Args:
        credentials: Optional S3Credentials for data access

    Returns:
        CredentialType enum
    """
    if credentials is not None:
        return CredentialType.PROVIDED
    else:
        return CredentialType.ENV


def _get_icechunk_storage_obj(
    repo_id: str,
    bucket_config: BucketResponse,
    prefix: str | None = None,
    credential_type: CredentialType = CredentialType.ANONYMOUS,
    s3_credentials: S3Credentials | None = None,
):  # Removed output type so icechunk import is not required
    """Gets the Icechunk storage object.

    For S3 buckets, if S3 credentials are given, gets the Icechunk
    storage object from these creds. Otherwise, gets the storage
    object by looking in the environment for credentials.

    Args:
        repo_id: Repo ID to use as the storage config prefix
        bucket_config: BucketResponse object containing the bucket nickname
        prefix:
            Optional prefix to use in the Icechunk storage config.
            If not provided, the repo ID will be used.
        credential_type: The type of credentials to use for the storage config
        s3_credentials: Optional S3Credentials for data access

    Returns:
        Icechunk Storage object
    """
    # Check if icechunk is in the environment before proceeding
    _raise_if_no_icechunk()
    import icechunk

    prefix = prefix or str(repo_id)
    logger.debug(f"Using bucket {bucket_config.name} and prefix {prefix} for Icechunk storage config")

    # Check the if the bucket is an S3 or S3-compatible bucket
    if bucket_config.platform in ("s3", "s3c", "minio"):
        # Extract the endpoint URL from the bucket config, if it exists
        endpoint_url = bucket_config.extra_config.get("endpoint_url")
        if endpoint_url is not None:
            endpoint_url = str(endpoint_url)  # mypy thinks the endpoint_url could be a bool
        region = bucket_config.extra_config.get("region_name")
        if region is not None:
            region = str(region)  # mypy thinks the region could be a bool
        # Extract the use_ssl flag from the bucket config, if it exists
        use_ssl = bucket_config.extra_config.get("use_ssl", True)  # TODO: what should be the default?
        # Use s3_storage to create the storage object for s3 or s3-compatible buckets
        return icechunk.s3_storage(
            bucket=bucket_config.name,
            prefix=prefix,
            region=region,
            endpoint_url=endpoint_url,
            allow_http=not use_ssl,
            access_key_id=s3_credentials.aws_access_key_id if s3_credentials else None,
            secret_access_key=s3_credentials.aws_secret_access_key if s3_credentials else None,
            session_token=s3_credentials.aws_session_token if s3_credentials else None,
            expires_after=s3_credentials.expiration if s3_credentials else None,
            anonymous=credential_type == CredentialType.ANONYMOUS,
            from_env=credential_type == CredentialType.ENV,
            get_credentials=None,  # TODO: this will be implemented in a future PR
        )
    # Otherwise, check if the bucket is a GCS bucket
    elif bucket_config.platform in ("gs"):
        # Use gcs_storage to create the storage object for GCS buckets
        # We only support self-managed credentials for GCS buckets
        return icechunk.gcs_storage(
            bucket=bucket_config.name,
            prefix=prefix,
            service_account_file=None,
            service_account_key=None,
            application_credentials=None,
            from_env=credential_type == CredentialType.ENV,
            config=None,
        )
    else:
        raise ValueError(f"Unsupported bucket platform: {bucket_config.platform}")


async def icechunk_repo_from_repo_model(
    repo_model: RepoModel,
    prefix: str | None,
    credential_type: CredentialType | None = None,
    s3_credentials: S3Credentials | None = None,
):  # Removed output type so icechunk import is not required
    """Creates an Icechunk Repository object from the RepoModel.

    To do this, we build a Icechunk Storage object to get the Icechunk repo.

    Args:
        repo_model: Repo catalog object containing the repo name, ID, and bucket config
        prefix: Optional prefix for the storage config. If not provided, use repo UUID.
        credential_type: The type of credentials to use for the storage object
        s3_credentials: Optional S3Credentials to use for data access

    Returns:
        Icechunk Repository object
    """
    # Check if icechunk is in the environment before proceeding
    _raise_if_no_icechunk()
    from icechunk import Repository as IcechunkRepository

    # Ensure the bucket isn't None
    # TODO: remove when bucket becomes required
    if repo_model.bucket is None:
        raise ValueError("The bucket on the catalog object cannot be None for Icechunk V2 repos!")

    # mypy seems to think that the bucket could be a legacy bucket response
    if isinstance(repo_model.bucket, LegacyBucketResponse):
        raise ValueError("The bucket on the catalog object cannot be a LegacyBucketResponse for Icechunk V2 repos!")

    # Build the icechunk storage object
    credential_type = credential_type or _get_credential_type(s3_credentials)
    storage = _get_icechunk_storage_obj(
        repo_id=str(repo_model.id),
        bucket_config=repo_model.bucket,
        prefix=prefix,
        credential_type=credential_type,
        s3_credentials=s3_credentials,
    )

    # TODO: this may cause a race condition in a distributed environment
    return IcechunkRepository.open_or_create(
        storage=storage,
        config=None,  # Use the default repository config for now
        virtual_chunk_credentials=None,  # TODO: implement this in a future PR: EAR-1456
    )

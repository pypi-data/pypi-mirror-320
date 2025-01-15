import datetime
from uuid import uuid4

import icechunk
import pytest

from arraylake.client import AsyncClient
from arraylake.repos.icechunk.utils import (
    ICECHUNK_REQUIRED_ENV_VARS,
    CredentialType,
    _get_icechunk_storage_obj,
    icechunk_repo_from_repo_model,
)
from arraylake.types import DBID, BucketResponse, LegacyBucketResponse
from arraylake.types import Repo as RepoModel
from arraylake.types import (
    RepoOperationMode,
    RepoOperationStatusResponse,
    S3Credentials,
)

repo_id = DBID(b"some_repo_id")


@pytest.fixture
def s3_bucket_config() -> BucketResponse:
    return BucketResponse(
        id=uuid4(),
        platform="s3",
        nickname="test-s3-bucket-nickname",
        name="s3-test",
        is_default=False,
        extra_config={
            "use_ssl": True,
            "endpoint_url": "http://foo.com",
            "region_name": "us-west-1",
        },
    )


@pytest.fixture
def gcs_bucket_config() -> BucketResponse:
    return BucketResponse(
        id=uuid4(),
        platform="gcs",
        nickname="test-gcs-bucket-nickname",
        name="gcs-test",
        is_default=False,
        extra_config={},
    )


def test_get_icechunk_storage_s3_credentials(
    s3_bucket_config: BucketResponse,
):
    creds = S3Credentials(
        aws_access_key_id="aws_access_key_id",
        aws_secret_access_key="aws_secret_access_key",
        aws_session_token="aws_session_token",
        expiration=None,
    )
    storage = _get_icechunk_storage_obj(
        repo_id=repo_id, bucket_config=s3_bucket_config, prefix=None, s3_credentials=creds, credential_type=CredentialType.PROVIDED
    )
    assert isinstance(storage, icechunk.Storage)


def test_get_icechunk_storage_obj_from_env(s3_bucket_config: BucketResponse, monkeypatch):
    for var in ICECHUNK_REQUIRED_ENV_VARS:
        monkeypatch.setenv(var, "test")

    storage = _get_icechunk_storage_obj(
        repo_id=repo_id, bucket_config=s3_bucket_config, prefix=None, s3_credentials=None, credential_type=CredentialType.ENV
    )
    assert isinstance(storage, icechunk.Storage)

    # Remove environment variables
    for var in ICECHUNK_REQUIRED_ENV_VARS:
        monkeypatch.delenv(var)


@pytest.mark.asyncio
async def test_get_icechunk_storage_from_repo_model_minio_from_env(isolated_org_with_bucket, token, monkeypatch):
    """Tests that the environment variables are used on the backend in icechunk for minio test setup"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "minio123")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "minio123")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_bucket
    bucket_config = await aclient.get_bucket_config(org=org, nickname=bucket_nickname)

    repo_model = RepoModel(
        _id=repo_id,
        org="earthmover",
        name="repo-name",
        updated=datetime.datetime.now(),
        status=RepoOperationStatusResponse(mode=RepoOperationMode.ONLINE, initiated_by={}),
        bucket=bucket_config,
    )
    await icechunk_repo_from_repo_model(repo_model=repo_model, prefix=None)

    # Remove environment variables
    monkeypatch.delenv("AWS_ACCESS_KEY_ID")
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY")
    monkeypatch.delenv("AWS_REGION")


@pytest.mark.asyncio
async def test_icechunk_store_from_repo_model_no_bucket_raises():
    with pytest.raises(ValueError) as excinfo:
        await icechunk_repo_from_repo_model(
            repo_model=RepoModel(
                _id=repo_id,
                org="earthmover",
                name="repo-name",
                updated=datetime.datetime.now(),
                status=RepoOperationStatusResponse(mode=RepoOperationMode.ONLINE, initiated_by={}),
                bucket=None,
            ),
            prefix=None,
        )
    assert "The bucket on the catalog object cannot be None for Icechunk V2 repos!" in str(excinfo.value)


@pytest.mark.asyncio
async def test_icechunk_repo_from_repo_model_legacy_bucket_raises():
    with pytest.raises(ValueError) as excinfo:
        await icechunk_repo_from_repo_model(
            repo_model=RepoModel(
                _id=repo_id,
                org="earthmover",
                name="repo-name",
                updated=datetime.datetime.now(),
                status=RepoOperationStatusResponse(mode=RepoOperationMode.ONLINE, initiated_by={}),
                bucket=LegacyBucketResponse(
                    id=uuid4(),
                    name="bucket-name",
                    platform="s3",
                    nickname="bucket-nickname",
                    updated=datetime.datetime.now(),
                    extra_config={},
                    auth_method="auth",
                    is_default=False,
                ),
            ),
            prefix=None,
        )
    assert "The bucket on the catalog object cannot be a LegacyBucketResponse for Icechunk V2 repos!" in str(excinfo.value)

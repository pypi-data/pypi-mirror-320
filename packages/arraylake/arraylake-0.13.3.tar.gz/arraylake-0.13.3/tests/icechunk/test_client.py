import json

import pytest
from httpx import Response
from icechunk import Repository

from arraylake import AsyncClient, Client
from arraylake.types import RepoKind, RepoOperationMode


@pytest.mark.asyncio
async def test_async_client(isolated_org_with_bucket, token):
    """Integration-style test for the async client."""
    org_name, _ = isolated_org_with_bucket

    aclient = AsyncClient(token=token)
    assert not await aclient.list_repos(org_name)

    # Create two new Icechunk repos
    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        repo = await aclient.create_repo(name, kind=RepoKind.V2)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

        repo = await aclient.get_repo(name)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

    # Check that duplicate repos are not allowed
    with pytest.raises(ValueError):
        await aclient.create_repo(name, kind=RepoKind.V2)

    # List the repos
    repo_listing = await aclient.list_repos(org_name)
    all_repo_names = {repo.name for repo in repo_listing}
    assert all_repo_names == {"foo", "bar"}

    # Delete the repos
    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        await aclient.delete_repo(name, imsure=True, imreallysure=True)

    # Check that the repos are gone
    with pytest.raises(ValueError):
        # can't get nonexistent repo
        await aclient.get_repo("doesnt/exist")

    with pytest.raises(ValueError):
        # can't delete nonexistent repo
        await aclient.delete_repo("doesnt/exist", imsure=True, imreallysure=True)


def test_client(isolated_org_with_bucket, token):
    """Integration-style test for the sync client."""
    org_name, _ = isolated_org_with_bucket

    client = Client(token=token)
    assert client.list_repos(org_name) == []

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        repo = client.create_repo(name, kind=RepoKind.V2)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

        repo = client.get_repo(name)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

    with pytest.raises(ValueError):
        # no duplicate repos allowed
        client.create_repo(name, kind=RepoKind.V2)

    repo_listing = client.list_repos(org_name)
    assert len(repo_listing) == 2
    all_repo_names = {repo.name for repo in repo_listing}
    assert all_repo_names == {"foo", "bar"}

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        client.delete_repo(name, imsure=True, imreallysure=True)

    with pytest.raises(ValueError):
        # can't get nonexistent repo
        client.get_repo("doesnt/exist")

    with pytest.raises(ValueError):
        # can't delete nonexistent repo
        client.delete_repo("doesnt/exist", imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_get_or_create_repo_async(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    aclient = AsyncClient(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in await aclient.list_repos(org_name)}
    # Create the repo
    await aclient.get_or_create_repo(name, kind=RepoKind.V2)
    assert repo_name in {repo.name for repo in await aclient.list_repos(org_name)}
    # Get the repo
    await aclient.get_or_create_repo(name, kind=RepoKind.V2)
    # TODO: earth-mover/icechunk#414: expose storage config so we can check more things
    # Delete the repo
    await aclient.delete_repo(name, imsure=True, imreallysure=True)


def test_get_or_create_repo_sync(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    client = Client(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
    # Create the repo
    client.get_or_create_repo(name, kind=RepoKind.V2)
    assert repo_name in {repo.name for repo in client.list_repos(org_name)}
    # Get the repo
    client.get_or_create_repo(name, kind=RepoKind.V1)
    # TODO: earth-mover/icechunk#414: expose storage config so we can check more things
    # Delete the repo
    client.delete_repo(name, imsure=True, imreallysure=True)


async def test_db_not_called_on_create_with_v1_repo(test_user, respx_mock):
    api_url = "https://foo.com"
    org = "test-org"
    repo_name = "foo"

    repo = dict(
        id="1234",
        org=org,
        name=repo_name,
        created=str(1234567890),
        description="",
        status=dict(mode="online", initiated_by={"system_id": "x"}),
        kind=RepoKind.V1,
    )

    aclient = AsyncClient(service_uri=api_url)
    get_db_route = respx_mock.request("GET", api_url + f"/repos/{org}/{repo_name}").mock(return_value=Response(200, json=repo))
    create_db_route = respx_mock.request("POST", api_url + f"/orgs/{org}/repos").mock(return_value=Response(200, json=repo))
    respx_mock.request("GET", api_url + "/user").mock(return_value=Response(200, json=json.loads(test_user.model_dump_json())))
    respx_mock.request("GET", api_url + f"/orgs/{org}/repos").mock(return_value=Response(200, json=[repo]))

    with pytest.raises(ImportError, match="Legacy Arraylake Repos"):
        await aclient.create_repo(f"{org}/foo", kind=RepoKind.V1)
    assert not get_db_route.called
    assert not create_db_route.called


@pytest.mark.asyncio
@pytest.mark.xfail(reason="status endpoint is currently admin only", raises=ValueError)
async def test_repo_status_changes(isolated_org_with_bucket, token, helpers):
    aclient = AsyncClient(token=token)
    org_name, _ = isolated_org_with_bucket
    _repo_name = helpers.random_repo_id()
    repo_name = f"{org_name}/{_repo_name}"
    await aclient.create_repo(repo_name, kind=RepoKind.V2)

    # assert repo is initialized with the right status
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.ONLINE
    assert repo_obj.status.message == "new repo creation"
    assert repo_obj.status.initiated_by.get("principal_id") is not None
    assert repo_obj.status.initiated_by.get("system_id") is None

    # assert update operates correctly
    await aclient._set_repo_status(repo_name, RepoOperationMode.OFFLINE, message="foo")
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.OFFLINE
    assert repo_obj.status.message == "foo"
    assert repo_obj.status.initiated_by.get("principal_id") is not None

    # assert system update is visible
    _on, _rn = repo_name.split("/")
    await helpers.set_repo_system_status(token, _on, _rn, RepoOperationMode.MAINTENANCE, "system message", False)
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.MAINTENANCE
    assert repo_obj.status.message == "system message"
    assert repo_obj.status.initiated_by.get("principal_id") is None
    assert repo_obj.status.initiated_by.get("system_id") is not None

    # is_user_modifiable is false, verify request is blocked
    with pytest.raises(ValueError, match="Repo status is not modifiable") as exc_info:
        await aclient._set_repo_status(repo_name, RepoOperationMode.ONLINE, message="foo")

    # and state is still what it was prior to the attempt
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.MAINTENANCE
    assert repo_obj.status.message == "system message"
    assert repo_obj.status.initiated_by.get("principal_id") is None

    await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_repo_with_inconsistent_bucket(isolated_org_with_bucket, token, helpers) -> None:
    aclient = AsyncClient(token=token)
    org_name, _ = isolated_org_with_bucket
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    await aclient.create_repo(repo_name, kind=RepoKind.V2)
    try:
        with pytest.raises(ValueError, match=r"does not match the configured bucket_config_nickname") as exc_info:
            await aclient.get_or_create_repo(repo_name, bucket_config_nickname="bad-nickname")
    finally:
        await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)

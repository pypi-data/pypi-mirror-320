from __future__ import annotations

import asyncio
import os
import shutil
import time
from pathlib import Path

import httpx
import pymongo
import pytest
import pytest_asyncio
from linkml_runtime.dumpers import json_dumper

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf
from omero_quay.core.connect import irods_sudo_conn
from omero_quay.core.workers import setup
from omero_quay.managers.irods import put_directory
from omero_quay.parsers.filesystem import gen_manifest

pytestmark = pytest.mark.asyncio(scope="module")

conf = get_conf()
DATA_PATH = conf["pytest"]["DOCKER_DATA_PATH"]


@pytest.fixture(scope="session")
def base_import(conf, xlsx_irods_path):
    manifest_id = asyncio.run(excel_request(xlsx_irods_path, conf))
    mongo_client = pymongo.MongoClient(
        conf["mongo"]["DB_URL"], conf["mongo"]["DB_PORT"]
    )
    manifests = mongo_client.quay.manifests
    waited = 0
    with mongo_client:
        while waited < 1800:
            time.sleep(30)
            waited += 30
            man = manifests.find_one(
                {"_id": manifest_id}, projection=["error", "states"]
            )
            if not man:
                continue
            if msg := man["error"] is not None:
                raise OSError(msg)
            for state in man["states"]:
                if state["status"] == "errored":
                    msg = f"Import failed for f{state['scheme']}"
                    raise ValueError(msg)
                if (state["scheme"] == "omero") and (state["status"] == "checked"):
                    return
    raise TimeoutError


@pytest.fixture(scope="session")
def conf():
    if "QUAY_CONF" not in os.environ:
        os.environ["QUAY_CONF"] = (
            (Path.cwd() / "tests/containers/quay_tester.yml").resolve().as_posix()
        )
    return get_conf()


@pytest.fixture(scope="session")
def data_path():
    path = Path(DATA_PATH).resolve()
    if not path.exists():
        path.mkdir(parents=True)
    return path.as_posix()


@pytest.fixture(scope="session")
def ingest_mount_path(data_path, conf):
    path = Path(conf["ingest"]["MOUNT_PATH"]) / Path(data_path).name
    if not path.exists():
        path.mkdir(parents=True)
    if Path(data_path) != path:
        shutil.copytree(data_path, path, dirs_exist_ok=True)
    return path


@pytest.fixture(scope="session")
def transient_mount_path(data_path, ingest_mount_path):
    if Path(data_path) != ingest_mount_path:
        shutil.copytree(data_path, ingest_mount_path, dirs_exist_ok=True)
    return ingest_mount_path
    # shutil.rmtree(ingest_mount_path)


@pytest.fixture(scope="session")
def irods_user_path(ingest_mount_path, conf):
    test_user = "facility0"
    local_path = ingest_mount_path
    logical_path = f"/{conf['irods']['IRODS_ZONE']}/home/{test_user}"
    # irods_col_path = (Path(logical_path) / local_path.name).as_posix()
    with irods_sudo_conn(conf, test_user) as sess:
        try:
            put_directory(
                local_path=local_path, logical_path=logical_path, session=sess
            )
        except KeyError:
            print("Put directory failed")
        yield logical_path
        # collection = sess.collections.get(irods_col_path)
        # collection.remove(recurse=True, force=True)


@pytest.fixture
def omero_share_path(conf):
    path = conf["omero"]["OMERO_SHARE_PATH"]
    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def yaml_manifest(transient_mount_path):
    return (Path(transient_mount_path) / "manifests" / "base_manifest.yml").as_posix()


@pytest.fixture
def yaml_manifest_2(transient_mount_path):
    return (Path(transient_mount_path) / "manifests" / "base_manifest_2.yml").as_posix()


@pytest.fixture
def users_manifest(transient_mount_path):
    return (Path(transient_mount_path) / "users" / "test_users.yml").as_posix()


@pytest.fixture
def test_users_json(transient_mount_path):
    return (Path(transient_mount_path) / "users" / "test_users.json").as_posix()


@pytest.fixture(scope="session")
def xlsx_irods_path(irods_user_path, transient_mount_path):  # noqa:ARG001
    return (Path(transient_mount_path) / "test_ingest_import.xlsx").as_posix()


@pytest.fixture
def xlsx_import_path(transient_mount_path):
    return (Path(transient_mount_path) / "test_ingest_import.xlsx").as_posix()


@pytest.fixture
def irods_manifest(irods_user_path):
    source = (Path(irods_user_path) / "data").as_posix()
    owner = "facility0"
    return gen_manifest(
        source,
        depth=1,
        hierarchy={"investigation": "test_inv", "study": "test_stu"},
        owner_name=owner,
        scheme="irods",
    )


@pytest.fixture
def fs_manifest(transient_mount_path):
    source = (Path(transient_mount_path) / "dir0").as_posix()
    owner = "facility0"
    return gen_manifest(
        source,
        depth=2,
        hierarchy={"investigation": "test_inv"},
        owner_name=owner,
        scheme="file",
    )


@pytest_asyncio.fixture()
async def fs_service(conf):
    conf["workers"]["watchers"] = {}
    conf["workers"]["managers"] = {
        "file": {
            "in_port": 5555,
            "out_port": 5554,
        }
    }
    try:
        await setup(conf)
    except KeyboardInterrupt:
        print("interrupted")
        return


@pytest_asyncio.fixture()
async def request_client(fs_manifest, conf):
    print("started request client")
    await asyncio.sleep(3)
    post_url = conf["ingest"]["POST_URL"]
    manifest_json = json_dumper.dumps(fs_manifest)

    async with httpx.AsyncClient() as client:
        print("Sending post request")
        await client.post(f"{post_url}", data=manifest_json, timeout=5)


@pytest_asyncio.fixture()
async def excel_client(excel_import_path, conf):
    conf["workers"]["watchers"] = {}
    conf["workers"]["managers"] = {
        "file": {
            "in_port": 5555,
            "out_port": 5554,
        }
    }
    try:
        await excel_request(excel_import_path, conf)
    except KeyboardInterrupt:
        print("interrupted")
        return

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid1

from ..core.config import get_conf
from ..core.manifest import Assay, DataLink, Investigation, Manifest, State, Study, User


def gen_manifest(srce_path, depth=0, hierarchy=None, owner_name=None, scheme="irods"):
    """
    depth 0: assay
    depth 1: study
    depth 2: investigation

    """

    if hierarchy is None:
        hierarchy = {}
    conf = get_conf()
    srce_dir = Path(srce_path)
    conf["SRCE_DIR"] = srce_dir.as_posix()
    manifest = Manifest(id=f"man_{uuid1()}")
    link = DataLink(
        id=f"lnk_{uuid1()}", owner=owner_name, srce_url=f"{scheme}://{srce_path}"
    )

    manager = User(
        id="usr_{uuid1()}",
        name=owner_name,
        role="manager",
        first_name=owner_name,
        last_name=owner_name,
        email="test@example.org",
    )

    match depth:
        case 0:
            if not {"investigation", "study", "assay"}.issubset(hierarchy):
                msg = """
You need to provide investigation, study and assay names in the `hierarchy`
 argument to import data at the assay level
                        """
                raise ValueError(msg)

            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
            )
            investigation.members = [manager]

            manifest.investigations.append(investigation)
            study = Study(
                id=f"stu_{uuid1()}",
                name=hierarchy["study"],
                owner=owner_name,
                parents=[investigation.id],
            )
            manifest.studies.append(study)
            assay = Assay(
                id=f"ass_{uuid1()}",
                name=hierarchy["assay"],
                owner=owner_name,
                parents=[study.id],
                importlink=link,
            )
            manifest.assays.append(assay)

        case 1:
            if "investigation" not in hierarchy:
                msg = """You need to provide
investigation and study  names in the `hierarchy` argument
to import data at the study level"""
                raise ValueError(msg)

            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
            )
            investigation.members = [manager]
            manifest.investigations.append(investigation)
            study = Study(
                id=f"stu_{uuid1()}",
                name=hierarchy["study"],
                owner=owner_name,
                parents=[investigation.id],
                importlink=link,
            )
            manifest.studies.append(study)
        case 2:
            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
                importlink=link,
            )
            investigation.members = [manager]
            manifest.investigations.append(investigation)
    now = datetime.now().isoformat()
    state = State(timestamp=now, host="localhost", scheme="file", status="started")
    manifest.states = [state]
    return manifest

"""
iRODS file operations

"""

from __future__ import annotations

import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid1

from ..core.manifest import Assay, Collection, Investigation, Manifest, Study
from ..core.utils import find_by_id, get_path
from .manager import Manager

log = logging.getLogger(__name__)


class FSManager(Manager):
    """Parses manifest in a file system

    example:

    .. code-block:: [python]

        dry_run = False
        ...
        with FSManager(manifest) as fsmngr:
            fsmngr.parse_manifest()
            # check every thing is ok
            print(fsmngr)
            if not dry_run:
                fsmngr.transfer()
    """

    scheme = "file"
    host = "localhost"

    def __init__(self, manifest: Manifest, conf: dict, host="localhost"):
        """

        required conf entries:

        conf['file']['SRCE_DIR'] # base directory at the source
        conf['file']['DEST_DIR'] # base directory at the destination
        """
        super().__init__(manifest, conf["file"], host=host)
        self.destinations = defaultdict(dict)

    def transfer(self):
        """
        Creates ISA collections (& group if there are new investigations) from self.new_isaobjects

        Moves data_objects from source to destination as mapped in
        `self.destinations`
        """
        log.info("in manager transfer")
        for _, destinations in self.destinations.items():
            for srce, dest in destinations.items():
                self.__move__(srce, dest)
                log.debug("moved %s to %s", srce, dest)

    @staticmethod
    def __move__(srce, dest):
        shutil.copy(srce, dest)

    def _delete(self, isaobject):
        if localobject := self._exists(isaobject):
            if localobject.is_dir():
                shutil.rmtree(localobject)
            else:
                localobject.unlink()

    def _update(self, isaobject):
        """Do nothing"""

    def _find_by_path(self, isaobject):
        path = Path(get_path(isaobject, "file"))
        if path.exists():
            return path
        return False

    def _find_by_id(self, isaobject):  # noqa:ARG002
        return False

    def _find_by_foreing_ids(self, isaobject):  # noqa:ARG002
        return False

    def _create(self, isaobject):
        if isinstance(isaobject, Collection):
            path = get_path(isaobject, "file")
            Path(path).mkdir(mode=0o744, parents=True, exist_ok=True)

    def _import_from(self, isaobject):
        link_path = Path(urlparse(isaobject.importlink.srce_url).path)
        if not link_path.exists():
            log.warning("%s not found", link_path)
            return

        if isinstance(isaobject, Investigation):
            self._prepare_investigation(isaobject)

        elif isinstance(isaobject, Study):
            self._prepare_study(isaobject)

        elif isinstance(isaobject, Assay):
            self._prepare_assay(isaobject)

    def _prepare_investigation(self, investigation):
        """This creates a new investigation, which means a directory"""
        link_path = Path(urlparse(investigation.importlink.srce_url).path)
        owner = investigation.importlink.owner

        dest = Path(self.conf["DEST_DIR"]).resolve()
        inv_path = (dest / investigation.name).resolve().as_posix()
        investigation.urls.append(f"file://{inv_path}")
        investigation.importlink.trgt_url = f"file://{inv_path}"
        orph = Path(inv_path) / "orphaned"
        orph.mkdir(mode=0o744, parents=True, exist_ok=True)
        self.destinations[investigation.owner].update(
            {do: (dest / orph).as_posix() for do in link_path.glob("*") if do.is_file()}
        )

        for stu_path in link_path.iterdir():
            dest = (Path(inv_path) / stu_path.name).as_posix()
            study = Study(
                id=f"stu_{uuid1()}",
                owner=owner,
                name=stu_path.name,
                parents=[investigation.id],
                urls=[f"file://{dest}"],
            )
            investigation.children.append(study.id)
            self.manifest.studies.append(study)
            self._walk_study(study, link_path)

    def _prepare_study(self, study):
        """
        Creates the study collection in iRODS and moves the content pointed
        of importlink there. All subdirectories will be imported as new assays
        with a flattened name"""

        link_path = Path(urlparse(study.importlink.srce_url).path)
        inv_id = study.parents[-1]
        investigation = find_by_id(inv_id, self.manifest.investigations)
        inv_path = get_path(investigation, "file")
        stu_path = (inv_path / study.name).resolve().as_posix()
        study.urls.append(f"file://{stu_path}")
        study.importlink.trgt_url = f"file://{stu_path}"
        self._walk_study(study, link_path)

    def _prepare_assay(self, assay):
        """Creates the assay collection in iRODS and moves the content pointed
        of importlink there.

        Suibdirectories are ignored
        """
        link_path = Path(urlparse(assay.importlink.srce_url).path)
        owner = assay.importlink.owner

        dest = Path(self.conf["DEST_DIR"]).resolve()
        stu_id = assay.parents[-1]
        study = find_by_id(stu_id, self.manifest.investigations)
        stu_path = get_path(study, "file")
        if stu_path is None:
            inv_id = study.parents[-1]
            investigation = find_by_id(inv_id, self.manifest.investigations)
            inv_path = get_path(investigation, "file")
            if inv_path is None:
                inv_path = dest / investigation.name
            stu_path = (inv_path / study.name).resolve()

        ass_path = (stu_path / assay.name).resolve()
        assay.urls.append(f"file://{ass_path.as_posix()}")
        assay.importlink.trgt_url = f"file://{ass_path}"
        files = [f for f in link_path.glob("*") if not f.is_dir()]
        self.destinations[owner].update(
            {
                (Path(link_path).resolve() / f).as_posix(): ass_path.as_posix()
                for f in files
            }
        )

    def prepare_datalink(self, datalink):
        """Moves a single file or the files in the directory to the assay

        Sub-directories are ignored, destination must already exist
        """
        raise NotImplementedError

    def _walk_study(self, study, path):
        stu_path = get_path(study, "file")
        for subdir, _, files in os.walk(path):
            rel_path = "_".join(Path(subdir).relative_to(path).parts)
            if not rel_path:  # orphaned data at study root
                rel_path = "orphaned"

            abs_path = Path(stu_path) / rel_path
            abs_path.mkdir(mode=0o744, parents=True, exist_ok=True)

            assay = Assay(
                id=f"ass_{uuid1()}",
                owner=study.owner,
                name=rel_path,
                parents=[study.id],
                urls=[f"file://{abs_path}"],
            )
            study.children.append(assay.id)
            self.destinations[study.owner].update(
                {
                    (Path(subdir).resolve() / f).as_posix(): abs_path.as_posix()
                    for f in files
                }
            )

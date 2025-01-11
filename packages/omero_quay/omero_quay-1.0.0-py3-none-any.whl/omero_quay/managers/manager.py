"""
Abstract class for manager
"""

from __future__ import annotations

import logging

from ..core.interface import Interface
from ..core.manifest import Manifest

log = logging.getLogger(__name__)


class Manager(Interface):
    """Abstract manager

    Managers parse a manifest and perform actions on a
    spectific system or between systems
    """

    def __init__(
        self,
        conf: dict,
        manifest: Manifest,
        scheme: str,
        host: str,
    ):
        """

        required conf entries:

        conf["YAML_STORE"] # Path to store the manifest's yml dumps
        """

        self.created_isaobjects = []
        self.updated_isaobjects = []
        self.deleted_isaobjects = []
        super().__init__(conf=conf, manifest=manifest, scheme=scheme, host=host)
        self.manifest = manifest
        self.mapping = {}

    def parse(self, parse_links=True):
        """Prepare data links and isa objects"""
        self.created_isaobjects = []
        self.updated_isaobjects = []
        self.deleted_isaobjects = []
        if parse_links:
            for isaobject in self.isaobjects:
                if isaobject.importlink is not None:
                    # this will add isaobjects
                    log.info("Importing from %s", isaobject.importlink.srce_url)
                    self._import_from(isaobject)
        for isaobject in self.isaobjects:
            self._prepare(isaobject)

        delete_str = "\n\t- ".join([o.name for o in self.deleted_isaobjects])
        create_str = "\n\t- ".join([o.name for o in self.created_isaobjects])
        update_str = "\n\t- ".join([o.name for o in self.updated_isaobjects])

        log.info(
            """
    * Objects marked for deletion:
        - %s
    * Objects marked for creation:
        - %s
    * Objects marked for update:
        - %s  """,
            delete_str,
            create_str,
            update_str,
        )

    def crud(self):
        """
        Updates the local hierarchy from the created, updated and deleted
        isaobjects
        """
        if self.state.status == "checked":
            return

        for isaobject in self.created_isaobjects:
            self._create(isaobject)

        for isaobject in self.updated_isaobjects:
            self._update(isaobject)

        for isaobject in self.deleted_isaobjects:
            self._delete(isaobject)

        self.set_state("changed")

    def cleanup(self):
        pass

    def transfer(self):
        raise NotImplementedError

    def annotate(self):
        raise NotImplementedError

    def _import_from(self, isaobject):
        raise NotImplementedError

    def _prepare(self, isaobject):
        if localobject := self._exists(isaobject):
            self.mapping[isaobject.id] = localobject
            if isaobject.delete:
                self.deleted_isaobjects.append(isaobject)
            else:
                self.updated_isaobjects.append(isaobject)
        else:
            self.created_isaobjects.append(isaobject)

    def _exists(self, isaobject):
        if localobject := self.mapping.get(isaobject.id):
            return localobject
        if (
            (localobject := self._find_by_id(isaobject))
            or (localobject := self._find_by_path(isaobject))
            or (localobject := self._find_by_foreign_ids(isaobject))
        ):
            self.mapping[isaobject.id] = localobject
            return localobject

        return False

    def _find_by_id(self, isaobject):
        raise NotImplementedError

    def _find_by_path(self, isaobject):
        raise NotImplementedError

    def _find_by_foreign_ids(self, isaobject):
        raise NotImplementedError

    def _create(self, isaobject):
        raise NotImplementedError

    def _delete(self, isaobject):
        """
        Deletes data
        """
        raise NotImplementedError

    def _update(self, isaobject):
        """
        Updates data based on the manifest
        """
        raise NotImplementedError

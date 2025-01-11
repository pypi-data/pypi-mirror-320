from __future__ import annotations

import logging
import os
import traceback
from datetime import datetime
from itertools import product
from pathlib import Path
from uuid import uuid1

import pymongo
from linkml_runtime.dumpers import yaml_dumper

from .manifest import Assay, Error, Investigation, Manifest, State, Study
from .utils import find_by_id

log = logging.getLogger(__name__)

HOME = Path(os.environ["HOME"])


log_path = HOME / "log" / "omero_quay"

log_path.mkdir(parents=True, exist_ok=True)


class Interface:
    """Base class to interact with a manifest object"""

    def __init__(
        self,
        conf: dict,
        manifest: Manifest | None = None,
        scheme: str | None = None,
        host: str | None = None,
    ):
        log.info("using interface sub class %s", self.__class__.__name__)
        if manifest is None:
            self.manifest = Manifest(id=f"man_{uuid1()}")
            self.manager = None
            log.info("Interface %s created an empty manifest", self.__class__.__name__)
        else:
            self.manifest = manifest
            if manifest.manager:
                self.manager = manifest.manager
            else:
                manager_ = next(
                    iter(
                        filter(
                            lambda m: m.role == "manager",
                            self.manifest.investigations[0].members,
                        )
                    )
                )
                self.manager = manager_.name
                self.manifest.manager = self.manager

        self.log = logging.getLogger(self.manifest.id)
        self.log.setLevel("DEBUG")
        log_file = log_path / f"{self.manifest.id}.log"
        if not log_file.exists():
            handler = logging.FileHandler(log_file)
            handler.setLevel("DEBUG")
            self.log.addHandler(handler)

        if "mongo" in conf:
            self.has_db = True
            self.mongo_client = pymongo.MongoClient(
                conf["mongo"]["DB_URL"], conf["mongo"]["DB_PORT"]
            )
            try:
                self.mongo_client.server_info()
            except pymongo.errors.ServerSelectionTimeoutError:
                self.log.error(
                    "Failed to connect to mongo DB with configuration %s", conf["mongo"]
                )
                self.has_db = False

        else:
            self.has_db = False

        if self.has_db:
            self.mongo_db = self.mongo_client.quay
            self.manifests = self.mongo_db.manifests
            self.store()

        self.conf = conf
        self.scheme = scheme
        self.host = host
        self.set_state(None)

    def set_state(self, status):
        """Set state of an item. Permissible values values for status:

        - started
        - changed
        - checked
        - expired
        - errored

        Args:
            status (str): The status of the item.
        """
        now = datetime.now().isoformat()
        for state in self.manifest.states[::-1]:
            if (state.host == self.host) and (state.scheme == self.scheme):
                self.log.info(
                    "Matched state with host %s and scheme %s with manager %s",
                    state.host,
                    state.scheme,
                    self.__class__.__name__,
                )
                if status is not None:
                    state.status = status
                state.timestamp = now
                self.state = state
                break
        else:
            self.log.info(
                "No state found for manager %s with host %s and scheme %s",
                self.__class__.__name__,
                self.host,
                self.scheme,
            )
            self.log.info(
                "available states : %s",
                "\n".join(
                    f"host: {s.host}, scheme: {s.scheme}, status, {s.status}"
                    for s in self.manifest.states[::-1]
                ),
            )
            self.state = State(
                timestamp=now, scheme=self.scheme, status=status, host=self.host
            )
            self.manifest.states.append(self.state)

        if self.has_db:
            self.manifests.update_one(
                {"_id": self.manifest.id},
                {"$set": {"states": [s.dict() for s in self.manifest.states]}},
            )

        self.log.info(
            "manager %s state set to %s", self.__class__.__name__, self.state.status
        )

    def set_other_states(self, status, schemes):
        for state, scheme in product(self.manifest.states[::-1], schemes):
            now = datetime.now().isoformat()

            if str(state.scheme) == scheme:
                self.log.info("setting status %s for scheme %s", status, scheme)
                new_state = State(
                    timestamp=now, scheme=scheme, status=status, host=state.host
                )
                new_state.status = status
                self.manifest.states.remove(state)
                self.manifest.states.append(new_state)

        if self.has_db:
            self.manifests.update_one(
                {"_id": self.manifest.id},
                {"$set": {"states": [s.dict() for s in self.manifest.states]}},
            )

    def __enter__(self):
        log.info("Started interface instance %s", self.__class__.__name__)
        self.set_state("started")
        now = datetime.now().isoformat()
        self.manifest.creation_date = now
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # don't store empty manifests
        if not self.manifest.investigations:
            self.mongo_client.close()
            return
        if exc_type:
            self.log.error("Exception: ", exc_info=(exc_type, exc_value, tb))
            trace = traceback.format_exception(exc_type, exc_value, tb)
            self.manifest.error = Error(message=str(exc_value), details="".join(trace))
            self.set_state("errored")

        self.store()
        self.mongo_client.close()
        log.info("Exiting %s", self)

    def __str__(self):
        n_inv = len(self.manifest.investigations)
        n_stu = len(self.manifest.studies)
        n_ass = len(self.manifest.assays)
        n_img = len(self.manifest.images)
        n_ann = len(self.manifest.quay_annotations)
        return f"""---
         {self.__class__.__name__} managing manifest {self.manifest.id} with

         - {n_inv} investigation{'s' if n_inv > 1 else ''}
         - {n_stu} stud{'ies' if n_stu > 1 else 'y'}
         - {n_ass} assay{'s' if n_ass > 1 else ''}
         - {n_img} image{'s' if n_img > 1 else ''}
         - {n_ann} annotation{'s' if n_ann > 1 else ''}

        Current status:  {self.state.status}
         """

    def store(self):
        if self.has_db:
            result = self.manifests.update_one(
                {"_id": self.manifest.id}, {"$set": self.manifest.dict()}, upsert=True
            )
            if result.matched_count:
                self.log.debug("Updated manifest %s in DB", self.manifest.id)
            else:
                self.log.debug("Inserted new manifest %s in DB", self.manifest.id)
        else:
            now = datetime.now().isoformat()
            fname = f"{now}_{self.manifest.id}.yml"
            store = Path(self.conf.get("YAML_STORE", "/tmp/"))
            if not store.exists():
                store.mkdir(parents=True)
            with (store / fname).open("w") as yh:
                yml = yaml_dumper.dumps(self.manifest)
                yh.write(yml)

    @property
    def isaobjects(self):
        return (
            self.manifest.investigations + self.manifest.studies + self.manifest.assays
        )

    def parse(self):
        raise NotImplementedError

    def get_parent_investigation(self, isaobject):
        if isinstance(isaobject, Investigation):
            return isaobject
        if isinstance(isaobject, Study):
            parent = find_by_id(isaobject.parents[-1], self.manifest.investigations)
        elif isinstance(isaobject, Assay):
            parent = find_by_id(isaobject.parents[-1], self.manifest.studies)
        return self.get_parent_investigation(parent)

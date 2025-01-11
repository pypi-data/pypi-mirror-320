"""
iRODS file operations

"""

from __future__ import annotations

import logging
import os
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid1

import irods.keywords as kw
from irods.access import iRODSAccess
from irods.column import Criterion
from irods.exception import (
    CAT_NO_ACCESS_PERMISSION,
    CAT_SQL_ERR,
    UNIX_FILE_CREATE_ERR,
    UNIX_FILE_OPEN_ERR,
    GroupDoesNotExist,
)
from irods.models import Collection as RCollection
from irods.models import CollectionMeta, DataObjectMeta
from irods.models import DataObject as RDataObject
from jinja2 import Template

from ..core.connect import irods_conn, irods_sudo_conn
from ..core.manifest import Assay, Collection, File, Investigation, Manifest, Study
from ..core.utils import find_by_id, get_identifiers, get_path
from .manager import Manager

log = logging.getLogger(__name__)
log.setLevel("INFO")


class iRODSManager(Manager):
    """Parses manifest in iRODS
    example:

    .. code-block:: [python]

        dry_run = False
        ...
        with iRODSManager(manifest) as rodsmngr:
            rodsmngr.parse()
            # check every thing is ok
            print(rodsmngr)
            if not dry_run:
                rodsmngr.transfer()
    """

    def __init__(self, conf: dict, manifest: Manifest):
        """

        required conf entries

        conf["irods"]['IRODS_HOST']
        conf["irods"]['IRODS_PORT']
        conf["irods"]['IRODS_ADMIN_USER']
        conf["irods"]['IRODS_ZONE']
        conf["irods"]['IRODS_ADMIN_PASS']

        """
        super().__init__(
            conf,
            manifest,
            scheme="irods",
            host=conf["workers"]["managers"]["irods"]["host"],
        )
        self.session = None
        self.destinations = defaultdict(dict)
        self.log.info("Treating manifest with manager %s", self.manager)

    def __enter__(self):
        super().__enter__()
        self.session = irods_conn(self.conf)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        self.session.__exit__(exc_type, exc_value, traceback)

    def transfer(self):
        """
        Moves data_objects from source to destination as mapped in
        `self.destinations`
        """

        for _, destinations in self.destinations.items():
            with irods_sudo_conn(self.conf, self.manager) as sess:
                for srce, dest in destinations.items():
                    if not sess.collections.exists(dest):
                        self.log.warning(
                            "Collection %s does not exist. Collections should not be"
                            " created during transfer",
                            dest,
                        )
                        sess.collections.create(dest)

                    if sess.collections.exists(srce):
                        # srce is a collection
                        continue

                    do = sess.data_objects.get(srce)

                    if sess.data_objects.exists(f"{dest}/{do.name}"):
                        self.log.info(
                            "file %s already exists, can't move %s there",
                            f"{dest}/{do.name}",
                            srce,
                        )
                        continue
                    sess.data_objects.copy(srce, dest)
                    # Note: Inherit must be set on the source collection to
                    # also respect inheritance on the target

    def annotate(self):
        raise NotImplementedError

    def _delete(self, isaobject):
        if localobject := self._exists(isaobject):
            if isinstance(isaobject, Collection):
                self.session.collections.remove(localobject.path, recurse=True)
            elif isinstance(isaobject, File):
                self.session.data_objects.unlink(localobject.path)
        else:
            self.log.info("Object %s marked for deletion not found", isaobject.name)

    def _update(self, isaobject):
        localobject = self._exists(isaobject)
        if not localobject:
            msg = (
                f"Object {isaobject.name} of type "
                " {type(isaobject)} has no mapping in irods"
            )
            raise ValueError(msg)

        if isaobject.irods_id != localobject.id:
            self.log.debug(
                "updating Id discrepancy between %s %s and iRODS %s %s",
                isaobject.__class__.__name__,
                isaobject.name,
                localobject.__class__.__name__,
                localobject.name,
            )

        if localobject.path != get_path(isaobject, "irods"):
            self.log.info(
                "Planning to move %s from %s to %s",
                localobject.name,
                localobject.path,
                get_path(isaobject, "irods"),
            )
            self.destinations[isaobject.owner][localobject.path] = get_path(
                isaobject, "irods"
            )

        self._set_ids_metadata(isaobject, localobject)

    def _set_ids_metadata(self, isaobject, localobject):
        self.log.info("Updating irods id for %s", isaobject.name)
        isaobject.irods_id = localobject.id
        for key, val in get_identifiers(isaobject).items():
            if key in localobject.metadata.keys():  # noqa:SIM118
                old = localobject.metadata.get_all(key)[-1]
                if old.value != str(val):
                    self.log.info("Updating %s for object %s", key, isaobject.name)
                    localobject.metadata.set(key, str(val))
            else:
                localobject.metadata.add(key, str(val))
                self.log.info("Setting %s for object %s", key, isaobject.name)

    def _find_by_path(self, isaobject):
        path = get_path(isaobject, "irods")
        if path is None:
            return False
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session

        if isinstance(isaobject, Collection):
            if session.collections.exists(path):
                return session.collections.get(path)

            return False

        if isinstance(isaobject, File):
            if session.data_objects.exists(path):
                return session.data_objects.get(path)
            return False

        msg = (
            "Only objects inheritating from File or Collection can be searched by path"
        )
        raise ValueError(msg)

    def _find_by_id(self, isaobject):
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session

        if isaobject.irods_id is None:
            return False

        if isinstance(isaobject, Collection):
            results = (
                session.query(RCollection.name)
                .filter(Criterion("=", RCollection.id, isaobject.irods_id))
                .all()
            )
            if results:
                (name,) = results[0].values()
                return session.collections.get(name)
            return False

        if isinstance(isaobject, File):
            results = (
                session.query(RDataObject.path)
                .filter(Criterion("=", RDataObject.id, isaobject.irods_id))
                .all()
            )
            if results:
                (name,) = results[0].values()
                return session.data_objects.get(name)
            return False

        msg = "Only objects inheritating from File or Collection can be searched"
        raise ValueError(msg)

    def _find_by_foreign_ids(self, isaobject):
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session
        ids = get_identifiers(isaobject)

        if isinstance(isaobject, Collection):
            for key, value in ids.items():
                results = (
                    session.query(RCollection.name)
                    .filter(Criterion("=", CollectionMeta.name, key))
                    .filter(Criterion("=", CollectionMeta.value, value))
                ).all()
                if results:
                    (path,) = results[0].values()
                    self.log.info("Found object %s by it's key %s", isaobject.name, key)
                    return session.collections.get(path)
            return False

        if isinstance(isaobject, File):
            for key, value in ids.items():
                results = (
                    self.session.query(RDataObject.path)
                    .filter(Criterion("=", DataObjectMeta.name, key))
                    .filter(Criterion("=", DataObjectMeta.value, value))
                ).all()
                if results:
                    (path,) = results[0].values()
                    return self.session.data_objects.get(path)
            return False

        msg = "Only objects inheritating from File or Collection can be searched"
        raise ValueError(msg)

    def _create(self, isaobject):
        if isinstance(isaobject, Investigation):
            self._create_investigation(isaobject)
        elif isinstance(isaobject, Collection):
            self._create_coll(isaobject)

    def _create_investigation(self, investigation: Investigation):
        """Creates the iRODS group, sets members"""

        owners = {m.name for m in investigation.members if m.role == "owner"}
        try:
            group = self.session.groups.get(investigation.name)
            irods_members = {m.name: m for m in group.members}
            if common := owners.intersection(irods_members):
                self.log.debug(
                    "The investigation %s already exists,"
                    " and users %s are already members"
                    " we will append studies to it ",
                    investigation.name,
                    common,
                )
            else:
                err_msg = (
                    f"The investigation {investigation.name} already exists,"
                    f" and no one from investigation owners ({', '.join(owners)}) is a member, aborting"
                )
                self.log.error(err_msg)
                raise ValueError(err_msg)

        except GroupDoesNotExist:
            self.log.info(
                "Creating investigation group %s in irods", investigation.name
            )
            group = self.session.groups.create(investigation.name)

        self._set_ids_metadata(investigation, group)
        irods_members = {m.name: m for m in group.members}
        group_coll = get_path(investigation, "irods")

        if self.manager not in irods_members:
            group.addmember(self.manager)

        for member in investigation.members:
            if member.name not in irods_members:
                group.addmember(member.name)
                irods_members = {m.name: m for m in group.members}

            match member.role:
                case "owner":
                    self.log.info("Adding %s as owner of %s", member.name, group_coll)
                    acl = iRODSAccess(
                        "own", group_coll, member.name, user_type="rodsuser"
                    )
                case "manager":
                    self.log.info("Adding %s as manager of %s", member.name, group_coll)
                    acl = iRODSAccess(
                        "delete_object",
                        group_coll,
                        member.name,
                        user_type="rodsuser",
                    )
                case "contributor":
                    self.log.info(
                        "Adding %s as contributor of %s", member.name, group_coll
                    )
                    acl = iRODSAccess(
                        "write", group_coll, member.name, user_type="rodsuser"
                    )
                case "collaborator":
                    self.log.info(
                        "Adding %s as collaborator of %s", member.name, group_coll
                    )
                    acl = iRODSAccess(
                        "read", group_coll, member.name, user_type="rodsuser"
                    )
            with irods_sudo_conn(self.conf, self.manager) as sess:
                sess.acls.set(acl)

        inh_acl = iRODSAccess("inherit", group_coll)
        with irods_sudo_conn(self.conf, self.manager) as sess:
            sess.acls.set(inh_acl)

        group = self.session.groups.get(investigation.name)
        admin = self.conf["irods"]["IRODS_ADMIN_USER"]
        if admin not in {m.name for m in group.members}:
            group.addmember(admin)
        admin_acl = iRODSAccess(
            "delete_object", group_coll, admin, user_type="rodsadmin"
        )
        with irods_sudo_conn(self.conf, self.manager) as sess:
            self.log.info("Setting admin as group owner")
            sess.acls.set(admin_acl)

        self.log.info("Investigation %s created", investigation.name)

    def _create_coll(self, isaobject):
        """Creates the collection in iRODS and sets acls"""
        with irods_sudo_conn(self.conf, self.manager) as sess:
            path = get_path(isaobject, "irods")
            if path is None:
                msg = f"""
                       No irods path found for {isaobject.name},
                       Available urls: {isaobject.urls}
                       """
                self.log.error(msg)
                raise ValueError(msg)
            has_coll = sess.collections.exists(path)

            if has_coll:
                coll = sess.collections.get(path)
                if not _check_acl(isaobject.owner, self.session, coll):
                    err_msg = f"The isaobject {isaobject.name} already exists, user {isaobject.owner} can't modify it"
                    raise ValueError(err_msg)

                self.log.info(
                    "collection %s already exists, user %s can modify it",
                    isaobject.name,
                    isaobject.owner,
                )
            else:
                try:
                    coll = sess.collections.create(path)
                except CAT_SQL_ERR as e:
                    self.log.error("error creating collection at %s", path, exc_info=e)
                    raise e

            self._set_ids_metadata(isaobject, coll)

            acl = iRODSAccess("own", coll.path, isaobject.owner, user_type="rodsuser")
            sess.acls.set(acl)
            inh_acl = iRODSAccess("inherit", coll.path)
            sess.acls.set(inh_acl)

    def _import_from(self, isaobject):
        """

        Parses a collection recursively into an ISA hierarchy of objects.

        The collection (I, S or A) containing an importlink is imported from the
        `isaobject.importlink.srce_url`

            study.importlink.srce_url = smb:///127.0.0.3/espace_perso/data_to_import

        The collection hierarchy is collabsed in 3 levels.

        see doc/tree.svg
        If the isaobect is a Study ...

        **TODO** complete doc
        """
        link = urlparse(isaobject.importlink.srce_url)
        user = isaobject.importlink.owner
        if link.scheme == "smb":
            # register
            for resc in self.conf["irods"]["resources"].values():
                smb_path = Template(link.path).render(user=user)
                smb_root = resc["smb_root"]
                if smb_path.startswith(smb_root):
                    unix_root = Template(resc["unix_root"]).render(user=user)
                    irods_root = Template(resc["irods_root"]).render(user=user)
                unix_path = smb_path.replace(smb_root, unix_root)
                irods_path = smb_path.replace(smb_root, irods_root)
                resc_name = resc["resc"]
                self.log.info(
                    "Found mapping: smb_root: %s, unix_root: %s, irods_root: %s",
                    smb_root,
                    unix_root,
                    irods_root,
                )
                break
            else:
                msg = f"""Template for link path mappings not found.
                       link path: {link.path}, available resources: {self.conf['irods']['resources']} """
                raise ValueError(msg)

            with irods_sudo_conn(self.conf, user) as sess:
                irods_parent = Path(irods_path).parent.as_posix()
                if not sess.collections.exists(irods_parent):
                    coll = sess.collections.create(irods_parent, recurse=True)
                    self.log.info("Created %s", coll)
                else:
                    coll = sess.collections.get(irods_parent)
                try:
                    inherit = iRODSAccess("inherit", coll)
                    sess.acls.set(inherit)
                    acl = iRODSAccess("own", coll, user, user_type="rodsuser")
                    sess.acls.set(acl)
                    admin = self.conf["irods"]["IRODS_ADMIN_USER"]
                    acl = iRODSAccess("own", coll, admin, user_type="rodsadmin")
                    sess.acls.set(acl)
                except TypeError:
                    self.log.info("Error when trying to set acl for user %s", user)
                except CAT_NO_ACCESS_PERMISSION:
                    self.log.error(
                        "WARNING: Could not set acl for collection %s", irods_parent
                    )
            with irods_conn(self.conf) as sess:
                self.log.info(
                    "resgistering %s to %s on resc %s", unix_path, irods_path, resc_name
                )
                options = {
                    kw.RESC_NAME_KW: resc_name,
                    kw.RECURSIVE_OPR__KW: "recursiveOpr",
                    kw.FORCE_FLAG_KW: "forceFlag",  # force update #
                }
                try:
                    sess.collections.register(unix_path, irods_path, **options)
                except UNIX_FILE_CREATE_ERR as e:
                    self.log.error(
                        "WARNING: Error register Path : %s in collection %s",
                        unix_path,
                        irods_path,
                    )
                    msg = f"There was an issue in {Path(unix_path).relative_to(unix_root)} in {isaobject.name}."
                    raise OSError(msg) from e

            isaobject.importlink.srce_url = f"irods://{irods_path}"
            old_link = link
            link = urlparse(isaobject.importlink.srce_url)
            self.log.info(
                "import link path was %s, is now %s ", old_link.path, link.path
            )

        with irods_sudo_conn(self.conf, isaobject.importlink.owner) as sess:
            if not sess.collections.exists(link.path):
                self.log.error(
                    "%s not found by %s", link.path, isaobject.importlink.owner
                )
                return

        if isinstance(isaobject, Investigation):
            self._prepare_investigation(isaobject)

        elif isinstance(isaobject, Study):
            self._prepare_study(isaobject)

        elif isinstance(isaobject, Assay):
            self._prepare_assay(isaobject)

    def _prepare_investigation(self, investigation):
        link_path = urlparse(investigation.importlink.srce_url).path
        with irods_sudo_conn(self.conf, investigation.importlink.owner) as sess:
            to_import = sess.collections.get(link_path)

        investigation.owner = investigation.importlink.owner

        zone = self.conf["irods"]["IRODS_ZONE"]
        inv_path = f"/{zone}/home/{investigation.name}"

        investigation.urls.append(f"irods://{inv_path}")
        investigation.importlink.trgt_url = f"irods://{inv_path}"
        # 1st level data objects are moved to investigation root
        # (images will be orphaned in omero)
        dest = f"{inv_path}/orphaned"

        self.destinations[investigation.owner].update(
            {do.path: dest for do in to_import.data_objects}
        )

        for coll in to_import.subcollections:
            # 1st level
            dest = f"{inv_path}/{coll.name}"

            study = Study(
                id=f"stu_{uuid1()}",
                owner=investigation.owner,
                name=coll.name,
                parents=[investigation.id],
                urls=[f"irods://{dest}"],
            )
            investigation.children.append(study.id)
            self.manifest.studies.append(study)
            self._walk_study(study, coll)

    def _prepare_study(self, study):
        """
        Creates the study collection in iRODS and moves the content pointed
        by importlink there. All subdirectories will be imported as new assays
        with a flattened name
        """
        link_path = urlparse(study.importlink.srce_url).path
        to_import = self.session.collections.get(link_path)
        # study.owner = importlink.owner
        inv_id = study.parents[-1]
        investigation = find_by_id(inv_id, self.manifest.investigations)
        zone = self.conf["irods"]["IRODS_ZONE"]
        inv_path = get_path(investigation, "irods")
        if inv_path is None:
            inv_path = f"/{zone}/home/{investigation.name}"
            investigation.urls.append(f"irods://{inv_path}")

        study.urls.append(f"irods://{inv_path}/{study.name}")
        study.importlink.trgt_url = f"irods://{inv_path}/{study.name}"

        self._walk_study(study, to_import)

    def _prepare_assay(self, assay):
        """Creates the assay collection in iRODS and moves the content pointed
        by importlink there.

        Subdirectories are suffixed to the file name
        """
        link_path = urlparse(assay.importlink.srce_url).path
        to_import = self.session.collections.get(link_path)
        stu_id = assay.parents[-1]
        study = find_by_id(stu_id, self.manifest.studies)
        stu_path = get_path(study, "irods")
        if stu_path is None:
            self.log.info(
                "Building path for study %s while perparing assay import", study.name
            )
            inv_id = study.parents[-1]
            investigation = find_by_id(inv_id, self.manifest.investigations)
            zone = self.conf["irods"]["IRODS_ZONE"]
            inv_path = get_path(investigation, "irods")
            if inv_path is None:
                inv_path = f"/{zone}/home/{investigation.name}"
                investigation.urls.append(f"irods://{inv_path}")
            stu_path = f"{inv_path}/{study.name}"
            study.urls.append(f"irods://{stu_path}")

        path = f"{stu_path}/{assay.name}"
        assay.urls.append(f"irods://{path}")
        assay.importlink.trgt_url = f"irods://{path}"
        # concatenate subdirectories and add to move list
        self._walk_assay(assay, to_import)

    def prepare_datalink(self, datalink):
        """Moves a single file or the files in the directory to the assay

        Sub-directories are ignored, destination must already exist
        """
        raise NotImplementedError

    def _walk_study(self, study, collection):
        for subcol, _, data_objects in collection.walk():
            rel_path = "_".join(Path(subcol.path).relative_to(collection.path).parts)
            if not rel_path:  # orphaned data at study root
                rel_path = "orphaned"

            study_path = get_path(study, "irods")
            abs_path = f"{study_path}/{rel_path}"

            assay = Assay(
                id=f"ass_{uuid1()}",
                owner=study.owner,
                name=rel_path,
                parents=[study.id],
                urls=[f"irods://{abs_path}"],
            )
            self.manifest.assays.append(assay)
            assay.parents.append(study.id)
            study.children.append(assay.id)
            self.destinations[study.owner].update(
                {do.path: abs_path for do in data_objects}
            )

    def _walk_assay(self, assay, collection):
        for subcol, _, data_objects in collection.walk():
            rel_path = "_".join(Path(subcol.path).relative_to(collection.path).parts)

            assay_path = get_path(assay, "irods")
            abs_path = f"{assay_path}/{rel_path}" if rel_path else assay_path
            self.destinations[assay.owner].update(
                {do.path: abs_path for do in data_objects}
            )


def _check_acl(user_name, session, col, minimal="modify_object"):
    acls = session.acls.get(col)
    min_val = iRODSAccess.to_int(minimal)
    for acl in acls:
        if acl.user_type == "rodsgroup":
            members = [m.name for m in session.groups.get(acl.user_name).members]
            if user_name in members:
                return iRODSAccess.to_int(acl.access_name) >= min_val
            return False
        if acl.user_name == user_name:
            return iRODSAccess.to_int(acl.access_name) >= min_val
    return False


def put_directory(local_path, logical_path, session):
    local_path = Path(local_path)

    for root, dirs, files in os.walk(local_path):
        rel_root = Path(root).relative_to(local_path)
        irods_col_path = (Path(logical_path) / local_path.name / rel_root).as_posix()
        if not session.collections.exists(irods_col_path):
            session.collections.create(irods_col_path)

        for local_file in files:
            local_file_path = (Path(root) / local_file).as_posix()
            irods_file_path = (Path(irods_col_path) / local_file).as_posix()
            try:
                session.data_objects.put(local_file_path, irods_file_path)
            except UNIX_FILE_OPEN_ERR:
                log.info("File %s is opened, skipping ", irods_file_path)
        for local_dir in dirs:
            irods_dir_path = (Path(irods_col_path) / local_dir).as_posix()
            if not session.collections.exists(irods_dir_path):
                session.collections.create(irods_dir_path)

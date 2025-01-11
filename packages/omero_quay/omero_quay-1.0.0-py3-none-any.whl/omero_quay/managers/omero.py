"""OMERO operations"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from random import randint
from uuid import uuid1
from xml.etree.ElementTree import ParseError

import ome_types.model as mod
from ezomero import post_map_annotation
from Ice import ObjectNotExistException
from ome_types import from_xml, to_xml
from ome_types.model.map import M, Map
from omero.gateway import TagAnnotationWrapper

# from omero import ApiUsageException
from ..core.connect import omero_admin_cli, omero_conn, omero_sudo_cli, omero_sudo_conn
from ..core.manifest import (
    Assay,
    Image,
    Investigation,
    Manifest,
    Study,
)
from ..core.utils import (
    expand_ids,
    find_by_id,
    find_by_name,
    get_class_mappings,
    get_depth,
    get_identifiers,
    get_path,
)
from .manager import Manager

log = logging.getLogger(__name__)

ann_map = {
    "file_annotation": mod.FileAnnotation,
    "tag_annotation": mod.TagAnnotation,
    "map_annotation": mod.MapAnnotation,
    "comment_annotation": mod.CommentAnnotation,
}


class OmeroManager(Manager):
    """
    This manager should not create objects in omero, this is deferred to omero transfer


    """

    def __init__(self, conf: dict, manifest: Manifest):
        super().__init__(
            conf,
            manifest,
            scheme="omero",
            host=conf["workers"]["managers"]["omero"]["host"],
        )
        self.omes = []
        self.ome_user = None
        self._conn = None
        self._type_mapping = get_class_mappings("ome")
        self.stale_annotations = []  # list of omero ids

        self.log.info("Treating manifest with manager %s", self.manager)

    def __enter__(self):
        super().__enter__()
        self._conn = omero_conn(self.conf)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.__exit__(exc_type, exc_value, traceback)
        self.log.info("Resetting irods state after leaving omero manager")
        super().__exit__(exc_type, exc_value, traceback)

    @property
    def conn(self):
        if not self._conn.isConnected():
            self._conn.connect()
        return self._conn

    def transfer(self):
        """
        Uses the (augmented) omes created by the `parse` method to import data in omero
        """
        log.info("OMEs: " + str(self.omes))
        for _, isaobject, ome, duplicates in self.omes:
            log.info("OME_Experimenter_Groups: " + str(ome.experimenter_groups))
            self._write_ome(isaobject, ome, out="ome.xml")
            ome_ = ome.copy()
            for image in duplicates:
                ome_.images.remove(image)
            self._write_transfer(isaobject, ome_)
            group_name = ome.experimenter_groups[0].name
            data_path = get_path(isaobject, "file")
            self.log.info(
                "Importing %s in omero from path %s for user %s",
                isaobject.name,
                data_path,
                isaobject.owner,
            )
            cli = omero_sudo_cli(
                self.conf,
                self.manager,
                opts=["--group", group_name],
            )
            data_path = get_path(isaobject, "file")
            self.log.info(
                "Importing %s in omero from path %s", isaobject.name, data_path
            )
            cli.invoke(
                [
                    "transfer",
                    "unpack",
                    "--merge",
                    "--ln_s_import",
                    "--folder",
                    data_path,
                ],
                strict=True,
            )
            self._update(isaobject)

        self.set_other_states("expired", ["irods"])

    def pack(self, isaobject):
        ome_id = isaobject.ome_id
        obj_t = self.type_mapping(isaobject)
        ome_object_str = f"{obj_t}:{ome_id}:"
        path = get_path(isaobject, "file")
        cli = omero_sudo_cli(self.conf, self.manager)
        cli.invoke(
            ["transfer", "pack", "--binaries", "none", ome_object_str, str(path)],
            strict=True,
        )
        (Path(path) / "transfer.xml").copy(Path(path) / "ome.xml")

        self.log.info("Resetting irods state from omero manager")
        isaobject.importlink = None
        self.set_other_states("expired", ["irods"])

    def type_mapping(self, isaobject):
        return self._type_mapping[isaobject.__class__.__name__]

    def cleanup(self):
        self.log.info("Cleaning up stale annotations %s", self.stale_annotations)
        self.stale_annotations = list(set(self.stale_annotations))
        if self.stale_annotations:
            self.log.info("Cleaning up annotations %s", self.stale_annotations)
            self.conn.deleteObjects("Annotation", self.stale_annotations, wait=True)

    def _import_from(self, isaobject):
        ome = self._get_ome(isaobject)
        depth = get_depth(isaobject)
        duplicates = self._parse_ome(depth, isaobject, ome)
        self.omes.append((depth, isaobject, ome, duplicates))

    def _get_ome(self, isaobject):
        user_name = self.manager
        self._set_ome_path(isaobject)
        path = get_path(isaobject, "file")
        if path is None:
            self.log.error("No file path found for %s", isaobject)
        self.log.info("Preparing data import from %s for user %s", path, user_name)
        try:
            ome_xml = Path(path) / "ome.xml"
            lock_file = Path(path) / "transfer.xml.lock"
        except TypeError as e:
            self.log.error("wrong path somehow, %s, urls: %s", path, isaobject.urls)
            raise e
        if lock_file.exists():
            msg = f"omero transfer prepare already processing {path}"
            self.log.info(msg)
            raise OSError(msg)
        if ome_xml.exists():
            if self.conf["omero"].get("USE_CACHE"):
                try:
                    self.log.info("Using cached ome.xml")
                    return from_xml(ome_xml)
                except ParseError:
                    self.log.info("Can't use cached ome.xml, looks corrupted")
            ome_xml.unlink()
        cli = omero_sudo_cli(self.conf, user_name)
        lock_file.touch()
        transfer_xml = Path(path) / "transfer.xml"
        if transfer_xml.exists():
            transfer_xml.unlink()
        try:
            cli.invoke(["transfer", "prepare", path], strict=True)
            (Path(path) / "transfer.xml").rename(ome_xml)
            return from_xml(ome_xml)
        except ParseError as e:
            # file gets corrupted some times
            ome_xml.unlink()
            raise e
        finally:
            lock_file.unlink()

    def _find_by_id(self, isaobject):
        otype = self.type_mapping(isaobject)
        if isaobject.ome_id is not None:
            obj = self.conn.getObject(otype, isaobject.ome_id)
            if obj:
                return obj
        return False

    def _find_by_path(self, isaobject):
        if isinstance(isaobject, Investigation):
            (ome_user,) = self.conn.getObjects(
                "experimenter", attributes={"omeName": isaobject.owner}
            )
            grps = {p.name: p for p in ome_user.listParents()}

            if isaobject.name in grps:
                self.log.info(
                    "Investigation %s already exists in omero", isaobject.name
                )
                return grps[isaobject.name]

        elif isinstance(isaobject, Study):
            investigation = find_by_id(
                isaobject.parents[-1], self.manifest.investigations
            )
            group = self._exists(investigation)
            if not group:
                self.log.info("Group %s not found", investigation.name)
                return False
            projects = self.conn.getObjects(
                "Project",
                opts={"group": group.id},
                attributes={"name": isaobject.name},
            )
            try:
                return next(iter(projects))
            except (ObjectNotExistException, StopIteration, ValueError):
                self.log.info("Project %s not found by name", isaobject.name)

        elif isinstance(isaobject, Assay):
            study = find_by_id(isaobject.parents[-1], self.manifest.studies)
            project = self._exists(study)

            if not project:
                self.log.info("Project %s not found", study.name)
                return False

            study.ome_id = project.getId()
            datasets = self.conn.getObjects(
                "Dataset",
                opts={"project": project.getId()},
                attributes={"name": isaobject.name},
            )
            try:
                return next(iter(datasets))
            except (ObjectNotExistException, StopIteration, ValueError):
                self.log.info("Dataset %s not found by name", isaobject.name)

        elif isinstance(isaobject, Image):
            assay = find_by_id(isaobject.parents[-1], self.manifest.assays)
            if dataset := self._exists(assay):
                existing = self.conn.getObjects(
                    "Image",
                    opts={
                        "dataset": dataset.id,
                    },
                    attributes={"name": isaobject.name},
                )
                try:
                    return next(iter(existing))
                except (ObjectNotExistException, ValueError, StopIteration):
                    self.log.info("Image %s not found by name", isaobject.name)

        return False

    def _find_by_foreign_ids(self, isaobject):
        otype = self.type_mapping(isaobject)
        ids = get_identifiers(isaobject)
        for key, value in ids.items():
            try:
                objects = self.conn.getObjectsByMapAnnotations(
                    otype, key=key, value=str(value), ns="quay"
                )
                obj = next(iter(objects))
            except (ObjectNotExistException, StopIteration, ValueError):
                continue
            self.log.info("Found object %s by it's key %s", isaobject.name, key)
            break
        else:
            obj = False
        return obj

    def _create(self, isaobject):
        self._set_ome_path(isaobject)
        if isinstance(isaobject, Investigation):
            self._create_investigation(isaobject)
        else:
            self.log.debug(
                (
                    "Object %s is not an investigation "
                    "object creation for other ISA levels should be left to "
                    "omero transfer"
                ),
                isaobject.name,
            )

    def _update(self, isaobject):
        self._set_ome_path(isaobject)
        localobject = self._exists(isaobject)
        if not localobject:
            self.log.info(
                "Object %s of type  %s has no mapping in omero",
                isaobject.name,
                type(isaobject),
            )
            return
        omero_id = localobject.getId()
        isaobject.ome_id = omero_id
        ids = get_identifiers(isaobject)
        otype = self.type_mapping(isaobject)
        if otype != "ExperimenterGroup":
            inv = self.get_parent_investigation(isaobject)
            with omero_sudo_conn(self.conf, isaobject.owner, inv.name) as conn:
                self.stale_annotations.extend(
                    post_unique_map_annotation(conn, otype, omero_id, ids, ns="quay")
                )
                self.stale_annotations.extend(deduplicate_tags(conn, otype, omero_id))
                self.log.info("Stale annotations: %s", self.stale_annotations)

        localobject.name = isaobject.name
        needs_update = False
        match self.type_mapping(isaobject):
            case "ExperimenterGroup":
                self._update_members(isaobject, localobject)

            case "Project":
                investigation = find_by_id(
                    isaobject.parents[-1], self.manifest.investigations
                )
                group = self._exists(investigation)
                if not group:
                    msg = f"Ancestor not found for {localobject.name}"
                    raise ValueError(msg)
                if group.id != localobject.details.group.id.val:
                    # new_id = localobject.details.group.id.val
                    # group_wrapper = self.conn.getObject("Project", new_id)
                    # localobject.details.group = group_wrapper
                    # needs_update = False
                    self.log.warning(
                        "Mismatch between Study parent investigation in omero %s and corresponding omero project's group %s",
                        group,
                        localobject.details.group,
                    )

            case "Dataset":
                study = find_by_id(isaobject.parents[-1], self.manifest.studies)
                project = self._exists(study)

                if not project:
                    msg = f"Ancestor not found for {localobject.name}"
                    raise ValueError(msg)

                # always update the last parent
                # for link in localobject.getParentLinks():
                #     self.log.info("Dataset %s has link to %s", localobject, link.parent)
                #     if project.id == link.parent.id:
                #         break
                # else:
                #     self.log.info("Changing parent of dataset %s", study.name)
                #     cli = omero_sudo_cli(self.conf, isaobject.owner)
                #     cli.invoke(
                #         [
                #             "obj",
                #             "new",
                #             "ProjectDatasetLink",
                #             f"parent=Project:{project.id}",
                #             f"child=Dataset:{localobject.id}",
                #         ]
                #     )

            case "Image":
                assay = find_by_id(isaobject.parents[-1], self.manifest.assays)
                dataset = self._exists(assay)

                if not dataset:
                    msg = f"Ancestor not found for {localobject.name}"
                    raise ValueError(msg)

                # always update the last parent
                for link in localobject.getparentLinks():
                    if dataset.id == link.parent.id:
                        break
                else:
                    self.log.info("Changing parent of dataset %s", assay.name)
                    cli = omero_sudo_cli(self.conf, self.manager)
                    cli.invoke(["delete", f"DatasetImageLink:{link.id}"])
                    cli.invoke(
                        [
                            "obj",
                            "new",
                            "DatasetImageLink",
                            f"parent=Dataset:{dataset.id}",
                            f"child=Image:{localobject.id}",
                        ]
                    )

            case "FileAnnotation":
                pass

        try:
            if needs_update:
                localobject.save()

        except AttributeError as e:
            self.log.error(
                "Error for local object %s from isaobject %s", localobject, isaobject
            )
            raise e

    def _delete(self, isaobject):
        if isaobject.id not in self.mapping:
            msg = f"object {isaobject.name} not found in mapping, can't delete"
            raise KeyError(msg)
        obj = self.mapping[isaobject.id]
        otype = obj.__class__.__name__

        self.conn.deleteObjects(
            otype,
            [obj],
            deleteAnns=False,
            deleteChildren=False,
            dryRun=False,
            wait=False,
        )

    def _set_ome_path(self, isaobject):
        if irods_path := get_path(isaobject, "irods"):
            path = (
                Path(self.conf["omero"]["OMERO_SHARE_PATH"])
                / Path(irods_path).relative_to(self.conf["omero"]["IRODS_SHARE_PATH"])
            ).as_posix()
            isaobject.urls.append(f"file://{path}")

    def _set_irods_path(self, isaobject):
        if file_path := get_path(isaobject, "file"):
            path = (
                Path(self.conf["omero"]["IRODS_SHARE_PATH"])
                / Path(file_path).relative_to(self.conf["omero"]["OMERO_SHARE_PATH"])
            ).as_posix()
            isaobject.urls.append(f"irods://{path}")

    def _create_investigation(self, investigation):
        # https://omero.readthedocs.io/en/stable/sysadmins/cli/usergroup.html
        user_name = self.manager
        (ome_user,) = self.conn.getObjects(
            "experimenter", attributes={"omeName": user_name}
        )

        # set read_annotate permission
        group_id = self.conn.createGroup(
            name=investigation.name, owner_Ids=[ome_user.id], perms="rwra--"
        )

        investigation.ome_id = group_id
        group = self.conn.getObject("ExperimenterGroup", group_id)
        self.mapping[investigation.id] = group
        self._update_members(investigation, group)

    def _update_members(self, investigation, group):
        self.log.info("Updating members from omeromanager")

        cli = omero_admin_cli(self.conf)
        cli.invoke(
            [
                "group",
                "adduser",
                "--name",
                investigation.name,
                "--as-owner",
                self.conf["omero"]["OMERO_ADMIN"],
            ],
            strict=True,
        )

        for member in investigation.members:
            if member.role in ["owner", "manager"]:
                cli.invoke(
                    [
                        "group",
                        "adduser",
                        "--name",
                        investigation.name,
                        "--as-owner",
                        member.name,
                    ],
                    strict=True,
                )
            else:
                cli.invoke(
                    [
                        "group",
                        "adduser",
                        "--name",
                        investigation.name,
                        member.name,
                    ],
                    strict=True,
                )
        cli.invoke(
            [
                "group",
                "removeuser",
                "--name",
                investigation.name,
                "--as-owner",
                self.conf["omero"]["OMERO_ADMIN"],
            ],
            strict=True,
        )
        self.mapping[investigation.id] = group

    def _parse_ome(self, depth, isaobject, ome):
        self.log.info("Parsing ome-cli-transfer xml for %s", isaobject.name)
        duplicates = []
        paths = get_image_paths(ome)

        for ome_image in ome.images:
            if depth == 2:
                investigation = isaobject
                study = None
                assay = None

            elif depth == 1:
                study = isaobject
                investigation = find_by_id(
                    study.parents[-1], self.manifest.investigations
                )
                assay = None

            elif depth == 0:
                assay = isaobject
                study = find_by_id(assay.parents[-1], self.manifest.studies)
                investigation = find_by_id(
                    study.parents[-1], self.manifest.investigations
                )

            image_path = Path(paths[ome_image.id])
            parts = image_path.parts
            if study is None:
                study_name = "orphaned" if len(parts) < 3 else parts[-3]
                study = find_by_name(
                    study_name,
                    expand_ids(investigation.children, self.manifest.studies),
                )
                if study is None:
                    self.log.info("Declaring study %s", study_name)
                    inv_path = get_path(investigation, "file")
                    study = Study(
                        id=f"stu_{uuid1()}",
                        name=study_name,
                        owner=investigation.owner,
                        urls=[f"file://{inv_path}/{study_name}"],
                    )
                    self._set_irods_path(study)
                    study.parents.append(investigation.id)
                    investigation.children.append(study.id)
                    self.manifest.studies.append(study)
                    self.created_isaobjects.append(study)

            if assay is None:
                assay_name = "orphaned" if len(parts) < 2 else parts[-2]
                assay = find_by_name(
                    assay_name, expand_ids(study.children, self.manifest.assays)
                )

                if assay is None:
                    self.log.info("Undeclared Assay detected")
                    stu_path = get_path(study, "file")

                    assay = Assay(
                        id=f"ass_{uuid1()}",
                        name=assay_name,
                        owner=investigation.owner,
                        urls=[f"file://{stu_path}/{assay_name}"],
                        parents=[study.id],
                    )
                    self._set_irods_path(assay)
                    self.created_isaobjects.append(assay)
                    study.children.append(assay.id)
                    assay.parents.append(study.id)
                    self.manifest.assays.append(assay)

            for project in ome.projects:
                if project.id == f"Project:{study.ome_id}":
                    break
            else:
                if study.ome_id is None:
                    study.ome_id = randint(2**28, 2**30)
                project = mod.Project(id=f"Project:{study.ome_id}", name=study.name)
                ome.projects.append(project)
                self._annotate(study, ome, project)

            for dataset in ome.datasets:
                if dataset.id == f"Dataset:{assay.ome_id}":
                    break
            else:
                if assay.ome_id is None:
                    assay.ome_id = randint(2**28, 2**30)
                dataset = mod.Dataset(id=f"Dataset:{assay.ome_id}", name=assay.name)
                project.dataset_refs.append(mod.DatasetRef(id=dataset.id))
                ome.datasets.append(dataset)
                self._annotate(assay, ome, dataset)

            base_path = get_path(assay, "file")
            irods_path = get_path(assay, "irods")
            image = Image(
                id=f"img_{uuid1()}",
                name=ome_image.name,
                owner=investigation.owner,
                urls=[
                    f"file://{base_path}/{image_path.as_posix()}",
                    f"irods://{irods_path}/{image_path.as_posix()}",
                ],
            )
            image.parents.append(assay.id)
            if self._exists(image) and (image not in duplicates):
                duplicates.append(ome_image)

            assay.images.append(image.id)
            self.manifest.images.append(image)
            dataset.image_refs.append(mod.ImageRef(id=ome_image.id))

            ome.experimenter_groups = [
                mod.ExperimenterGroup(id=uuid1().int, name=investigation.name)
            ]

        if duplicates:
            self.log.warning("Found %d existing images", len("dupicates"))
            return duplicates
        return []

    def _annotate(self, isaobject, ome=None, localobject=None):
        mmap = [M(k=k, value=str(v)) for k, v in get_identifiers(isaobject).items()]
        ann = mod.MapAnnotation(
            id=f"Annotation:{uuid1().int}", value=Map(ms=mmap), namespace="quay"
        )
        ome.structured_annotations.append(ann)
        localobject.annotation_refs.append(mod.AnnotationRef(id=ann.id))

        for ann_id in isaobject.quay_annotations:
            ann = find_by_id(ann_id, self.manifest.quay_annotations)
            ome_kls = ann_map[ann.ann_type]

            match ome_kls:
                case mod.MapAnnotation:
                    mmap = [M(k=kv.key, value=str(kv.value)) for kv in ann.kv_pairs]

                    local_ann = mod.MapAnnotation(
                        id=f"Annotation:{uuid1().int}",
                        value=Map(ms=mmap),
                        namespace="quay",
                    )
                    ome.structured_annotations.append(local_ann)
                    localobject.annotation_refs.append(
                        mod.AnnotationRef(id=local_ann.id)
                    )
                case mod.TagAnnotation | mod.CommentAnnotation:
                    local_ann = ome_kls(
                        id=f"Annotation:{uuid1().int}",
                        value=ann.value,
                        namespace="quay",
                    )
                    ome.structured_annotations.append(local_ann)
                    localobject.annotation_refs.append(
                        mod.AnnotationRef(id=local_ann.id)
                    )

    def update_manifest(self, isaobject, ome):
        """ """
        raise NotImplementedError

    @staticmethod
    def _write_ome(isaobject, ome, out="transfer.xml"):
        path = Path(get_path(isaobject, "file")) / out
        with path.open("w") as th:
            th.write(to_xml(ome))

    @staticmethod
    def _write_transfer(isaobject, ome):
        path = Path(get_path(isaobject, "file")) / "transfer.xml"
        with path.open("w") as th:
            th.write(to_xml(ome))


def get_image_paths(ome):
    """
    Retrieves original import paths from annotations in an OME object
    generated by omero-cli-transfer
    """
    xml_anns = {
        ann.id: ann.value.any_elements[0].children[0].text
        for ann in ome.structured_annotations.xml_annotations
    }

    original_paths = {}
    for img in ome.images:
        for ref in img.annotation_refs:
            if ref.id in xml_anns:
                original_paths[img.id] = xml_anns[ref.id]
                break
    if len(original_paths) != len(ome.images):
        msg = f"Not all paths found for images {', '.join([img.name for img in ome.images])} "
        raise ValueError(msg)

    return original_paths


# post_map_annotation(self.conn, otype, localobject.getId(), ids, ns="quay")


def deduplicate_map_annotations(conn, otype, omero_id, ns):
    solidified = {}
    to_delete = []

    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []
    # Deduplicate
    for ann in omero_object.listAnnotations(ns):
        if hasattr(ann, "getMapValueAsMap"):
            _map = ann.getMapValueAsMap()
            solidified.update(_map)
            to_delete.append(ann.id)

    post_map_annotation(conn, otype, omero_object.getId(), solidified, ns)
    return to_delete


def deduplicate_tags(conn, otype, omero_id):
    tag_d = defaultdict(set)
    existings = {}
    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []

    to_delete = []
    for tag in omero_object.listAnnotations():
        if isinstance(tag, TagAnnotationWrapper):
            text = tag.getValue()
            existing = next(
                iter(conn.getObjects("TagAnnotation", attributes={"textValue": text}))
            )
            tag_d[text] = tag_d[text].union({tag.id})
            existings[text] = existing

    for text in tag_d:
        tags, existing = tag_d[text], existings[text]
        if existing.id not in tags:
            omero_object.linkAnnotation(existing)
        to_delete.extend(list(tags - {existing.id}))
    return to_delete


def post_unique_map_annotation(conn, otype, omero_id, mapping, ns):
    solidified = {}
    to_delete = []

    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []
    # Deduplicat
    for ann in omero_object.listAnnotations(ns):
        if hasattr(ann, "getMapValueAsMap"):
            _map = ann.getMapValueAsMap()
            solidified.update(_map)
            to_delete.append(ann.id)

    # Update
    solidified.update(mapping)
    post_map_annotation(conn, otype, omero_id, solidified, ns)
    return to_delete

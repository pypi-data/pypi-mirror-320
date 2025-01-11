from __future__ import annotations

import logging
import os
from pathlib import Path
from uuid import uuid1

import pandas as pd

from ..core.config import get_conf
from ..core.interface import Interface
from ..core.manifest import (
    Assay,
    DataLink,
    Investigation,
    KVPair,
    MapAnnotation,
    Study,
    TagAnnotation,
    User,
)
from ..core.utils import find_by_id, find_by_name, get_path

log = logging.getLogger(__name__)


class XlsxParser(Interface):
    def __init__(self, conf, xlsx_path):
        super().__init__(conf, scheme="xlsx", host=os.uname().nodename)
        self.xlsx_path = Path(xlsx_path).resolve()
        self.sheets = {}
        self.users = {}

    def parse(self):
        self.log.info("Loading excel file %s", self.xlsx_path)
        sheet_names = ["User", "Investigation", "Study", "Assay"]
        sheets = pd.read_excel(self.xlsx_path, sheet_names)
        self.sheets = {
            key: dataframe.dropna(how="all")
            .reset_index(drop=True)
            # .replace(pd.NA, "")
            .apply(_cleanup)
            for key, dataframe in sheets.items()
        }
        self._parse_users()
        # Only one manager is supported
        self.manager = self.sheets["Investigation"].loc[0, "manager"]
        self.manifest.manager = self.manager

        for idx in self.sheets["Investigation"].index:
            self._parse_investigation(idx)
        for idx in self.sheets["Study"].index:
            self._parse_study(idx)
        for idx in self.sheets["Assay"].index:
            self._parse_assay(idx)

        self.set_state("checked")

    def _parse_investigation(self, idx: int):
        row = self.sheets["Investigation"].loc[idx].replace(pd.NA, "")
        inv = Investigation(
            id=f"inv_{uuid1()}", name=row["name"], description=row["description"]
        )
        for roles in ["collaborators", "contributors", "owners"]:
            if not row[roles]:
                continue
            for o in row[roles].split(","):
                if not self.users[o].role:
                    self.users[o].role = roles[:-1]
                inv.members.append(self.users[o])

        inv.owner = row["owners"].split(",")[0]

        if row["samba_path"]:
            samba_url = _parse_samba_path(row["samba_path"])
            self.log.info("Using SAMBA path")
            inv.urls.append(samba_url)
        elif row["irods_path"]:
            irods_url = f"irods://{row['irods_path']}"
            self.log.info("Using iRODS path")
            inv.urls.append(irods_url)

        self.manifest.investigations.append(inv)

    def _get_srce_url(self, row, inv):
        if root_path := get_path(inv, "smb"):
            scheme = "smb"
        elif root_path := get_path(inv, "irods"):
            scheme = "irods"
        row_path = row["path"].replace("\\", "/")
        return f"{scheme}://{root_path}/{row_path}"

    def _parse_study(self, idx: int):
        stu = self.sheets["Study"].loc[idx]
        inv_name = stu["parent_investigation"]
        inv = find_by_name(inv_name, self.manifest.investigations)

        if inv is None:
            msg = f"Parent investigation {inv_name} not found for study {stu['name']}"
            raise KeyError(msg)

        study = Study(
            id=f"stu_{uuid1()}",
            name=stu["name"],
            owner=stu["owner"],
            description=str(stu["description"]),
            parents=[inv.id],
        )
        if stu.get("path"):
            srce_url = self._get_srce_url(stu, inv)
            study.importlink = DataLink(
                id=f"imp_{uuid1()}",
                owner=self.manager,
                srce_url=srce_url,
            )
        if stu["tags"] and not pd.isna(stu["tags"]):
            tags = stu["tags"].split(",")
            for tag in tags:
                tag_ann = TagAnnotation(
                    id=f"ann_{uuid1()}",
                    value=tag,
                    namespace="quay",
                )
                self.manifest.quay_annotations.append(tag_ann)
                study.quay_annotations.append(tag_ann.id)

        inv.children.append(study.id)
        self.manifest.studies.append(study)

    def _parse_assay(self, idx: int):
        keys = self.conf["excel"]["keys"]

        ass = self.sheets["Assay"].loc[idx]
        stu_name = ass["parent"]
        study = find_by_name(stu_name, self.manifest.studies)

        if study is None:
            msg = f"Parent study {stu_name} not found for assay {ass['name']}"
            raise KeyError(msg)

        inv_name = study.parents[0]
        inv = find_by_id(inv_name, self.manifest.investigations)

        assay = Assay(
            id=f"ass_{uuid1()}",
            name=ass["name"],
            owner=ass["owner"],
            description=str(ass["description"]),
            parents=[study.id],
        )

        if ass.get("path"):
            srce_url = self._get_srce_url(ass, inv)
            assay.importlink = DataLink(
                id=f"imp_{uuid1()}",
                owner=self.manager,
                srce_url=srce_url,
            )

        study.children.append(assay.id)
        self.manifest.assays.append(assay)

        kv_pairs = [KVPair(key=k, value=v) for k, v in dict(ass[keys].dropna()).items()]
        map_ann = MapAnnotation(
            id=f"ann_{uuid1()}", kv_pairs=kv_pairs, namespace="quay"
        )
        assay.quay_annotations.append(map_ann.id)
        self.manifest.quay_annotations.append(map_ann)

        if ass["tags"] and not pd.isna(ass["tags"]):
            tags = ass["tags"].split(",")
            for tag in tags:
                tag_ann = TagAnnotation(
                    id=f"ann_{uuid1()}",
                    value=tag,
                    namespace="quay",
                )
                self.manifest.quay_annotations.append(tag_ann)
                assay.quay_annotations.append(tag_ann.id)

    def _parse_users(self):
        for _, user in self.sheets["User"].iterrows():
            self.users[user["login"]] = User(
                id=user.get("orcid_id", f"usr_{uuid1()}"),
                name=user["login"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                institution=user["institution"],
            )


def parse_xlsx(xlsx_path):
    xlsx_path = Path(xlsx_path).resolve()
    log.info("Loading excel file %s", xlsx_path)
    conf = get_conf()
    with XlsxParser(conf, xlsx_path) as parser:
        parser.parse()
        return parser.manifest


def _cleanup(col):
    quotes = "' «»“”’'"  # noqa:RUF001

    try:
        return col.str.strip(quotes)
    except AttributeError:
        return col


def _parse_samba_path(win_path):
    if ":" in win_path:
        win_path = win_path.split(":")[1]
    win_path = "/".join(win_path.split("\\"))
    return f"smb:/{win_path}"

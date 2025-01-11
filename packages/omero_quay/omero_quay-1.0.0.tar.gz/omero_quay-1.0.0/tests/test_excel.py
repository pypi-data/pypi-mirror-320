from __future__ import annotations

from pathlib import Path

import pytest
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import yaml_loader

from omero_quay.core.manifest import Manifest
from omero_quay.parsers.errors import (
    ExcelValidationError,
    MissingExcelSheetError,
    NoExistingOMEROUser,
    UserNotInOMEROGroup,
)
from omero_quay.parsers.excel import parse_xlsx
from omero_quay.parsers.validate_excel import (
    check_assay_owner_is_parent_study_owner_or_contributor,
    check_everything,
    check_if_assay_path_is_subpath_of_other_assay,
    check_if_user_in_group,
    check_study_owner_is_parent_investigation_owner_or_contributor,
    validate_assays_parent_studies,
    validate_logins,
    validate_user_existence,
    validate_xlsx_structure,
)

"""
Tests for all known use cases of possible errors with Excel XLSX file.
"""


def test_invalid_omero_user():
    with pytest.raises(NoExistingOMEROUser):
        validate_user_existence("omero_invalid_user")


def test_omero_user_not_in_group(base_import):  # noqa:ARG001
    with pytest.raises(UserNotInOMEROGroup):
        check_if_user_in_group("facility0", "system")


def test_parse(xlsx_import_path, yaml_manifest_2):
    manifest = parse_xlsx(xlsx_import_path)
    assert manifest.studies
    with Path(yaml_manifest_2).open("w") as mf:
        mf.write(yaml_dumper.dumps(manifest))

    with Path(yaml_manifest_2).open("r") as mf:
        manifest = yaml_loader.loads(mf, target_class=Manifest)


def test_no_tags():
    manifest = parse_xlsx("./tests/excel_files/study_assay_no_tags_entries.xlsx")
    assert len(manifest.studies[1].quay_annotations) == 0


def test_check_everything(xlsx_import_path):
    assert check_everything(xlsx_import_path)


@pytest.mark.parametrize(
    "missing_excel_sheet",
    list(Path("./tests/excel_files/missing_excel_sheet/").glob("*.xlsx")),
)
def test_missing_sheet(missing_excel_sheet):
    with pytest.raises(MissingExcelSheetError):
        validate_xlsx_structure(missing_excel_sheet)


def test_user_sheet_no_logins_column():
    with pytest.raises(ExcelValidationError):
        validate_xlsx_structure("./tests/excel_files/user_no_logins_sheet.xlsx")


def test_user_invalid_logins_sheet():
    with pytest.raises(NoExistingOMEROUser):
        validate_logins("./tests/excel_files/user_invalid_logins_sheet.xlsx")


def test_user_no_login_sheet():
    with pytest.raises(ExcelValidationError):
        validate_logins("./tests/excel_files/user_no_login_user_sheet.xlsx")


def test_investigation_empty_collaborators_and_contributors():
    validate_logins(
        "./tests/excel_files/investigation_empty_collaborators_and_contributors_sheet.xlsx"
    )


@pytest.mark.parametrize(
    "no_existing_omero_user",
    list(Path("./tests/excel_files/no_existing_omero_user/").glob("*.xlsx")),
)
def test_no_existing_omero_user(no_existing_omero_user):
    with pytest.raises(NoExistingOMEROUser):
        validate_logins(no_existing_omero_user)


@pytest.mark.parametrize(
    "no_valid_user",
    list(Path("./tests/excel_files/no_valid_user/").glob("*.xlsx")),
)
def test_no_valid_user(no_valid_user):
    with pytest.raises(ExcelValidationError):
        validate_logins(no_valid_user)


@pytest.mark.parametrize(
    "invalid_excel_structure",
    list(Path("./tests/excel_files/invalid_excel_structure/").glob("*.xlsx")),
)
def test_invalid_excel_structure(invalid_excel_structure):
    with pytest.raises(ExcelValidationError):
        validate_xlsx_structure(invalid_excel_structure)


def test_assays_parent_studies():
    with pytest.raises(ExcelValidationError):
        validate_assays_parent_studies(
            "./tests/excel_files/assay_parent_is_invalid_study_sheet.xlsx"
        )


def test_check_study_owner_is_parent_investigation_owner_or_contributor():
    with pytest.raises(ExcelValidationError):
        check_study_owner_is_parent_investigation_owner_or_contributor(
            "./tests/excel_files/study_owner_is_not_parent_investigation_owner_or_contributor_sheet.xlsx"
        )


def test_check_assay_owner_is_parent_study_owner_or_contributor():
    with pytest.raises(ExcelValidationError):
        check_assay_owner_is_parent_study_owner_or_contributor(
            "./tests/excel_files/assay_owner_is_absent_contributor_sheet.xlsx"
        )


def check_is_path_is_subpath():
    with pytest.raises(ExcelValidationError):
        check_if_assay_path_is_subpath_of_other_assay(
            "./tests/excel_files/assay_atleast_one_path_is_subpath_of_one_path_sheet.xlsx"
        )

from __future__ import annotations


class ExcelValidationError(Exception):
    """Base error for excel parser"""


class NoExistingOMEROUser(ExcelValidationError):
    def __init__(self, entered_user_login):
        self.message = f"User {entered_user_login} does not exist in OMERO"


class MissingExcelSheetError(ExcelValidationError):
    def __init__(self, sheet_name, file_path):
        self.message = f"Sheet {sheet_name} does not exist in {file_path} Excel file"

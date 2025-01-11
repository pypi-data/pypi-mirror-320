from enum import StrEnum


class ToolTypes(StrEnum):
    COPY_DIR = "copy-dir"
    CREATE_DIR = "create-dir"
    RENAME_DIR = "rename-dir"
    DELETE_DIR = "delete-dir"
    COPY_FILE = "copy-file"
    CREATE_FILE = "create-file"
    RENAME_FILE = "rename-file"
    DELETE_FILE = "delete-file"
    EDIT_CONTENT = "edit-content"
    COPY_ALL = "copy-all"
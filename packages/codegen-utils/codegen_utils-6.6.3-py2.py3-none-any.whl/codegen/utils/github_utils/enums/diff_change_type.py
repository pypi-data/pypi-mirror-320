from enum import StrEnum


class DiffChangeType(StrEnum):
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    MODIFIED = "M"

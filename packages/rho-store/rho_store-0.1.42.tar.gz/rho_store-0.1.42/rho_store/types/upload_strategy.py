import enum


class ExtendedEnum(enum.Enum):
    @classmethod
    def values(cls) -> set[str]:
        return set(map(lambda c: c.value, cls))

    @classmethod
    def keys(cls) -> set[str]:
        return set(map(lambda c: c.name, cls))


class UploadStrategy(ExtendedEnum):
    NEW_TABLE = "NEW_TABLE"
    NEW_VERSION = "NEW_VERSION"
    APPEND = "APPEND"
    MERGE = "MERGE"
    REPLACE = "REPLACE"


__all__ = ["UploadStrategy"]

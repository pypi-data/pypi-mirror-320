from dataclasses import dataclass


@dataclass(frozen=True)
class SortOption:
    name: str
    desc: bool = False


@dataclass(frozen=True)
class FilterOption:
    name: str
    value: str | float | int
    op: str = "like"

    VALID_OPERATORS = {
        "in_range",
        "in",
        "is",
        "like",
        "=",
        ">",
        ">=",
        "<",
        "<=",
    }

    def __post_init__(self):
        if self.op not in self.VALID_OPERATORS:
            raise ValueError(f"Invalid operator. Must be one of: {', '.join(self.VALID_OPERATORS)}")


__all__ = ["SortOption", "FilterOption"]

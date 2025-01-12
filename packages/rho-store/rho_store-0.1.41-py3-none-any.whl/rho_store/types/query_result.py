from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class QueryResult:
    id: str
    time: float
    rows: list[tuple]
    columns: tuple[str]
    total_rows: int

    def to_list(self) -> list[dict]:
        return [dict(zip(self.columns, row)) for row in self.rows]

    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(data=self.rows, columns=self.columns)
        df.drop(columns=["_id", "_version", "_created_at"], inplace=True, errors="ignore")
        return df


__all__ = ["QueryResult"]

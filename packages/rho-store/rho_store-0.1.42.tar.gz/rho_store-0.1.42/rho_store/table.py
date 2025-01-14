from typing import Callable, Protocol

import pandas as pd

from .config import init_config
from .types import StoreDfCommand, QueryResult, SortOption, UploadStrategy


class MakeQueryProtocol(Protocol):
    def __call__(
        self,
        table_id: str,
        columns: list[str] | None = None,
        version: int | None = None,
        sort: list[SortOption] | None = None,
        filters: list[tuple[str, str, any]] | None = None,
        page: int = 1,
        limit: int = 10000,
        search: str | None = None,
    ) -> QueryResult: ...


class Table:
    def __init__(
        self,
        workspace_id: str,
        table_id: str,
        latest_version: int,
        name: str = "",
        data: pd.DataFrame = None,
        fetch_data: Callable[[str, int], pd.DataFrame] = None,
        store_data: Callable[[StoreDfCommand], None] = None,
        make_query: MakeQueryProtocol = None,
    ):
        self.workspace_id = workspace_id
        self.table_id = table_id
        self.latest_version = latest_version
        self.name = name
        self._data = data
        self._fetch_data = fetch_data
        self._store_data = store_data
        self._make_query = make_query
        self._config = init_config()

    def __str__(self) -> str:
        return f'<Table id="{self.table_id}" name="{self.name}" url="{self.client_url}">'

    def __repr__(self) -> str:
        return f'<Table id="{self.table_id}" name="{self.name}" url="{self.client_url}">'

    @property
    def client_url(self) -> str:
        return f"{self._config.CLIENT_URL}/app/tables/{self.table_id}?wid={self.workspace_id}"

    @property
    def data(self, refresh: bool = False) -> pd.DataFrame:
        if self._data is None or refresh is True:
            self._data = self.fetch_data()
        return self._data

    def fetch_data(self, version: int = None) -> pd.DataFrame:
        return self._fetch_data(self.table_id, version)

    def make_query(
        self,
        columns: list[str] | None = None,
        version: int | None = None,
        sort: list[SortOption] | None = None,
        filters: list[tuple[str, str, any]] | None = None,
        page: int = 1,
        limit: int = 10000,
        search: str | None = None,
    ) -> QueryResult:
        return self._make_query(
            table_id=self.table_id,
            columns=columns,
            version=version,
            sort=sort,
            filters=filters,
            page=page,
            limit=limit,
            search=search,
        )

    def append(self, data: pd.DataFrame) -> None:
        command = StoreDfCommand(
            data=data, table_id=self.table_id, strategy=UploadStrategy.APPEND.value, run_async=True
        )
        self._store_data(command)
        self._clear_cache()

    def replace(self, data: pd.DataFrame) -> None:
        command = StoreDfCommand(
            data=data,
            table_id=self.table_id,
            strategy=UploadStrategy.REPLACE.value,
            run_async=True
        )
        self._store_data(command)
        self._clear_cache()

    def merge(self, data: pd.DataFrame, column: str) -> None:
        command = StoreDfCommand(
            data=data,
            table_id=self.table_id,
            strategy=UploadStrategy.MERGE.value,
            merge_options={"column": column},
            run_async=True
        )
        self._store_data(command)
        self._clear_cache()

    def new_version(self, data: pd.DataFrame) -> None:
        command = StoreDfCommand(
            data=data,
            table_id=self.table_id,
            strategy=UploadStrategy.NEW_VERSION.value,
            run_async=True
        )
        self._store_data(command)
        self._clear_cache()

    def _clear_cache(self) -> None:
        self._data = None


__all__ = ["Table"]

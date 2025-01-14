from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Callable

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.widgets import DataTable
from textual.widgets.data_table import Column, ColumnKey, CellKey
from typing_extensions import Self

SORT_INDICATOR_UP: Final[str] = ' \u25b4'
SORT_INDICATOR_DOWN: Final[str] = ' \u25be'


@dataclass
class Sort:
    key: ColumnKey | None = None
    label: str = ''
    direction: bool = False

    def reverse(self) -> None:
        self.direction = not self.direction

    @property
    def indicator(self) -> str:
        return SORT_INDICATOR_UP if self.direction else SORT_INDICATOR_DOWN


class SortableDataTable(DataTable):
    DEFAULT_CSS = """
    SortableDataTable {
        height: 1fr;
        border: $foreground 80%;
    }
    """

    BINDINGS = [
        Binding('z', 'toggle_zebra', 'Toggle Zebra', show=False)
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._sort = Sort()
        self.cursor_type = 'row'  # type: ignore
        self.show_row_labels = False
        self.sort_function: Callable[[Any], Any] | None = None

    @property
    def sort_column(self) -> Sort:
        return self._sort

    def _column_key(self, _label: str) -> ColumnKey | None:
        for key, label in self.columns.items():
            if label.label.plain == _label:
                return key

        return None

    @property
    def sort_column_label(self) -> str | None:
        if self._sort.key is None:
            return None

        label: Text = self.columns[self._sort.key].label
        label.remove_suffix(self._sort.indicator)
        return str(label)

    def clear(self, columns: bool = False) -> Self:
        super().clear(columns)
        # _sort contains a column key that becomes invalid when clearing the columns, so reset it.
        self._sort = Sort()
        return self

    def column_names(self) -> list[Column]:
        data = self.columns.copy()
        if self._sort.key:
            column = data[self._sort.key]
            column.label.remove_suffix(self._sort.indicator)

        return list(data.values())

    @on(DataTable.HeaderSelected)
    def header_clicked(self, header: DataTable.HeaderSelected) -> None:
        self.sort_on_column(header.column_key)

    def sort_on_column(self, key: ColumnKey | str, direction: bool | None = None) -> None:
        if isinstance(key, str):
            key = self._column_key(key)  # type: ignore
            if key is None:
                return

        assert isinstance(key, ColumnKey)

        if self._sort.key is not None:
            column = self.columns[self._sort.key]
            column.label.remove_suffix(self._sort.indicator)
            self._update_column_width(self._sort.key)

        sort_value = Sort(key=key)
        if self._sort.key == sort_value.key:
            sort_value = self._sort
            sort_value.reverse()

        assert sort_value.key

        self.columns[key].label += sort_value.indicator
        self._update_column_width(key)

        if direction is not None:
            sort_value.direction = direction

        try:
            self.sort(sort_value.key, reverse=sort_value.direction, key=self.sort_function)
            self._sort = sort_value
        except TypeError:
            self.columns[key].label.remove_suffix(self._sort.indicator)
            print(f'Error sorting on column: {sort_value.key.value}')

    def _update_column_width(self, key: ColumnKey) -> None:
        if len(self.rows) == 0:
            return

        self._update_column_widths({CellKey(row_key=next(iter(self.rows)), column_key=key)})

    def action_toggle_zebra(self) -> None:
        self.zebra_stripes = not self.zebra_stripes

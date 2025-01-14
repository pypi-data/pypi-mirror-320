from __future__ import annotations

from typing import Any

from rich.style import Style
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.widgets import DataTable, Label

from slurm_viewer.data.node_model import Node
from slurm_viewer.data.queue_model import Queue
from slurm_viewer.widgets.table_formatting import format_value


class DetailScreen(ModalScreen[None]):
    BINDINGS = [('escape', 'pop_screen')]

    DEFAULT_CSS = """
    DetailScreen {
        align: center middle;
        width: auto;
        height: auto;
        & > DataTable {
            width: auto;
            min-width: 50%;
            height: auto;
            background: $panel;
        }
        & > Label {
            background: $panel;
        }
    }
    """

    def __init__(self, model: Node | Queue, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.model = model
        columns = set(self.model.model_fields.keys())
        columns.update(name for name, value in vars(type(self.model)).items() if isinstance(value, property))
        self._columns = sorted(columns)

    def compose(self) -> ComposeResult:
        data_table: DataTable = DataTable(show_row_labels=False)
        data_table.add_columns('key', 'value')
        data_table.cursor_type = 'row'
        data_table.zebra_stripes = True
        data_table.border_title = 'Detailed information'
        yield data_table
        yield Label()

    def on_mount(self) -> None:
        def format_func(_value: Any, style: Style) -> Text:
            if isinstance(_value, float):
                return Text(f'{_value:.2f}', style=style, justify='left')

            return Text(str(_value), style=style, justify='left')

        data_table = self.query_one(DataTable)

        for key in sorted(self._columns):
            value = getattr(self.model, key)
            if value is None:
                continue
            data_table.add_row(key, format_value(self.model, key, _format_func=format_func))

        data_table.sort(data_table.coordinate_to_cell_key(Coordinate(0, 0)).column_key)

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    @on(DataTable.RowHighlighted)
    def row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        key = event.control.get_row_at(event.cursor_row)[0]
        self.query_one(Label).update(f'{key}: {self._get_description(key)}')

    def _get_description(self, key: str) -> str:
        default = 'No description available.'
        if key in self.model.model_fields:
            desc = self.model.model_fields[key].description
            return desc if desc is not None else default

        if key in self.model.model_computed_fields:
            desc = self.model.model_computed_fields[key].description
            return desc if desc is not None else default

        return default

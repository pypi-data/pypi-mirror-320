from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Static, Label, Button

from slurm_viewer.data.config import Config
from slurm_viewer.widgets.loading import Loading
from slurm_viewer.data.slurm_communication import Slurm
from slurm_viewer.data.priority_model import Priority
from slurm_viewer.widgets.sortable_data_table import SortableDataTable


class PriorityWidget(Static):
    CSS_PATH = Path(__file__) / 'slurm_viewer.tcss'

    config: reactive[Config] = reactive(Config, layout=True, always_update=True)

    def __init__(self, _slurm: Slurm, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slurm = _slurm
        self.priority_info: list[Priority] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(id='priority_horizontal'):
                yield Label(f'Last update: {datetime.datetime.now().strftime("%H:%M:%S")}', id='priority_label')
                yield Button(label='Refresh', id='priority_refresh', disabled=True)
            with ScrollableContainer():
                yield SortableDataTable(id='priority_table')

    @work
    async def watch_config(self, _: Config, __: Config) -> None:
        with Loading(self):
            self.priority_info = await self.slurm.priority()
            self._priority_data_table()

    def on_mount(self) -> None:
        self._priority_data_table()

    def copy_to_clipboard(self) -> None:
        self.app.copy_to_clipboard('PriorityWidget copy to clipboard')

    def _priority_data_table(self) -> None:
        def _text(value: str | int | float) -> Text:
            if isinstance(value, str):
                return Text(value, justify='right')
            if isinstance(value, int):
                return Text(str(value), justify='right')
            if isinstance(value, float):
                if value < 1.0:
                    return Text(f'{value:.6f}', justify='right')
                return Text(f'{value:.0f}', justify='right')
            raise RuntimeError(f'Unexpected type {type(value)}')

        if not self.is_mounted:
            return

        data_table = self.query_one('#priority_table', SortableDataTable)
        data_table.cursor_type = 'row'
        data_table.clear(columns=True)
        data_table.zebra_stripes = True
        data_table.add_columns(*self.config.ui.priority_columns)
        data_table.border_title = f'{len(self.priority_info)} users'

        for row in self.priority_info:
            data = [_text(getattr(row, key)) for key in self.config.ui.priority_columns]
            data_table.add_row(*data)

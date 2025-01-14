from __future__ import annotations

import datetime
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work, on
from textual.app import ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane, Label, Button, Checkbox

from slurm_viewer.data.config import Config
from slurm_viewer.data.models import SlurmError
from slurm_viewer.data.node_model import Node, State
from slurm_viewer.data.queue_model import Queue
from slurm_viewer.data.slurm_protocol import SlurmProtocol
from slurm_viewer.widgets.loading import Loading
from slurm_viewer.widgets.sortable_data_table import SortableDataTable


class StatusWidget(Static):
    CSS_PATH = Path(__file__) / 'slurm_viewer.tcss'

    config: reactive[Config] = reactive(Config, layout=True, always_update=True)

    def __init__(self, _slurm: SlurmProtocol, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slurm = _slurm
        self.cluster_info: list[Node] = []
        self.queue_info: list[Queue] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(id='horizontal_spacer')
            yield Label(id='status_label')
            yield Button(label='Refresh', id='status_refresh')
            with ScrollableContainer(id='status_scrollable_container'):
                with TabbedContent(id='cluster_tab'):
                    with TabPane('Resource Information'):
                        yield SortableDataTable(id='resource_table')
                    with TabPane('Partition Information'):
                        yield SortableDataTable(id='partition_table')
                    with TabPane('User Information'):
                        yield SortableDataTable(id='user_table')

    @work(name='status_widget_watch_config')
    async def watch_config(self, _: Config, __: Config) -> None:
        try:
            widget: Widget = self.query_one('#status_scrollable_container', ScrollableContainer)
        except NoMatches:
            return

        with Loading(widget):
            try:
                self.cluster_info = await self.slurm.nodes()
                self.queue_info = await self.slurm.queue(user_only=False)
                self.query_one('#status_label', Label).update(f'Last update: {datetime.datetime.now().strftime("%H:%M:%S")}')
                await self.update_status_info()
            except SlurmError as e:
                self.app.notify(title='Error retrieving data from cluster', message=str(e), severity='error')

    @work(name='status_widget_refresh_info')
    @on(Button.Pressed, '#status_refresh')
    async def refresh_info(self, _: Checkbox.Changed) -> None:
        await self.timer_update()

    async def timer_update(self) -> None:
        try:
            self.cluster_info = await self.slurm.nodes()
            self.queue_info = await self.slurm.queue(user_only=False)
            await self.update_status_info()
            self.query_one('#nodes_label', Label).update(f'Last update: {datetime.datetime.now().strftime("%H:%M:%S")}')
        except SlurmError as e:
            self.app.notify(title='Error updating nodes', message=str(e), severity='error')

    async def update_status_info(self) -> None:
        @dataclass
        class Cpu:
            tot: int = 0
            alloc: int = 0
            offline: int = 0

            @property
            def idle(self) -> int:
                return self.tot - self.alloc

            def add(self, tot: int, alloc: int) -> None:
                self.tot += tot
                self.alloc += alloc

            def add_offline(self, offline: int) -> None:
                self.offline += offline

        data: defaultdict[str, Cpu] = defaultdict(Cpu)
        for node in self.cluster_info:
            for partition in node.partitions:
                if (State.DOWN, State.DRAIN) in node.states:
                    data[partition].add(node.cpu_tot, node.cpu_alloc)
                    continue

                data[partition].add(node.cpu_tot, node.cpu_alloc)

        partition_table = self.query_one('#partition_table', SortableDataTable)
        partition_table.cursor_type = 'row'
        partition_table.clear(columns=True)
        partition_table.zebra_stripes = True
        partition_table.add_columns('Partition', 'CPU (Tot)', 'CPU (Alloc)', 'CPU (Idle)', 'CPU (Offline)')

        for key, value in data.items():
            partition_table.add_row(
                key,
                Text(str(value.tot), justify='right'),
                Text(str(value.alloc), justify='right'),
                Text(str(value.idle), justify='right'),
                Text(str(value.offline), justify='right')
            )

    def copy_to_clipboard(self) -> None:
        self.app.copy_to_clipboard('statusWidget copy to clipboard')

    async def _status_data_table(self) -> None:
        pass

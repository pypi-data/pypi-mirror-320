from __future__ import annotations

import platform
from pathlib import Path
from typing import Protocol, cast, Final, Generator, Callable

# pylint: disable=wrong-import-position,
import rich

rich.print('Starting application .', end='')
from textual.app import App, ComposeResult

rich.print('.', end='')
from textual.binding import Binding

rich.print('.', end='')
from textual.containers import Vertical

rich.print('.', end='')
from textual.reactive import reactive

rich.print('.', end='')
from textual.widget import Widget
from textual.widgets import Footer, Header, TabbedContent, TabPane, HelpPanel

rich.print('.', end='')
from textual.css.query import NoMatches

rich.print('.', end='')
from slurm_viewer.data.slurm_communication import Slurm
from slurm_viewer.data.slurm_protocol import SlurmProtocol
from slurm_viewer.data.config import Config, Tabs, Cluster

rich.print('.', end='')
from slurm_viewer.widgets.nodes_widget import NodesWidget
rich.print('.', end='')
from slurm_viewer.widgets.queue_widget import QueueWidget
rich.print('.', end='')
from slurm_viewer.widgets.status_widget import StatusWidget

rich.print('.', end='')
from slurm_viewer.widgets.screens.select_partitions_screen import SelectPartitionScreen
from slurm_viewer.widgets.screens.help_screen import HelpScreen

rich.print('')

# Use in snapshot testing to disable clock in header
SHOW_CLOCK = True

try:
    from slurm_viewer.widgets.plot_widget import PlotWidget
except ImportError:
    PlotWidget = None  # type: ignore

# pylint: enable=wrong-import-position

USE_PRIORITY_WIDGET: Final[bool] = False


class SlurmTabBase(Protocol):
    def copy_to_clipboard(self) -> None:
        ...

    async def timer_update(self) -> None:
        ...


def default_factory(cluster: Cluster) -> SlurmProtocol:
    return Slurm(cluster)


class SlurmViewer(App):
    CSS_PATH = Path(__file__).parent / 'widgets/slurm_viewer.tcss'

    BINDINGS = [
        Binding(key='f1', action='help', description='Help'),
        Binding(key='shift+f1', action='help_panel', description='Help panel'),
        Binding(key='q', action='quit', description='Quit'),
        Binding(key='u', action='user', description='User only'),
        Binding(key='p', action='partitions', description='Select Partitions'),
        Binding(key='f2', action='copy_to_clipboard', description='Copy to clipboard', show=False),
        Binding(key='f3', action='reload_config', description='Reload config', show=False),
        Binding(key='f5', action='refresh', description='Refresh', show=False),
        Binding(key='f12', action='screenshot', description='Screenshot', show=False),
    ]

    config: reactive[Config] = reactive(Config.init, layout=True, always_update=True)

    def __init__(self, factory: Callable[[Cluster], SlurmProtocol] = default_factory) -> None:
        super().__init__()
        self.title = f'{self.__class__.__name__}'  # type: ignore
        if len(self.config.clusters) == 0:
            self.app.notify(title='No clusters defined',
                            message='The settings file does not contain any cluster definitions.', severity='error')
        self.slurms: list[SlurmProtocol] = []
        self._factory = factory

    def compose(self) -> ComposeResult:
        yield Header(show_clock=SHOW_CLOCK)
        with Vertical():
            with TabbedContent(id='cluster_tab'):
                for idx, cluster in enumerate(self.config.clusters):
                    with TabPane(cluster.name, id=f'cluster_tab_{idx}'):
                        slurm = self._factory(cluster)
                        self.slurms.append(slurm)
                        yield from self.compose_tab(slurm)
        yield Footer()

    async def on_mount(self) -> None:
        # Update the tab titles
        for idx, slurm in enumerate(self.slurms):
            name: str | None = await slurm.cluster_name()
            if name is None:
                if len(slurm.cluster().name) > 0:
                    name = slurm.cluster().name
                else:
                    name = platform.node()

            assert name is not None
            self.query_one(TabbedContent).get_tab(f'cluster_tab_{idx}').label = name  # type: ignore

    @staticmethod
    def compose_tab(_slurm: SlurmProtocol) -> Generator[Widget, None, None]:
        with TabbedContent():
            for tab in _slurm.cluster().tabs:
                if tab == Tabs.NODES:
                    with TabPane('Nodes'):
                        yield NodesWidget(_slurm).data_bind(SlurmViewer.config)
                        continue

                if tab == Tabs.JOBS:
                    with TabPane('Jobs'):
                        yield QueueWidget(_slurm).data_bind(SlurmViewer.config)
                        continue

                if tab == Tabs.STATUS:
                    with TabPane('Status'):
                        yield StatusWidget(_slurm).data_bind(SlurmViewer.config)
                        continue

                if tab == Tabs.GPU:
                    if PlotWidget is None:
                        continue

                    with TabPane('GPU usage'):
                        yield PlotWidget(_slurm).data_bind(SlurmViewer.config)
                        continue

    async def action_help(self) -> None:
        await self.app.push_screen(HelpScreen(self.slurms, self.config))

    async def action_help_panel(self) -> None:
        try:
            await self.query_one(HelpPanel).remove()
        except NoMatches:
            await self.mount(HelpPanel())

    async def action_reload_config(self) -> None:
        self.notify('Reloading configuration')
        self.config = Config.init()  # type: ignore

    async def action_refresh(self) -> None:
        active_cluster_tab = self.query_one('#cluster_tab', TabbedContent).active_pane
        assert active_cluster_tab
        pane = active_cluster_tab.query_one(TabbedContent).active_pane
        assert pane

        children = pane.children
        assert len(children) == 1

        await cast(SlurmTabBase, children[0]).timer_update()

    async def action_copy_to_clipboard(self) -> None:
        active_cluster_tab = self.query_one('#cluster_tab', TabbedContent).active_pane
        assert active_cluster_tab
        pane = active_cluster_tab.query_one(TabbedContent).active_pane
        assert pane

        children = pane.children
        assert len(children) == 1

        cast(SlurmTabBase, children[0]).copy_to_clipboard()

    async def action_user(self) -> None:
        self.config.ui.user_only = not self.config.ui.user_only
        self.mutate_reactive(SlurmViewer.config)
        self.notify('User only' if self.config.ui.user_only else 'All users')

    async def action_partitions(self) -> None:
        def _update_partitions(selected: list[str] | None) -> None:
            if selected is None:
                return

            if active_cluster.partitions == selected:
                # selection has not changed, don't update the config to stop updating the widgets.
                return

            for cluster in self.config.clusters:
                if cluster.name == active_cluster.name:
                    cluster.partitions = selected
                    break

            self.mutate_reactive(SlurmViewer.config)

        active_pane = self.query_one('#cluster_tab', TabbedContent).active_pane
        assert active_pane
        nodes = active_pane.query_one(NodesWidget)
        assert nodes

        active_cluster = nodes.slurm.cluster()
        all_partitions = await nodes.slurm.partitions()
        screen = SelectPartitionScreen(all_partitions, active_cluster.partitions)
        await self.push_screen(screen, _update_partitions)


if __name__ == "__main__":
    app = SlurmViewer()
    app.run()

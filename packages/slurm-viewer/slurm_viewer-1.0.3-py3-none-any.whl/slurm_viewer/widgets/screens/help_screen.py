import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from importlib_metadata import PackageNotFoundError
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static, TabbedContent, TabPane, Rule

from slurm_viewer.data.slurm_protocol import SlurmProtocol
from slurm_viewer.data.config import Config
from slurm_viewer.widgets.logo import LkebLogoLarge


class HelpScreen(ModalScreen[None]):
    BINDINGS = [('escape', 'pop_screen')]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
        width: auto;
        height: auto;
        & > VerticalScroll {
            width: 70%;
            height: 70%;
            background: $panel;
        }        
    }
    """

    def __init__(self, slurms: list[SlurmProtocol], config: Config, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._slurms = slurms
        self._config = config

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static(self._create_header_help(), id='header')
            yield Static(Markdown('  \n'.join(
                [
                    '# Contact',
                    ' - Created by [Patrick de Koning](https://www.linkedin.com/in/patrick-de-koning-3b99a22/) and '
                    '[Prerak Mody](https://www.linkedin.com/in/prerakmody/)',
                    ' - Developed at [LKEB](https://lkeb.nl)',
                    ' - Raise issues or feature request on [gitlab](https://gitlab.com/lkeb/slurm_viewer/-/issues)'
                ]
            )))
            yield LkebLogoLarge(id='help_logo')
            yield Rule(line_style='heavy')
            with TabbedContent():
                with TabPane('System'):
                    yield Static('', id='help_system')
                with TabPane('Nodes'):
                    yield Static('', id='help_nodes')
                with TabPane('Jobs'):
                    yield Static('', id='help_jobs')
                with TabPane('GPU'):
                    yield Static('', id='help_gpu')

    async def on_mount(self) -> None:
        self.query_one('#help_system', Static).update(await self._create_system_help())
        self.query_one('#help_nodes', Static).update(self._create_nodes_help())
        self.query_one('#help_jobs', Static).update(self._create_jobs_help())
        self.query_one('#help_gpu', Static).update(self._create_gpu_help())

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    @staticmethod
    def _create_header_help() -> Markdown:
        md = [
            '# SLURM Viewer'
            #, 'View the status of the nodes and job queues in a SLURM cluster.',
            ,
            ' - Using a single terminal command, `slurm-viewer` allows you to view the status of your SLURM cluster '
            '(i.e., nodes and jobs). This command combines information from SLURM commands like '
            '`sinfo`, `scontrol`, `squeue` and `sacct` in a tabular and customizable view. '
            , ' - This application can be run on a cluster itself or any computer that can SSH into a cluster.'
            , ' - slurm-viewer has been tested on SLURM versions from 20.x to 24.x'
            , ' - Press Esc to quit this screen.'
        ]
        return Markdown('  \n'.join(md))

    async def _create_system_help(self) -> Markdown:
        def _module_version(name: str) -> str:
            try:
                return version(name)
            except PackageNotFoundError:
                return 'N/A'

        md = [
            '## Runtime environment',
            '|Package|Version|',
            '|--|--|',
            f'|Config|{self._config.config_file}|',
            f'|Python|{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}|',
            f'|SLURM Viewer|{_module_version("slurm-viewer")}|',
            f'|Textual|{_module_version("textual")}|',
            ' ',
            '## Clusters',
            '|Name|Server(s)|Version|',
            '|---|---|---|'
        ]

        for node in self._slurms:
            md.append(f'|{node.cluster().name}|{", ".join(node.cluster().servers)}|{node.slurm_version()}|')

        return Markdown('  \n'.join(md))

    @staticmethod
    def _create_nodes_help() -> Markdown:
        with (Path(__file__).parent / 'help_nodes.md').open('r', encoding='utf8') as f:
            return Markdown('  \n'.join(f.readlines()))

    @staticmethod
    def _create_jobs_help() -> Markdown:
        with (Path(__file__).parent / 'help_jobs.md').open('r', encoding='utf8') as f:
            return Markdown('  \n'.join(f.readlines()))

    @staticmethod
    def _create_gpu_help() -> Markdown:
        with (Path(__file__).parent / 'help_gpu.md').open('r', encoding='utf8') as f:
            return Markdown('  \n'.join(f.readlines()))

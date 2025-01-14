import csv
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static
from textual_plotext import PlotextPlot

from slurm_viewer.data.config import Config
from slurm_viewer.data.job_model import Job
from slurm_viewer.data.models import SlurmError
from slurm_viewer.data.queue_model import JobStateCodes
from slurm_viewer.data.slurm_protocol import SlurmProtocol
from slurm_viewer.widgets.loading import Loading


def _filter_data(data: list[Job]) -> list[Job]:
    filtered_data = []
    for job in data:
        if job.AllocTRES.gpu is None:
            continue

        if not job.TRESUsageInMax.gpu_mem or not job.TRESUsageInMax.gpu_mem.value:
            continue

        if job.TRESUsageInMax.gpu_mem.GB < 1:
            continue

        if job.Elapsed < timedelta(seconds=60):
            continue

        if job.State != JobStateCodes.COMPLETED:
            continue

        filtered_data.append(job)
    return filtered_data


class PlotWidget(Static):
    DEFAULT_CSS = """
    PlotextPlot {
        border: $foreground 80%;
    }
    """
    CSS_PATH = Path(__file__) / 'slurm_viewer.tcss'

    config: reactive[Config] = reactive(Config, layout=True, always_update=True)

    def __init__(self, _slurm: SlurmProtocol, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.slurm = _slurm
        self.gpu_usage: list[Job] = []
        self.gpu_history = 4  # weeks

    def compose(self) -> ComposeResult:
        with Vertical():
            yield PlotextPlot(id='gpu_mem_plot')
            yield PlotextPlot(id='gpu_util_plot')

    @work
    async def watch_config(self, _: Config, __: Config) -> None:
        with Loading(self):
            try:
                self.gpu_usage = await self.slurm.jobs(self.gpu_history, self.config.ui.user_only)
            except SlurmError as e:
                self.gpu_usage = []
                self.notify(f'{e.cluster.name}, {e.func}', title='Slurm Timeout', severity='error')

            await self.update_plot(self.config.ui.user_only)

    async def copy_to_clipboard(self) -> None:
        with StringIO() as fp:
            data = _filter_data(self.gpu_usage)

            fieldnames = list(data[0].model_dump().keys())
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for node in data:
                writer.writerow(node.model_dump())

            # noinspection PyUnresolvedReferences
            self.app.copy_to_clipboard(fp.getvalue())
            self.app.notify('Copied GPU info to clipboard')

    async def update_plot(self, user_only: bool) -> None:
        if not self.is_mounted:
            return

        data = _filter_data(self.gpu_usage)

        end = date.today()
        start = end - timedelta(weeks=self.gpu_history)
        time_string = f'from {start:%A %d %B} until {end:%A %d %B}'

        gpu_mem_data = [job.TRESUsageInMax.gpu_mem.GB for job in data]  # type: ignore
        plotextplot = self.query_one('#gpu_mem_plot', PlotextPlot)
        plt = plotextplot.plt
        plt.clear_figure()
        bins = 24
        plt.hist(gpu_mem_data, bins)
        plt.title(f'GPU memory histogram {time_string} ({len(gpu_mem_data)} jobs for {"User" if user_only else "All"})')
        plt.xlabel('GPU Mem (GB)')
        plt.ylabel('# jobs')
        plotextplot.refresh()

        gpu_util_data = [job.TRESUsageInMax.gpu_util for job in data]
        plotextplot = self.query_one('#gpu_util_plot', PlotextPlot)
        plt = plotextplot.plt
        plt.clear_figure()
        bins = 25
        plt.hist(gpu_util_data, bins)
        plt.title(f'GPU utilization histogram {time_string} ({len(gpu_util_data)} jobs)')
        plt.xlabel('GPU utilization (%)')
        plt.ylabel('# jobs')
        plotextplot.refresh()

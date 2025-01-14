from __future__ import annotations

import enum
import os
from pathlib import Path
from typing import cast

import tomlkit
import tomlkit.exceptions
from pydantic import BaseModel, field_validator, Field, AliasChoices


def get_config_filename(filename: Path) -> Path:
    if 'SLURM_VIEW_CONFIG' in os.environ:
        filename = Path(os.environ['SLURM_VIEW_CONFIG'])
        if filename.exists():
            return filename

    if filename.exists():
        return filename

    filename = Path.home() / '.config/slurm-viewer/settings.toml'
    if filename.exists():
        return filename

    raise FileNotFoundError('Settings file could not be found. ')


class Tabs(str, enum.Enum):
    NODES = 'nodes'
    JOBS = 'jobs'
    GPU = 'gpu'
    STATUS = 'status'


# noinspection PyDataclass
class Cluster(BaseModel):
    servers: list[str] = Field(default=[], validation_alias=AliasChoices('server', 'servers'))
    name: str = ''
    node_name_ignore_prefix: list[str] = Field(default_factory=list)
    partitions: list[str] = Field(default_factory=list)
    ignore_partitions: list[str] = Field(default_factory=list)
    tabs: list[Tabs] = Field(default=[Tabs.NODES, Tabs.JOBS, Tabs.GPU])

    # TOML doesn't support None, so have to check it here.
    @field_validator('servers', mode='before')
    @classmethod
    def server_validator(cls, value: str | list[str] | None) -> list[str]:
        if value is None or value == 'None':
            return []

        if isinstance(value, str):
            return [value]

        return value


# noinspection PyDataclass
class UiSettings(BaseModel):
    node_columns: list[str] = Field(default_factory=list)
    queue_columns: list[str] = Field(default_factory=list)
    priority_columns: list[str] = Field(default_factory=list)
    auto_refresh: bool = False
    refresh_interval: int = 30  # seconds
    user_only: bool = False


# noinspection PyDataclass
class Config(BaseModel):
    clusters: list[Cluster] = Field(default_factory=list)
    ui: UiSettings = UiSettings()
    _config_file: Path = Path('settings.toml')

    @classmethod
    def init(cls) -> Config:
        cfg: Config | None
        try:
            cfg = Config.load(get_config_filename(Path('settings.toml')))
        except FileNotFoundError:
            cfg = create_default_config()

        if cfg is not None:
            return cfg

        raise RuntimeError('Settings file could not be loaded.')

    @classmethod
    def load(cls, _filename: Path | str) -> Config:
        if not Path(_filename).exists():
            raise FileNotFoundError(f'Settings file "{Path(_filename).absolute().resolve()}" does not exist.')

        try:
            with Path(_filename).open('r', encoding='utf-8') as settings_file:
                toml_content = tomlkit.loads(settings_file.read())
                setting = Config(**cast(dict, toml_content))
        except (tomlkit.exceptions.ParseError, tomlkit.exceptions.UnexpectedCharError) as e:
            raise RuntimeError(f'Error parsing settings file: {_filename}: {e}.') from e

        setting._config_file = Path(_filename).absolute().resolve()
        return setting

    def get_cluster(self, name: str) -> Cluster | None:
        for cluster in self.clusters:
            if cluster.name == name:
                return cluster

        return None

    @property
    def config_file(self) -> Path:
        return self._config_file


def create_default_config() -> Config | None:
    config = Config()
    config.ui.node_columns = [
        "node_name",
        "state",
        "gpu_tot",
        "gpu_alloc",
        "gpu_avail",
        "gpu_type",
        "gpu_mem",
        "cpu_tot",
        "cpu_alloc",
        "cpu_avail",
        "mem_tot",
        "mem_avail",
        "cpu_gpu",
        "mem_gpu",
        "partitions",
        "active_features"
    ]
    config.ui.queue_columns = [
        "user",
        "job_id",
        "reason",
        "exec_host",
        "start_time",
        "submit_time",
        "start_delay",
        "run_time",
        "time_limit",
        "command",
        "work_dir"
    ]
    config.ui.priority_columns = [
        "user_name",
        "job_id",
        "job_priority_n",
        "age_n",
        "fair_share_n",
        "partition_name"
    ]

    # pylint: disable=no-member
    config.clusters.append(Cluster())
    # pylint: enable=no-member

    config_path = Path('~/.config/slurm-viewer/settings.toml').expanduser().resolve()
    config_path.parent.mkdir(exist_ok=True, parents=True)

    if config_path.exists():
        overwrite = input('Config file already exists, overwrite? [Y/n] ')
        if overwrite.lower() == 'n':
            print(f'Skipping config file generation, file already exists: {config_path}')
            return None

    with open(config_path, 'w', encoding='utf-8') as settings_file:
        doc = tomlkit.document()
        ui = tomlkit.table()
        ui.update(**config.ui.model_dump())
        doc['ui'] = ui

        clusters = tomlkit.aot()
        cluster = Cluster().model_dump()
        cluster['servers'] = 'None'
        cluster['tabs'] = ['nodes', 'jobs']
        clusters.append(tomlkit.item(cluster))
        doc['clusters'] = clusters

        tomlkit.dump(doc, settings_file, sort_keys=True)
    print(f'Config file generated: {config_path}')

    return config


if __name__ == '__main__':
    create_default_config()

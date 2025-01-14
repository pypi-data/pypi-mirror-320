from __future__ import annotations

from slurm_viewer.data.config import Cluster


class SlurmError(Exception):
    """ Custom exception for slurm errors. """

    def __init__(self, cluster: Cluster, func: str) -> None:
        self.cluster = cluster
        self.func = func

    def __str__(self) -> str:
        return f'{self.cluster}, {self.func}'

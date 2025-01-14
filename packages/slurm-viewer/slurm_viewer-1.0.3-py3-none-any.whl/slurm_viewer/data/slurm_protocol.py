from __future__ import annotations

from typing import Protocol, Union

from slurm_viewer.data.config import Cluster
from slurm_viewer.data.job_model import Job
from slurm_viewer.data.job_model_v2 import JobModel
from slurm_viewer.data.node_model import Node
from slurm_viewer.data.priority_model import Priority
from slurm_viewer.data.queue_model import Queue


class SlurmProtocol(Protocol):
    async def slurm_version(self) -> str:
        ...

    def disconnect(self) -> None:
        ...

    def cluster(self) -> Cluster:
        ...

    async def cluster_name(self) -> Union[str, None]:
        ...

    async def partitions(self) -> list[str]:
        ...

    async def nodes(self) -> list[Node]:
        ...

    async def queue(self, user_only: bool) -> list[Queue]:
        ...

    async def jobs(self, num_weeks: int, user_only: bool) -> list[Job]:
        ...

    async def current_jobs(self) -> list[JobModel]:
        ...

    async def priority(self) -> list[Priority]:
        ...

    async def users(self, group: str) -> list[str]:
        ...

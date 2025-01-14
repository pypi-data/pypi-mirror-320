from __future__ import annotations

import asyncio
import json
import re
# noinspection PyProtectedMember
from asyncio.subprocess import Process
from dataclasses import dataclass
from socket import gaierror
from typing import Protocol, Union

import asyncssh
import pydantic
from asyncssh import ConnectionLost, ProcessError

import slurm_viewer
import slurm_viewer.data
import slurm_viewer.data.config
from slurm_viewer.data.job_model import Job
from slurm_viewer.data.job_model_v2 import JobModel
from slurm_viewer.data.legacy_text_output_tools import (
    LegacyTextConversionError,
    create_node_info,
    create_queue_info,
)
from slurm_viewer.data.models import SlurmError
from slurm_viewer.data.node_model import Node, create_node
from slurm_viewer.data.priority_model import Priority
from slurm_viewer.data.queue_model import Queue


@dataclass
class ReturnValue:
    return_code: int
    stdout: str
    stderr: str


class SlurmCommProtocol(Protocol):
    """Protocol for Slurm Communication"""

    async def run_command(self, command: str) -> ReturnValue: ...

    def disconnect(self) -> None: ...


class SshCom:
    """SSH implementation for Slurm Communication."""

    def __init__(self, _cluster: slurm_viewer.data.config.Cluster):
        self._cluster = _cluster
        self._connection: asyncssh.SSHClientConnection | None = None
        self._lock = asyncio.Lock()
        self._timeout = 30  # seconds
        self._login_timeout = 5  # seconds
        self._skip = False

    async def _connect(self) -> None:
        async with self._lock:
            if self._skip:
                # Cluster has been unreachable before, skip it for the rest of the runtime.
                self._connection = None
                return

            if self._connection is not None:
                return

            for server in self._cluster.servers:
                try:
                    self._connection = await asyncssh.connect(
                        server, login_timeout=self._login_timeout
                    )
                except (ConnectionLost, gaierror):
                    continue  # Error connecting to server, try the next one.
                break  # Connected to a logon node
            else:
                # None of the servers want to connect, skip this cluster.
                self._skip = True
                self._connection = None
                return

            assert self._connection is not None

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()

    async def run_command(self, command: str) -> ReturnValue:
        await self._connect()

        if self._connection is None:
            return ReturnValue(return_code=1, stdout='', stderr='Skipped this cluster')

        try:
            result = await self._connection.run(
                command, check=True, timeout=self._timeout
            )
        except ProcessError as e:
            return ReturnValue(return_code=1, stdout='', stderr=str(e))

        if (
                not (isinstance(result.stdout, str) and isinstance(result.stderr, str))
                or result.returncode is None
        ):
            raise SlurmError(self._cluster, func=command)

        return ReturnValue(result.returncode, result.stdout, result.stderr)


class LocalCom:
    """Local implementation for Slurm Communication."""

    def __init__(self, _cluster: slurm_viewer.data.config.Cluster):
        self._cluster = _cluster
        self._process: Process | None = None

    def disconnect(self) -> None:
        if self._process:
            self._process.terminate()

    # noinspection PyMethodMayBeStatic
    async def run_command(self, command: str) -> ReturnValue:
        self._process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await self._process.communicate()
        if self._process.returncode is None:
            return ReturnValue(
                return_code=1, stdout=stdout.decode(), stderr=stderr.decode()
            )

        return ReturnValue(self._process.returncode, stdout.decode(), stderr.decode())


class Slurm:
    """Communicate with Slurm via SSH or local."""

    def __init__(self, _cluster: slurm_viewer.data.config.Cluster) -> None:
        self._cluster = _cluster
        self._com: SlurmCommProtocol = self._create_slurm()

    async def slurm_version(self) -> str:
        value = await self._com.run_command('sinfo --version')

        if value.return_code == 0 and (
                m := re.match(r'^slurm (?P<version>.*)$', value.stdout)
        ):
            return m.group('version')

        return ''

    def disconnect(self) -> None:
        self._com.disconnect()

    def cluster(self) -> slurm_viewer.data.config.Cluster:
        return self._cluster

    def _partitions_argument(self) -> str:
        if len(self._cluster.partitions) == 0:
            return ''

        return '--partition ' + ','.join(self._cluster.partitions)

    def _create_slurm(self) -> SlurmCommProtocol:
        if self._cluster.servers is None or len(self._cluster.servers) == 0:
            return LocalCom(self._cluster)

        return SshCom(self._cluster)

    def _extract_json(self, value: ReturnValue) -> dict:
        try:
            if match := re.search(r'\{.*}', value.stdout, re.DOTALL):
                return json.loads(match.group(0))  # type: ignore
            return {}
        except json.JSONDecodeError as e:
            raise SlurmError(cluster=self._cluster, func=f'JSON decode failed, {e}: {value.stdout}') from e

    async def cluster_name(self) -> Union[str, None]:
        cmd = 'sinfo --json'
        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            return None

        data = self._extract_json(value)
        try:
            meta = data['meta']
            if 'Slurm' in meta and 'cluster' in meta['Slurm']:
                return meta['Slurm']['cluster']  # type: ignore
            if 'slurm' in meta and 'cluster' in meta['slurm']:
                return meta['slurm']['cluster']  # type: ignore
        except KeyError:
            pass

        return None

    async def partitions(self) -> list[str]:
        cmd = 'sinfo --format=%R --noheader'

        value = (await self._com.run_command(cmd)).stdout.splitlines()
        for part in self._cluster.ignore_partitions:
            value.remove(part)

        return value

    async def nodes(self) -> list[Node]:
        cmd = 'scontrol --json show nodes'

        value = await self._com.run_command(cmd)

        if value.return_code == 0:
            node_list = []
            data = self._extract_json(value)
            for node_dict in data['nodes']:
                node = create_node(node_dict, self._cluster.node_name_ignore_prefix)
                if node is None:
                    continue
                node_list.append(node)
            return node_list

        # Fallback in case cluster doesn't support json output.
        cmd = 'scontrol --oneliner show nodes'

        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster,
                func=f'scontrol failed, {value.return_code=}: {cmd}',
            )

        nodes = []
        for node_str in value.stdout.splitlines():
            node_info = create_node_info(node_str, self._cluster)
            if node_info is None:
                continue

            nodes.append(node_info)

        return nodes

    async def queue(self, user_only: bool) -> list[Queue]:
        cmd = f'squeue {self._partitions_argument()} --json'

        if user_only:
            cmd += ' --me'

        value = await self._com.run_command(cmd)

        if value.return_code == 0:
            data = self._extract_json(value)
            if data is None:
                return []

            queue_list = []
            for job_dict in data['jobs']:
                job = Queue(**job_dict)
                queue_list.append(job)
            return queue_list

        # Fallback in case cluster doesn't support json output.
        cmd = f'squeue {self._partitions_argument()} --format=%all'

        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster,
                func=f'squeue failed, {value.return_code=}: {cmd}',
            )

        try:
            return create_queue_info(value.stdout.splitlines())  # type: ignore
        except LegacyTextConversionError as e:
            raise SlurmError(cluster=self._cluster, func=f'squeue failed, {e}') from e

    async def jobs(self, num_weeks: int, user_only: bool) -> list[Job]:
        cmd = f'sacct --starttime now-{num_weeks}week --long --parsable2'

        if not user_only:
            cmd += f' --allusers {self._partitions_argument()}'

        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster, func=f'sacct failed, {value.return_code=}: {cmd}'
            )

        lines = value.stdout.splitlines()

        if len(lines) == 0:
            return []

        header = lines[0].rstrip().split('|')
        try:
            return [Job(**dict(zip(header, x.rstrip().split('|')))) for x in lines[1:]]
        except pydantic.ValidationError as e:
            raise SlurmError(cluster=self._cluster, func=str(e)) from e

    async def current_jobs(self) -> list[JobModel]:
        cmd = 'sacct --allusers --json'
        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster, func=f'sacct failed, {value.return_code=}: {cmd}'
            )

        data = self._extract_json(value)
        if data is None:
            return []
        return [JobModel(**job_dict) for job_dict in data['nodes']]

    async def priority(self) -> list[Priority]:
        partitions = ','.join(self._cluster.partitions)
        cmd = f'"sprio --partition={partitions}"'

        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster, func=f'sprio failed, {value.return_code=}: {cmd}'
            )

        # noinspection PyUnresolvedReferences
        header = list(Priority.model_fields.keys())

        lines = value.stdout.splitlines()
        if len(lines) == 0:
            return []

        result = []
        for line in lines[1:]:  # skip the first row (it's the header)
            result.append(Priority(**dict(zip(header, line.rstrip().split('|')))))

        return result

    async def users(self, group: str) -> list[str]:
        cmd = f'getent group {group}'

        value = await self._com.run_command(cmd)

        if value.return_code != 0:
            raise SlurmError(
                cluster=self._cluster,
                func=f'getent failed, {value.return_code=}: {cmd}',
            )

        return sorted(value.stdout.rsplit(':', maxsplit=1)[-1].split(','))

""" Pydantic model for capturing SLURM node information. """
from __future__ import annotations

import datetime
import re
from collections.abc import Iterator
from enum import Enum
from typing import Any

import dateutil.parser
from pydantic import BaseModel, Field, AliasChoices, field_validator, computed_field, ConfigDict

from slurm_viewer.data.common_types import MemoryUsed

# Examples to parse:
#  - 'cpu=72,mem=468000M,gres/cpu=72,gres/gpu=4,gres/gpu:a100=4'
#  - 'cpu=10,mem=190000M,gres/gpu=2,gres/gpu:rtx6000=2'
#  - 'cpu=45,mem=420G,gres/cpu=72,gres/gpu=3,gres/gpu:a100_3g.20gb=3'
#  - 'cpu=24,mem=48G,gres/gpu=3'
#  - 'cpu=38,mem=252032M,gres/gpu=3,gres/gpu:3g.40gb=2,gres/gpu:4g.40gb=1'
#  - 'cpu=26,mem=224928M,gres/gpu=3'
#  - 'cpu=72,mem=264G,gres/gpu:a100=2'
#  - 'cpu=256,mem=490000M,gres/gpu:a100=4,gres/nvme=3500'
#  - 'cpu=76,mem=166072M,gres/gpu:a100=2,gres/gpu:a100_1g.5gb=2,gres/nvme=100'
ALLOCTRESS_RE = re.compile(
    r'(?:cpu=(?P<cpu>\d+),)?'
    r'(?:mem=(?P<mem>\d+(\.\d+)?[MG]),)?'
    r'(?:gres/cpu=\d+,)?'
    r'(?:gres/gpu=(?P<gpu_total>\d+))?'
    r'(?:gres/gpu:(?P<gpu_type>[\w.]+)=\d+)?'
)

# Examples to parse:
#  - 'cpu=16,mem=250G,billing=16,gres/gpu=3'
#  - 'cpu=72,mem=480G,billing=512,gres/cpu=72,gres/gpu=4,gres/gpu:a100=4'
#  - 'cpu=24,mem=381596M,billing=125,gres/gpu=4'
#  - 'cpu=64,mem=252619M,billing=133,gres/gpu=4,gres/gpu:3g.40gb=2,gres/gpu:4g.40gb=2'
#  - 'cpu=256,mem=490000M,billing=256,gres/gpu:a100=2,gres/gpu:a100_1g.5gb=14,gres/nvme=3500'
#  - 'cpu=256,mem=490000M,billing=256,gres/gpu:a100=4,gres/nvme=3500'
#  - 'cpu=256,mem=490000M,billing=256,gres/gpu:a100=2,gres/gpu:a100_1g.5gb=14,gres/nvme=3500'
#  - 'cpu=12,mem=187.50G,billing=12,gres/gpu=2'
CFGTRESS_RE = re.compile(
    r'(?:cpu=(?P<cpu>\d+),)?'
    r'(?:mem=(?P<mem>\d+(\.\d+)?[MG]),)?'
    r'(?:billing=(?P<billing>\d+),)?'
    r'(?:gres/cpu=\d+,)?'
    r'(?:gres/gpu=(?P<gpu_total>\d+))?'
    r'(?:gres/gpu:(?P<gpu_type>[\w.]+)=\d+)?'
)


class TresResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cpu: int | None = None
    mem: MemoryUsed | None = None
    billing: int | None = None
    gpu_total: int | None = None
    gpu_type: list[GPU] | None = None


def parse_tres(pattern: re.Pattern, _value: str) -> TresResult:
    def _value_str(_name: str) -> str | None:
        if _name in match.groupdict().keys() and match.group(_name) is not None:
            return match.group(_name)
        return None

    def _value_int(_name: str) -> int | None:
        val = _value_str(_name)
        if val is not None:
            try:
                return int(val)
            except TypeError:
                pass

        return None

    def _value_mem(_name: str) -> MemoryUsed | None:
        val = _value_str(_name)
        if val is not None:
            try:
                return MemoryUsed(val)
            except TypeError:
                pass

        return None

    result = TresResult()

    gpu_types = {}
    total_gpus_v1 = 0  # from gpu_total
    total_gpus_v2 = 0  # sum from gpu_type

    matches: Iterator[re.Match[str]] = pattern.finditer(_value)
    value: int | MemoryUsed | None
    for match in matches:
        if value := _value_int('cpu'):
            result.cpu = value
        if value := _value_mem('mem'):
            result.mem = value
        if value := _value_int('billing'):
            result.billing = value
        if value := _value_int('gpu_total'):
            total_gpus_v1 += value

        if 'gpu_type' in match.groupdict().keys() and match.group('gpu_type') is not None:
            gpu_type = match.group('gpu_type')
            gpu_count = int(_value.split(f'gres/gpu:{gpu_type}=')[1].split(',')[0])
            gpu_types[gpu_type] = gpu_count
            total_gpus_v2 += gpu_count

    result.gpu_total = total_gpus_v1 if total_gpus_v1 > 0 else total_gpus_v2

    if gpu_types:
        result.gpu_type = [GPU(name=k, amount=v) for k, v in gpu_types.items()]

    return result


class State(Enum):
    """ Node state """
    IDLE = 'IDLE'
    DOWN = 'DOWN'
    MIXED = 'MIXED'
    ALLOCATED = 'ALLOCATED'
    DRAIN = 'DRAIN'
    MAINTENANCE = 'MAINTENANCE'
    RESERVED = 'RESERVED'
    NOT_RESPONDING = 'NOT_RESPONDING'
    PLANNED = 'PLANNED'
    COMPLETING = 'COMPLETING'
    REBOOT_REQUESTED = 'REBOOT_REQUESTED'
    INVALID_REG = 'INVALID_REG'
    UNKNOWN = 'UNKNOWN'


class CfgTRES(BaseModel):
    """ Configured Trackable Resources """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cpu: int | None = None
    mem: MemoryUsed | None = None
    billing: int | None = None
    gpu: int | None = None


class AllocTRES(BaseModel):
    """ Allocated Trackable Resources """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cpu: int | None = None
    mem: MemoryUsed | None = None
    gpu_alloc: int | None = None
    gpu_type: list[GPU] | None = None
    gpu_total: int | None = None


class GPU(BaseModel):
    """ GPU name and count. """
    name: str
    amount: int

    def __str__(self) -> str:
        return f'{self.name}:{self.amount}'


def gpu_mem_from_features(_features: list[str]) -> MemoryUsed | None:
    """ Get the GPU memory from features. """
    for feature in _features:
        m = re.search(r'^.*.(?P<gpu_mem>\d{2,})[Gg]\w*$', feature)
        if m is None:
            continue

        try:
            return MemoryUsed.from_mb(int(m['gpu_mem']) * 1024)
        except ValueError:
            return None

    return None


# See https://github.com/python/mypy/issues/1362
# mypy: disable-error-code="operator, no-any-return"
# pylint: disable=comparison-with-callable,unsupported-membership-test
class Node(BaseModel):
    """ Slurm node model. """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    active_features: list[str] = Field(default_factory=list)
    alloc_tres: AllocTRES = Field(validation_alias=AliasChoices('alloc_tres', 'tres_used'), default=AllocTRES())
    arch: str = Field(validation_alias=AliasChoices('arch', 'architecture'), default='N/A')
    available_features: list[str] = Field(validation_alias=AliasChoices('available_features', 'features'),
                                          default_factory=list)
    boards: int | None = None
    boot_time: datetime.datetime | None = None
    cfgtres: CfgTRES = Field(validation_alias=AliasChoices('cfgtres', 'tres'), default=CfgTRES())
    cores_per_socket: int = Field(validation_alias=AliasChoices('cores_per_socket', 'cores'), default=-1)
    cpu_alloc: int = Field(validation_alias=AliasChoices('cpu_alloc', 'alloc_cpus'), default=-1)
    cpu_efctv: int | None = Field(validation_alias=AliasChoices('cpu_efctv', 'effective_cpus'), default=None)
    cpu_tot: int = Field(validation_alias=AliasChoices('cpu_tot', 'cpus'), default=-1)
    cpuload: float = Field(validation_alias=AliasChoices('cpuload', 'cpu_load'), default=-1.0)
    gres: list[GPU] = Field(default_factory=list)
    gres_used: list[GPU] = Field(default_factory=list)
    last_busy_time: datetime.datetime | None = Field(validation_alias=AliasChoices('last_busy_time', 'last_busy'),
                                                     default=None)
    mcs_label: str = 'N/A'
    mem_alloc: MemoryUsed = Field(validation_alias=AliasChoices('alloc_mem', 'alloc_memory'), default=MemoryUsed())
    # mem_avail: MemoryUsed = Field(validation_alias=AliasChoices('freemem', 'free_mem'), default=MemoryUsed())
    mem_tot: MemoryUsed = Field(validation_alias=AliasChoices('realmemory', 'real_memory'), default=MemoryUsed())
    node_addr: str = Field(validation_alias=AliasChoices('node_addr', 'address'), default='N/A')
    node_hostname: str = Field(validation_alias=AliasChoices('node_hostname', 'hostname'), default='N/A')
    node_name: str = Field(validation_alias=AliasChoices('node_name', 'name'), repr=True, default='N/A')
    os: str = Field(validation_alias=AliasChoices('os', 'operating_system'), default='N/A')
    owner: str | None = None
    partitions: list[str] = Field(default_factory=list)
    resume_after_time: datetime.datetime | None = Field(validation_alias=AliasChoices('resume_after_time', 'resume_after'),
                                                        default=None)
    slurmd_start_time: datetime.datetime | None = None
    sockets: int = -1
    states: list[State] = Field(alias='state', default_factory=list, description='State of the node.')
    threads_per_core: int = Field(validation_alias=AliasChoices('threads_per_core', 'threads'), default=-1)
    tmp_disk: MemoryUsed = Field(validation_alias=AliasChoices('tmp_disk', 'temporary_disk'), default=MemoryUsed())
    version: str | None = None
    weight: int = -1

    @computed_field(description='Available CPU cores.')
    def cpu_avail(self) -> int:
        if getattr(self, 'cpu_tot', None) is None or getattr(self, 'cpu_alloc', None) is None:
            return -1
        return self.cpu_tot - self.cpu_alloc

    @computed_field(description='Available Memory.')
    def mem_avail(self) -> MemoryUsed:
        if getattr(self, 'mem_tot', None) is None or getattr(self, 'mem_alloc', None) is None:
            return MemoryUsed(None)
        return self.mem_tot - self.mem_alloc

    @computed_field(description='Total GPUs.')
    def gpu_tot(self) -> int:
        return sum(x.amount for x in self.gres)

    @computed_field(description='Allocated GPUs.')
    def gpu_alloc(self) -> int:
        if self.alloc_tres.gpu_alloc is not None:
            return self.alloc_tres.gpu_alloc

        if len(self.gres_used) > 0:
            return sum(x.amount for x in self.gres_used)

        return 0

    @computed_field(description='Available GPUs.')
    def gpu_avail(self) -> int:
        if self.gres and self.gpu_tot is not None and self.gpu_alloc is not None:
            return self.gpu_tot - self.gpu_alloc
        return 0

    @computed_field(description='GPU type.')
    def gpu_type(self) -> str:
        return ','.join(sorted({x.name for x in self.gres}))

    # pylint: disable=too-many-return-statements
    @computed_field(description='Amount of GPU memory (GB)')
    def gpu_mem(self) -> MemoryUsed:
        mem = gpu_mem_from_features(self.available_features)
        if mem is not None:
            return mem

        # Detect Nvidia Multi-Instance GPU (MIG)
        gpu_re = re.compile(r'(?P<name>.*)_\dg.(?P<mem>\d+)gb')
        # noinspection PyTypeChecker
        if m := gpu_re.match(self.gpu_type):  # type: ignore
            return MemoryUsed.from_mb(int(m.group('mem')) * 1024)

        # Some hard coded values
        if 'a100' == self.gpu_type:
            # Could be 40Gb or 80Gb
            return MemoryUsed.from_mb(80 * 1024)

        if 'h100' == self.gpu_type:
            return MemoryUsed.from_mb(80 * 1024)

        if '2080' in self.gpu_type:
            return MemoryUsed.from_mb(11 * 1024)

        if 'tesla_t4' == self.gpu_type:
            return MemoryUsed.from_mb(16 * 1024)

        return MemoryUsed(None)

    # pylint: enable=too-many-return-statements

    @computed_field(description='Number of available CPUs divided by the number of available GPUs.')
    def cpu_gpu(self) -> float | str:
        if self.gpu_avail == 0:
            return '-'
        return self.cpu_avail / self.gpu_avail

    @computed_field(description='Available CPU memory divided by the number of available GPUs.')
    def mem_gpu(self) -> float | str:
        if self.gpu_avail == 0:
            return '-'
        # noinspection PyTypeChecker
        return self.mem_avail.GB / self.gpu_avail  # type: ignore

    @computed_field(description='State of the node as a string.')
    def state(self) -> str:
        return ','.join([x.name.lower() for x in self.states])

    @field_validator('resume_after_time', 'boot_time', 'last_busy_time', 'slurmd_start_time', mode='before')
    @classmethod
    def date_validator(cls, value: Any) -> datetime.datetime | None:
        if value is None:
            return None

        if isinstance(value, dict):
            return datetime.datetime.fromtimestamp(value['number'])

        if isinstance(value, int):
            return datetime.datetime.fromtimestamp(value)

        if not isinstance(value, datetime.datetime) and len(value) > 0:
            return None

        # noinspection PyTypeChecker
        return dateutil.parser.parse(value)

    @field_validator('available_features', 'active_features', 'partitions', mode='before')
    @classmethod
    def list_validator(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return value.split(',')

    @field_validator('gres', 'gres_used', mode='before')
    @classmethod
    def gres_validator(cls, _value: str) -> list[GPU]:
        """
        Parameters
        ----------
        _value : str
            The string to parse
             - cpu:192
             - gpu:RTX6000:3
             - gpu:a100:4(S:0-1),cpu:72
             - gpu:a100_3g.20gb:8(S:0-1),cpu:72
             - gpu:a100:4(S:0-1),nvme:3500
             - a100_4g:2,a100_3g:2
        """

        if len(_value) == 0:
            return []

        if ',' in _value:
            values = _value.split(',')
        else:
            values = [_value]

        gpus = []
        for value in values:
            data = value.split(':')
            if len(data) < 3:
                continue

            name = data[1]
            try:
                num_gpus = int(re.split(r'\D+', data[2])[0])
            except ValueError:
                num_gpus = 0

            # Dirty fix for Alice
            if '4g.40gb' in name:
                name = 'a100_4g'
            if '3g.40gb' in name:
                name = 'a100_3g'
            if name == '1(S':
                name = 'tesla_t4'
                num_gpus = 1
            # End

            gpus.append(GPU(name=name, amount=num_gpus))
        return gpus

    @field_validator('cfgtres', mode='before')
    @classmethod
    def cfgtres_validator(cls, value: str) -> CfgTRES:
        result = parse_tres(CFGTRESS_RE, value)
        return CfgTRES(**result.model_dump())

    @field_validator('alloc_tres', mode='before')
    @classmethod
    def alloctres_validator(cls, value: str | None) -> AllocTRES:
        if value is None:
            return AllocTRES()

        result = parse_tres(ALLOCTRESS_RE, value)
        return AllocTRES(**result.model_dump())

    @field_validator('states', mode='before')
    @classmethod
    def state_validator(cls, value: str | list[str]) -> list[State]:
        def _create_states(_value: list[str]) -> list[State]:
            _states = []
            for x in _value:
                try:
                    _states.append(State(x))
                except ValueError:
                    pass
            return _states

        if isinstance(value, list):
            return _create_states(value)

        return _create_states(value.split('+'))

    @field_validator('cpuload', mode='before')
    @classmethod
    def cpuload_validator(cls, value: str | dict) -> float:
        if isinstance(value, (int, str)):
            return float(value)

        return float(value['number'])

    @field_validator('mem_avail', 'mem_alloc', 'mem_tot', 'tmp_disk', mode='before')
    @classmethod
    def mem_validator(cls, value: str | int | dict) -> MemoryUsed:
        if isinstance(value, int) or isinstance(value, str):  # pylint: disable=consider-merging-isinstance
            return MemoryUsed.from_mb(int(value))

        return MemoryUsed.from_mb(value['number'])


def create_node(_node_dict: dict, _node_name_ignore_prefix: list[str]) -> Node:
    node = Node(**_node_dict)
    for ignore_prefix in _node_name_ignore_prefix:
        if node.node_name.startswith(ignore_prefix):
            node.node_name = node.node_name.removeprefix(ignore_prefix)
            break
    return node

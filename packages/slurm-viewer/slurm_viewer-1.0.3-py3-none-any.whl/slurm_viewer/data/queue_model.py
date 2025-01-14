""" Pydantic model for capturing SLURM queue information. """
from __future__ import annotations

import datetime
import json
import math
import re
from enum import Enum

import dateutil.parser
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, computed_field

from slurm_viewer.data.common_types import CPU_TIME_RE, Number


class JobStateCodes(Enum):
    """ Job state codes. """
    BOOT_FAIL = 'BOOT_FAIL'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    COMPLETING = 'COMPLETING'
    DEADLINE = 'DEADLINE'
    FAILED = 'FAILED'
    NODE_FAIL = 'NODE_FAIL'
    OUT_OF_MEMORY = 'OUT_OF_MEMORY'
    PENDING = 'PENDING'
    PREEMPTED = 'PREEMPTED'
    RUNNING = 'RUNNING'
    REQUEUED = 'REQUEUED'
    RESIZING = 'RESIZING'
    REVOKED = 'REVOKED'
    SUSPENDED = 'SUSPENDED'
    TIMEOUT = 'TIMEOUT'
    UPDATE_DB = 'UPDATE_DB'


# See https://github.com/python/mypy/issues/1362
# mypy: disable-error-code="operator, no-any-return"
# pylint: disable=comparison-with-callable,unsupported-membership-test
class Queue(BaseModel):
    """ Slurm queue model. """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # min_memory: MemoryUsed
    # nodelist_reason: str
    # reservation: str
    # s_c_t: str
    # time: datetime.datetime
    # uid: int | Number
    account: str | None = None
    accrue_time: datetime.datetime | None = None
    admin_comment: str | None = None
    allocating_node: str | None = None
    array_job_id: int | Number | None = None
    array_task_id: str | int | Number | None = None
    array_max_tasks: Number | int | None = None
    array_task_string: str | None = None
    association_id: int | None = None
    batch_features: str | None = None
    batch_flag: bool | None = None
    batch_host: str | None = None
    flags: list[str] | None = None
    burst_buffer: str | None = None
    burst_buffer_state: str | None = None
    cluster: str | None = None
    cluster_features: str | None = None
    command: str | None = None
    comment: str | None = None
    container: str | None = None
    container_id: str | None = None
    contiguous: int | bool = 0
    core_spec: str | int | None = None
    cores_per_socket: str | Number | None = None
    cpus_per_task: Number | None = None
    cpu_frequency_minimum: Number | None = None
    cpu_frequency_maximum: Number | None = None
    cpu_frequency_governor: Number | None = None
    cpus: int | Number | None = None
    cron: str | None = None
    deadline: Number | None = None
    delay_boot: Number | int | None = None
    dependency: str | None = None
    derived_exit_code: Number | None = None
    eligible_time: datetime.datetime | None = None
    end_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    excluded_nodes: str | None = None
    exit_code: Number | None = None
    extra: str | None = None
    exec_host: str = Field(validation_alias=AliasChoices('exec_host', 'batch_host'), default='N/A')
    failed_node: str | None = None
    features: str | None = None
    federation_origin: str | None = None
    federation_siblings_active: str | None = None
    federation_siblings_viable: str | None = None
    gres_detail: list[str] | None = None
    group: str | None = Field(validation_alias=AliasChoices('group', 'group_name'), default='N/A')
    group_id: int | None = None
    het_job_id: Number | int | None = None
    het_job_id_set: str | None = None
    het_job_offset: Number | int | None = None
    job_id: int | None = None
    job_resources: str | None = None
    job_size_str: list[str] | None = None
    last_scheduled_evaluation: datetime.datetime | None = None
    licenses: str | None = None
    mail_user: str | None = None
    max_cpus: Number | int | None = None
    max_nodes: Number | int | None = None
    mcs_label: str | None = None
    memory_per_tres: str | None = None
    min_cpu: int | Number = Field(validation_alias=AliasChoices('min_cpus', 'min_cpu', 'minimum_cpus_per_node'),
                                  default=Number())
    min_tmp_disk: int | Number = Field(validation_alias=AliasChoices('min_tmp_disk', 'minimum_tmp_disk_per_node'),
                                       default=Number())
    name: str = 'N/A'
    nice: int | None = None
    nodelist: str = Field(validation_alias=AliasChoices('nodelist', 'required_nodes'), default='N/A')
    # 'nodes' is used in both txt and json format but with different meanings, so look for the JSON name first
    nodes: int | Number = Field(validation_alias=AliasChoices('node_count', 'nodes'), default=Number())
    over_subscribe: str | bool = Field(validation_alias=AliasChoices('over_subscribe', 'oversubscribe'), default='N/A')
    partition: str = 'N/A'
    priority: float | Number = Number()
    qos: str = 'N/A'
    reason: str = Field(validation_alias=AliasChoices('reason', 'state_reason'), default='N/A')
    req_nodes: str = Field(validation_alias=AliasChoices('req_nodes', 'required_nodes'), default='N/A')
    scheduled_nodes: str | None = Field(validation_alias=AliasChoices('schednodes', 'scheduled_nodes'), default=None)
    sockets_per_node: str | Number | None = None
    st: str = Field(validation_alias=AliasChoices('st', 'state_description'), default='N/A')
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    # noinspection PyDataclass
    states: list[JobStateCodes] = Field(validation_alias=AliasChoices('state', 'job_state'), default_factory=list,
                                        description='State of the job.')
    submit_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    threads_per_core: str | None| Number = None
    time_left: datetime.timedelta | None = None
    time_limit: datetime.timedelta | None = None
    tres_per_node: str = 'N/A'
    user: str = Field(validation_alias=AliasChoices('user', 'user_name'), default='N/A')
    wc_key: str | None = Field(validation_alias=AliasChoices('wc_key', 'wckey'), default=None)
    work_dir: str = Field(validation_alias=AliasChoices('work_dir', 'work', 'current_working_directory'), default='N/A')

    @computed_field(description='Delay between submitting the job and starting the job.')
    def start_delay(self) -> datetime.timedelta:
        if not hasattr(self, 'states'):
            return datetime.timedelta(seconds=-1)

        if JobStateCodes.RUNNING in self.states:
            return self.start_time - self.submit_time

        return datetime.timedelta(seconds=math.ceil((datetime.datetime.now() - self.submit_time).total_seconds()))

    @computed_field(description='How long has the job been running.')
    def run_time(self) -> datetime.timedelta:
        if JobStateCodes.RUNNING in self.states:
            # only report full seconds.
            return datetime.timedelta(seconds=math.ceil((datetime.datetime.now() - self.start_time).total_seconds()))
        return datetime.timedelta(0)

    @field_validator('states', mode='before')
    @classmethod
    def state_validator(cls, value: str | list) -> list[JobStateCodes]:
        if isinstance(value, str):
            return [JobStateCodes(x) for x in value.split()]

        return [JobStateCodes(x) for x in value]

    @field_validator('job_resources', mode='before')
    @classmethod
    def job_resources_validator(cls, value: str | dict) -> str:
        if isinstance(value, str):
            return value

        return json.dumps(value)

    @field_validator('deadline', mode='before')
    @classmethod
    def deadline_validator(cls, value: int | dict) -> Number:
        if isinstance(value, int):
            return Number(set=True, infinite=False, number=value)

        return Number(**value)

    @field_validator('derived_exit_code', 'exit_code', mode='before')
    @classmethod
    def exit_code_validator(cls, value: int | dict) -> Number | None:
        if isinstance(value, int):
            return Number(set=True, infinite=False, number=value)

        if 'return_code' in value:
            return Number(**value['return_code'])

        return Number(**value)

    @field_validator('qos', mode='before')
    @classmethod
    def qos_validator(cls, value: str | None) -> str:
        if value is None or not isinstance(value, str):
            return 'N/A'

        return value


    @field_validator('time_limit', 'time_left', mode='before')
    @classmethod
    def timedelta_validator(cls, value: str | dict) -> datetime.timedelta:
        # Parse the JSON output
        if isinstance(value, dict):
            num = Number(**value)
            return datetime.timedelta(minutes=num.number)

        # Parse the text output to extract the time
        try:
            m = re.search(CPU_TIME_RE, value)
            # if the regex did not match return 0
            if not m:
                return datetime.timedelta(0)
        except TypeError:
            return datetime.timedelta(0)

        # Create a timedelta object from the named groups in the regex
        return datetime.timedelta(**{k: float(v) for k, v in m.groupdict().items() if v is not None})

    @field_validator('submit_time', 'start_time', 'end_time', 'last_scheduled_evaluation', 'eligible_time', 'accrue_time',
                     mode='before')
    @classmethod
    def datetime_validator(cls, value: str | int) -> datetime.datetime:
        if value is None:
            return datetime.datetime(year=1970, month=1, day=1)

        if isinstance(value, datetime.datetime):
            return value

        if isinstance(value, dict):
            return datetime.datetime.fromtimestamp(value['number'])

        if isinstance(value, int):
            return datetime.datetime.fromtimestamp(value)

        try:
            # noinspection PyTypeChecker
            return dateutil.parser.parse(value)
        except ValueError:
            return datetime.datetime(year=1970, month=1, day=2)

    @computed_field(description='State of the node as a string.')
    def state(self) -> str:
        return ','.join([x.name.lower() for x in self.states])

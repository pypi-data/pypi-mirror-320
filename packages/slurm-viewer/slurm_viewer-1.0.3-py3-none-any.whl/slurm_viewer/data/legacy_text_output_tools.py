from __future__ import annotations

import re

from pydantic import ValidationError

from slurm_viewer.data.config import Cluster
from slurm_viewer.data.queue_model import Queue
from slurm_viewer.data.node_model import Node, create_node

NODE_RE = (r'^NodeName=(?P<node_name>.+?)\s+Arch=(?P<arch>.+?)\s+CoresPerSocket=(?P<cores_per_socket>\d+)\s+CPUAlloc=('
           r'?P<cpu_alloc>\d+)\s+(CPUEfctv=(?P<cpu_efctv>\d+)\s+)?CPUTot=(?P<cpu_tot>\d+)\s+CPULoad=('
           r'?P<cpuload>\d+\.\d+)\s+AvailableFeatures=(?P<available_features>.+?)\s+ActiveFeatures=('
           r'?P<active_features>.+?)\s+Gres=(?P<gres>.+?)\s+NodeAddr=(?P<node_addr>.+?)\s+NodeHostName=('
           r'?P<node_hostname>.+?)\s+Version=(?P<version>.+?)\s+OS=(?P<os>.+?)\s+RealMemory=('
           r'?P<real_memory>\d+)\s+AllocMem=(?P<alloc_mem>\d+)\s+FreeMem=(?P<freemem>\d+)\s+Sockets=('
           r'?P<sockets>\d+)\s+Boards=(?P<boards>\d+)\s+State=(?P<state>.+?)\s+ThreadsPerCore=('
           r'?P<threads_per_core>\d+)\s+TmpDisk=(?P<tmp_disk>\d+)\s+Weight=(?P<weight>.+?)\s+Owner=('
           r'?P<owner>.+?)\s+MCS_label=(?P<mcs_label>.+?)\s+Partitions=(?P<partitions>.+?)\s+BootTime=('
           r'?P<boot_time>.+?)\s+SlurmdStartTime=(?P<slurmd_start_time>.+?)\s+LastBusyTime=(?P<last_busy_time>.+?)\s+('
           r'ResumeAfterTime=(?P<resume_after_time>.+?)\s+)?CfgTRES=(?P<cfgtres>.+?)\s+AllocTRES=(?P<alloc_tres>.+?)\s+')


class LegacyTextConversionError(RuntimeError):
    ...


def create_node_info(node_str: str, cluster: Cluster) -> Node | None:
    m = re.search(NODE_RE, node_str)
    if not m:
        return None

    return create_node(m.groupdict(), cluster.node_name_ignore_prefix)


def create_queue_info(lines: list[str]) -> list[Queue]:
    def _create_queue(_data: str, _header: list[str]) -> Queue | None:
        txt = _data.split('|')
        queue = dict(zip(_header, txt))
        return Queue(**queue)

    result = []
    header = [x.casefold() for x in lines[0].rstrip().split('|')]
    parsing_errors = []
    for x in lines[1:]:
        try:
            val = _create_queue(x.rstrip(), header)

            if val is None:
                continue

            result.append(val)
        except ValidationError:
            parsing_errors.append(x.rstrip())

    if len(parsing_errors) > 0:
        raise LegacyTextConversionError('\n'.join(parsing_errors))

    return result

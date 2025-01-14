from __future__ import annotations

from pydantic import BaseModel


class Priority(BaseModel):
    age_n: float
    age_w: float
    association_n: float
    association_w: float
    cluster_name: str
    fair_share_n: float
    fair_share_w: float
    job_id: int
    job_size_n: float
    job_size_w: float
    qos_name: str
    nice_adjustment: float
    account_name: str
    partition_n: float
    partition_w: float
    qos_n: float
    qos_w: float
    partition_name: str
    admin_w: float
    tres_n: str
    tres_w: str
    user_name: str
    job_priority_n: float
    job_priority_w: float

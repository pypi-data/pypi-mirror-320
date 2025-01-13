import typing

import pydantic

from truestate.datasets.types import DatasetConfig
from truestate.jobs.types import JobType


class DataTransformConfig(pydantic.BaseModel):
    job_type: typing.Literal[JobType.DataTransform] = JobType.DataTransform
    query_type: str = "sql"
    query: str
    input_datasets: list[DatasetConfig]
    output_datasets: list[DatasetConfig]

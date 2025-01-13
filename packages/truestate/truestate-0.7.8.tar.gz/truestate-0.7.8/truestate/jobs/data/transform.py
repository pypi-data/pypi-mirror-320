import typing

from truestate.datasets.dataset import Dataset
from truestate.datasets.types import DatasetConfig
from truestate.jobs.data.types import DataTransformConfig
from truestate.jobs.job import Job
from truestate.jobs.types import JobType
from truestate.jobs.utils import parse_data


class DataTransform(Job):
    def __init__(
        self,
        input_datasets: typing.Union[
            str,
            Dataset,
            typing.List[typing.Union[Dataset, str]],
        ],
        output_datasets: typing.Union[
            str,
            Dataset,
            typing.List[typing.Union[Dataset, str]],
        ],
        query: str,
        name=None,
        description=None,
    ) -> None:
        if not name or len(name) == 0:
            raise ValueError("Please define a name for your data transform job")

        if not description or len(description) == 0:
            raise ValueError("Please define a description for your data transform job")

        super().__init__(
            JobType.DataTransform, name, description, input_datasets, output_datasets
        )

        if not query or len(query) == 0:
            raise ValueError("Please define a query for your data transform job")
        else:
            self.query = query

    def params(self) -> dict:
        params = DataTransformConfig(
            input_datasets=self._parse_inputs(),
            output_datasets=self._parse_outputs(),
            query=self.query,
        )

        return params.model_dump()

    def _parse_inputs(self) -> typing.List[DatasetConfig]:
        parsed = parse_data(self.inputs)
        print(parsed)
        return parsed

    def _parse_outputs(self) -> typing.List[DatasetConfig]:
        return parse_data(self.outputs)

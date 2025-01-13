import re
import typing

from truestate.datasets.dataset import Dataset
from truestate.datasets.types import DatasetConfig


def parse_data(
    data: typing.Union[
        str,
        Dataset,
        typing.List[typing.Union[Dataset, str]],
    ],
) -> typing.List[Dataset]:
    # unified function for parsing inputs or outputs

    if isinstance(data, str):
        return [
            DatasetConfig(
                name=validate_dataset_name(data),
                description="",
            )
        ]

    elif isinstance(data, Dataset):
        return [DatasetConfig(name=data.name, description=data.description)]

    elif isinstance(data, typing.List):
        datasets = []
        for item in data:
            if isinstance(item, Dataset):
                datasets.append(
                    DatasetConfig(name=item.name, description=item.description)
                )
            elif isinstance(item, str):
                datasets.append(
                    DatasetConfig(name=validate_dataset_name(item), description="")
                )
            else:
                raise ValueError(
                    f"Invalid input type in list : {type(item)}, expected Dataset or str"
                )

        return datasets

    else:
        raise ValueError(
            f"Invalid input type : {type(data)}, expected str, Dataset, or List[Dataset | str]"
        )


def validate_dataset_name(dataset_name: str) -> bool:
    pattern = r"^[a-zA-Z][a-zA-Z0-9_]*$"
    if bool(re.match(pattern, dataset_name)):
        return dataset_name
    else:
        raise Exception(
            f"Invalid dataset name: {dataset_name}. Dataset names must start with a letter and contain only letters, numbers and underscores."
        )

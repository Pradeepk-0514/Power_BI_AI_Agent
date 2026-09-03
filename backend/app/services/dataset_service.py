from uuid import uuid4


class DatasetService:

    def __init__(self):
        self.datasets = {}

    def register_dataset(
        self,
        filename: str,
        file_path: str
    ) -> dict:

        dataset_id = str(uuid4())

        dataset = {
            "dataset_id": dataset_id,
            "filename": filename,
            "file_path": file_path,
            "status": "uploaded",
            "profile": None,
        }

        self.datasets[dataset_id] = dataset

        return dataset

    def get_dataset(
        self,
        dataset_id: str
    ) -> dict | None:

        return self.datasets.get(dataset_id)

    def update_profile(
        self,
        dataset_id: str,
        profile: dict
    ) -> dict:

        dataset = self.datasets.get(dataset_id)

        if dataset is None:
            raise KeyError("Dataset not found")

        dataset["status"] = "analyzed"
        dataset["profile"] = profile

        return dataset


# Shared DatasetService instance
dataset_service = DatasetService()
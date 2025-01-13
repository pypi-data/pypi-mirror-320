import glob
import os
from pathlib import PurePath
import abc
from enum import Enum
import json
import pandas as pd


class StorageType(Enum):
    FILE_SYSTEM = 1
    S3 = 2


STORAGE_NAME_MAP: dict = {"FILE-SYSTEM": StorageType.FILE_SYSTEM,
                          "S3": StorageType.S3}


class FileManager:
    """
    Facade for file management
    """

    def __init__(self, storage_type: StorageType | str):
        self.storage_type: StorageType = (
            storage_type if isinstance(storage_type, StorageType) else STORAGE_NAME_MAP[storage_type.upper()]
        )
        self._storage = FileStorageFactory.get_storage_handler(self.storage_type)

    def open(self, file_name, **kwargs) -> pd.DataFrame:
        storage_handler = FileStorageFactory().get_storage_handler(self.storage_type)
        return storage_handler.open(file_name, **kwargs)

    def write(self, data: pd.DataFrame, file_name, **kwargs):
        storage_handler = FileStorageFactory().get_storage_handler(self.storage_type)
        storage_handler.write(data, file_name, **kwargs)

    def list_files(self, folder: str, pattern="*"):
        storage_handler = FileStorageFactory().get_storage_handler(self.storage_type)
        files = storage_handler.list_files(folder, pattern)
        return files


class FileStorage(abc.ABC):

    @abc.abstractmethod
    def open(self, file_name: str, **kwargs) -> pd.DataFrame:
        ...

    @abc.abstractmethod
    def write(self, dataset: pd.DataFrame, file_name: str, **kwargs):
        ...

    @staticmethod
    def get_file_extension(file_name: str) -> str:
        file_name_elements: list = file_name.split(".")
        return file_name_elements[-1]

    @abc.abstractmethod
    def list_files(self, folder: str, pattern: str) -> list:
        ...


class FileStorageFactory:

    @staticmethod
    def get_storage_handler(storage_type: StorageType) -> FileStorage:
        if storage_type == StorageType.FILE_SYSTEM:
            return LocalFileSystem()
        return S3()


class LocalFileSystem(FileStorage):

    def open(self, file_name: str, **kwargs) -> pd.DataFrame:
        """
        Open a file pointed by file_name in the local file system

        :param file_name: Full path to the file name in the file system
        :param kwargs: Arguments for the file type backend, selected depending on the file system
        :return: A dataframe with the price time series

        """

        file_extension: str = self.get_file_extension(file_name)
        if file_extension == "parquet":
            return pd.read_parquet(file_name, engine="pyarrow", **kwargs)
        if file_extension == "csv":
            return pd.read_csv(file_name, **kwargs)
        if file_extension == "json":
            with open(file_name, "r") as file:
                return json.load(file)

        raise ValueError(f"File type not recognized {file_extension}")

    def write(self,
              dataset: any,
              file_name: str,
              **kwargs):

        self._create_output_folder(file_name)
        file_extension: str = self.get_file_extension(file_name)
        if file_extension == "parquet":
            dataset.to_parquet(file_name, engine="pyarrow", **kwargs)
        elif file_extension == "csv":
            dataset.to_csv(file_name)
        elif file_extension == "json":
            with open(file_name, "w", encoding="UTF-8") as file_ptr:
                json.dump(dataset, file_ptr)
        else:
            raise ValueError(f"File type not recognized {file_extension}")

    @staticmethod
    def _create_output_folder(full_file_path: str):
        folder = str(PurePath(full_file_path).parent)
        os.makedirs(folder, exist_ok=True)

    @staticmethod
    def _build_folder_name(folder_container: str,
                           folder: str):
        return str(PurePath(folder_container, folder))

    def list_files(self, folder: str, pattern: str, folder_separator: str = "/") -> list:
        folder_path = str(PurePath(folder, pattern))
        file_list = glob.glob(folder_path)
        files_clean = [file_name.split(folder_separator)[-1] for file_name in file_list]
        return files_clean


# TODO: Implement S3 methods
class S3(FileStorage):

    def open(self, file_name: str, **kwargs) -> pd.DataFrame:
        ...

    def write(self, dataset: pd.DataFrame, file_name: str, **kwargs):
        ...

    def list_files(self, folder: str, pattern: str) -> list:
        ...

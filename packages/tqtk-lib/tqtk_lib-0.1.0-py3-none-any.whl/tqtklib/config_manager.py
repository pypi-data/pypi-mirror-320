from pathlib import PurePath
import yaml


class ConfigManager:
    @staticmethod
    def open_config(file_path, file_name) -> dict:
        config_file_path = PurePath(file_path, file_name)
        with open(config_file_path, "r", encoding="utf-8") as file_pointer:
            config_file = yaml.safe_load(file_pointer)
        return config_file

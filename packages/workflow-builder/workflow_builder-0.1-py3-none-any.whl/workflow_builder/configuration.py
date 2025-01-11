from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Type, Union

try:
    import tomllib
except ImportError:
    import toml

from workflow_builder.logger import logger
from workflow_builder.utils import match_names

_CONFIGURATION_CLASS = []


def configclass(*alias: str, strict=False):
    """ UpperCamelCase, lowerCamelCase and SnakeCase can
    be accepted if strict is False
    """
    def wrapper(cls):
        dc = dataclass(cls)
        if strict:
            predictor = lambda _n: _n if _n in alias else None
        else:
            if len(alias) > 0:
                predictor = lambda _n: match_names(_n, alias)
            else:
                predictor = lambda _n: [_n] if _n == cls.__name__ else []

        _CONFIGURATION_CLASS.append((predictor, dc))
        return dc

    return wrapper


@dataclass()
class Configuration:
    """
    Base class for configurations, can be extended to define specific configuration types.
    """

    @classmethod
    def parser(cls, row_config: dict):
        """
        Default parser for dataclass-based subclasses. If not overridden,
        it will initialize the dataclass with the provided dictionary.
        It will also attempt to convert string or integer values to StrEnum or IntEnum.
        """
        _params = {}
        _attr_dict = cls.__annotations__
        for key, value in row_config.items():
            if key in _attr_dict:
                field_type = _attr_dict[key]

                # If the field is an Enum, try to convert the value
                if isinstance(field_type, type) and issubclass(field_type, Enum):
                    # Convert value to corresponding Enum
                    if isinstance(value, str):
                        try:
                            value = field_type[value]
                        except KeyError:
                            raise ValueError(f"Invalid value for {key}: {value} not found in {field_type}")
                    elif isinstance(value, int):
                        try:
                            value = field_type(value)
                        except ValueError:
                            raise ValueError(f"Invalid value for {key}: {value} not found in {field_type}")

                _params[key] = value
        return cls(**_params)


class ConfigManager:
    def __init__(self, config_files: str):
        self.config_files = config_files
        self.config_instances = {}
        self.config_data = {}

        # Parse multiple toml files
        toml_files = Path(self.config_files).glob('*.toml')
        for toml_file in toml_files:
            with open(toml_file, 'r', encoding='utf-8') as f:
                self.config_data.update(toml.load(f))

    def get_config(self, cls: Type[Configuration]):
        return self.config_instances[cls.__name__]

    def __getitem__(self, cls: Type[Configuration]):
        return self.config_instances[cls.__name__]

    def load_configs(self):
        """
        Create instances of Configuration subclasses
        under configuration.configs based on the parsed data.
        """

        for predictor, cls in _CONFIGURATION_CLASS:
            # Create instances of the class based on parsed configuration data
            cls_name = cls.__name__
            _initialized = False
            for _config_name in self.config_data:
                if len(names := predictor(_config_name)) > 0:
                    config_dict = self.config_data[names[0]]

                    # Create the instance and call _parser to initialize
                    config_instance = cls.parser(config_dict)
                    self.config_instances[cls_name] = config_instance
                    _initialized = True
                    # Store config_instance or perform additional actions here
                    logger.info(f"Created instance of {cls_name} with config {config_dict}")
            if not _initialized:
                try:
                    # Try to create the instance
                    config_instance = cls.parser({})
                    self.config_instances[cls_name] = config_instance
                except TypeError:
                    logger.warning(f'{cls_name} cannot create an instance without config')

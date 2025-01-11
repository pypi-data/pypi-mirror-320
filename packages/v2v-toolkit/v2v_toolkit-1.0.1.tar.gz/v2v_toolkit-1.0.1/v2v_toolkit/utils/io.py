import json
import os

import yaml
from typing import Any


def read_json(filepath: str) -> Any:
    """Reads a json file

    Args:
        filepath: path to the json file

    Returns:
        json like object
    """
    with open(filepath, "r") as f:
        return json.load(f)


def read_yaml(filepath: str) -> Any:
    """Reads a yaml file

    Args:
        filepath: path to the yaml file

    Returns:
        yaml like object
    """
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def read_default(filepath: str) -> Any:
    """Reads a default file

    Args:
        filepath: path to the default file

    Returns:
        string
    """
    with open(filepath, "r") as f:
        return f.read()


def io_read(path: str) -> Any:
    """Wrapper for reading files streams

    Args:
        path: path to the file

    Returns:
        any type of json like object or str
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")
    if path.endswith(".json"):
        return read_json(path)
    elif path.endswith(".yaml"):
        return read_yaml(path)
    return read_default(path)


def write_json(filepath: str, data: Any) -> None:
    """Writes a json file

    Args:
        filepath: path to the json file
        data: content to write

    Returns:
        None
    """
    if not filepath.endswith(".json"):
        filepath += ".json"
    with open(filepath, "w") as f:
        json.dump(data, f)


def write_yaml(filepath: str, data: Any) -> None:
    """Writes a yaml file

    Args:
        filepath: path to the json file
        data: content to write

    Returns:
        None
    """
    if not filepath.endswith(".yaml"):
        filepath += ".yaml"
    with open(filepath, "w") as f:
        yaml.dump(data, f)


def write_default(filepath: str, data: Any) -> None:
    """Writes to file stream

    Args:
        filepath: path to the file
        data: content to write

    Returns:
        None
    """
    with open(filepath, "w") as f:
        f.write(data)


def io_write(path: str, data: Any, overwrite: bool = False) -> None:
    """Wrapper for writing to differnet files streams

    Args:
        path: path to the file
        data: content to write
        overwrite: overwrite existing file

    Returns:
        None

    Raises:
        FileExistsError - if file already exists and overwrite flag is not set.
    """
    if os.path.exists(path):
        if not overwrite:
            raise FileExistsError(path)
        os.remove(path)
    if path.endswith(".json"):
        return write_json(path, data)
    elif path.endswith(".yaml"):
        return write_yaml(path, data)
    return write_default(path, data)

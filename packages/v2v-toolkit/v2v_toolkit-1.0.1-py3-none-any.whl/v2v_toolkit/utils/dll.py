import importlib.util
import os
import pathlib
import sys

from v2v_toolkit.exceptions import V2VGraphError


def dynamic_loading(cls: str, workspace: str | None = None):
    """DLL: dynamic library loading utility

    Loads a class from a workspace, allowing for dynamic module loading via configuration files.

    Args:
        cls: class name or package to be loaded into program
        workspace: search root directory

    Returns:
        loaded class signature.

    Raises:
        V2VGraphError - on dynamic module loading failure
    """
    workspace = pathlib.Path(workspace if workspace else os.getcwd())
    *module_path_parts, class_name = cls.split(".")
    module_path = pathlib.Path(*module_path_parts)
    file_path = workspace / module_path.with_suffix(".py")
    module_name = ".".join(module_path_parts)

    if file_path.exists():
        spec = importlib.util.spec_from_file_location(
            module_name, str(file_path.resolve())
        )
        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, class_name):
            return getattr(module, class_name)
        raise V2VGraphError(f"Class '{class_name}' not found in module '{module_name}'")

    raise V2VGraphError(f"Module file not found: {file_path}")

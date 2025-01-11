from __future__ import annotations

import dataclasses
import logging
import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, List

from v2v_toolkit.exceptions import V2VModuleError
from v2v_toolkit.utils.config import ConfigBaseStruct
from v2v_toolkit.utils.logs import setup_logger
from v2v_toolkit.core.workspace import Workspace


@dataclasses.dataclass
class ModuleMapping:
    module: str  # module path to be imported
    name: str | None = None  # unique identifier for the module
    depends_on: List[str] = dataclasses.field(
        default_factory=list
    )  # list of dependencies
    params: dict = dataclasses.field(
        default_factory=dict
    )  # additional parameters to instantiate obj

    def __post_init__(self):
        """Set default values

        Returns:
            None
        """
        if not self.name:
            self.name = self.module.split(".")[-1]


class Module(ABC):
    def __init__(
        self,
        name: str | None = None,
        depends_on: List[Module] | None = None,
        workspace: str | Workspace | None = None,
        logger: logging.Logger | None = None,
        **params,
    ):
        """Constructor for base `Module` class to be pipelined.

        Args:
            name: unique identifier.
            depends_on: dependency list.
            workspace: disk cache handler.
            logger: logger object if logging is enabled or provided.
            **params: any additional parameters to instantiate algorithm.
        """
        self.name = name if name else self.__class__.__name__
        self.depends_on = depends_on if depends_on else list()
        self.config = ConfigBaseStruct(**params)

        self.workspace = workspace
        if isinstance(workspace, str):
            workspace = workspace if workspace else self.name
            self.workspace = Workspace(workspace=workspace)
        elif isinstance(workspace, Workspace):
            self.workspace = workspace
        self.logger = logger
        if self.config.logging_enabled and self.logger is None:
            if self.workspace is None:
                logfile = None
            else:
                logfile = os.path.join(self.workspace.root, f"{self.name}.log")
                if self.workspace.root != self.workspace.workspace:
                    logfile = os.path.join(self.workspace.workspace, logfile)
            self.logger = setup_logger(
                loggername=self.name, filename=logfile, level=self.config.logging_level
            )
        if not self.config.logging_enabled:
            self.logger = setup_logger("", null=True)

    def setup(self) -> None:
        """Allocation of required resources for algorithm.

        Returns: None

        """
        pass

    def teardown(self) -> None:
        """De-allocation of resources.

        Returns: None

        """
        pass

    def __call__(self, *args, **kwargs) -> Any:
        """Main method to run algorithm respecting constraints introduced by high-hierarchy executor.

        Args:
            *args: any positional arguments to be passed to algorithm
            **kwargs: any keyword arguments to be passed to algorithm

        Returns: T - any (generic) type
        Raises: V2VModuleError

        """
        try:
            self.setup()
            ret = self.run(*args, **kwargs)
            self.teardown()
            return ret
        except Exception as e:
            self.logger.error(f"Node '{str(self)}' failed: {traceback.format_exc()}")
            raise V2VModuleError(e)

    def __repr__(self) -> str:
        return f"{self.name}"

    def __str__(self) -> str:
        return self.__repr__()

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Base method to run algorithm.

        Args:
            *args, **kwargs: the source data to consume.

        Returns:
            product of the algorithm.
        """
        pass

    @property
    def metadata(self):
        """Metadata from module instance.

        Returns:
            dict with module metadata
        """
        return {
            "name": self.name,
            "depends_on": [str(dep) for dep in self.depends_on],
            "workspace": self.workspace,
            "params": str(dataclasses.asdict(self.config)),
        }

    def add_dependency(self, module: Module) -> None:
        """Add dependency to the module.

        Add any specified dependency to the module.

        Args:
            module: the module instance to add

        Returns:
            None
        """
        self.depends_on.append(module)

    def remove_dependency(self, module: Module) -> None:
        """Remove dependency from the module.

        Removes any specified dependency from the module.

        Args:
            module: the module to remove

        Returns:
            None
        """
        self.depends_on.remove(module)

from __future__ import annotations

import logging
import os
import sys
from typing import MutableMapping

from v2v_toolkit.utils.common import get_current_os, get_current_version, cpu_ct

SysCtx = MutableMapping[str, str]


class Context:
    def __init__(self, ctx: SysCtx = os.environ, **kwargs):
        """System context customized for the execution scheme.

        The context is a collection of variables that manage the execution environment.
        It is used to orchestrate the execution of the pipeline.

        Args:
            ctx: system context
            **kwargs: additional parameters like scheduler, logging, caching etc.
        """
        self.os = get_current_os()
        self.version = get_current_version()
        self.python, self.python_version = sys.executable, "{}.{}.{}".format(
            *sys.version_info[:3]
        )
        self.cpu_limit = int(
            ctx.get("V2V_CPU_LIMIT", kwargs.get("cpu_limit", cpu_ct()))
        )
        self.scheduler = ctx.get("V2V_SCHEDULER", kwargs.get("scheduler", "processes"))
        self.logging_enabled = ctx.get(
            "V2V_LOGGING_ENABLED", kwargs.get("logging_enabled", False)
        )
        self.logging_level = logging.getLevelName(
            ctx.get("V2V_LOGGING_LEVEL", kwargs.get("logging_level", "INFO"))
        )
        self.caching = bool(ctx.get("V2V_CACHING", kwargs.get("caching", False)))
        self.timeout = int(ctx.get("V2V_TIMEOUT", kwargs.get("timeout", -1)))

    def __str__(self) -> str:
        """Context to string conversion.

        Returns:
            string representation from the context obj
        """
        return (
            f"python: {self.python_version}; "
            f"os: {self.os}; "
            f"cpu_limit: {self.cpu_limit}; "
            f"scheduler: {self.scheduler}; "
            f"logging_enabled: {self.logging_enabled}; "
            f"caching: {self.caching}; "
            f"timeout: {self.timeout}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_ctx(env: SysCtx = os.environ, **kwargs) -> Context:
        """Create a new context from the provided environment variables otherwise use system defaults.

        Args:
            env: os environment
            **kwargs: additional parameters

        Returns:
            Context object
        """
        return Context(env, **kwargs)

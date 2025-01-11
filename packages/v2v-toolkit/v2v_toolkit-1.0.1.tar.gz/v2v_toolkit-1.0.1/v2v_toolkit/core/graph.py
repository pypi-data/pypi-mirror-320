from __future__ import annotations

import logging
import os.path
import traceback
from typing import Any, List, Dict

import dask
import networkx as nx
from dask.delayed import Delayed

from v2v_toolkit.core.context import Context
from v2v_toolkit.core.module import ModuleMapping
from v2v_toolkit.exceptions import V2VError, V2VModuleError, V2VGraphError
from v2v_toolkit.utils.dll import dynamic_loading
from v2v_toolkit.utils.io import io_read
from v2v_toolkit.utils.logs import setup_logger
from v2v_toolkit.core.workspace import Workspace

T = Any  # template typedef


class Graph:
    def __init__(
        self,
        context: Context | None = None,
        workspace: str | Workspace | None = None,
        logger: logging.Logger | None = None,
    ):
        """Graph runtime engine.

        Class implements the main runtime engine for the modular pipeline.
        Takes care of all downstream low-level tasks like lazy loading, scheduling, parallelism,
        processes spawning, timeouts, terminations, memory constraints etc.

        Args:
            context: system context control parameters to orchestrate execution of pipeline.
            workspace: disk cache manager or path to workspace to be created in current working dir.
            logger: logger object for debugging purposes, health checks and telemetry.
        """
        self.context = context if context else Context()
        self.workspace = workspace if workspace else Workspace()
        if isinstance(workspace, str):
            self.workspace = Workspace(workspace=workspace)
        self.logger = logger
        if self.context.logging_enabled and self.logger is None:
            logfile = os.path.join(self.workspace.root, "runtime.log")
            self.logger = setup_logger(
                loggername=self.__class__.__name__,
                filename=logfile,
                level=context.logging_level,
            )
        if not self.context.logging_enabled:
            self.logger = setup_logger("", null=True)
        self.dag = nx.DiGraph()
        self.rt_code = 0

    def __conv2process(self, u: T, subgraph: list):
        """Wrapper for processes to have non-blocking capability.

        Args:
            u: the callable struct (__call__ method implementation)
            subgraph: dependencies, execution of callable struct is stalled until graph resolve all needed dependencies.

        Returns:
            evaluated callable struct for scheduling.
        """

        def safe_exec(*inputs):
            try:
                return u(*inputs)
            except V2VModuleError:
                self.logger.error(f"Node '{str(u)}' failed: {traceback.format_exc()}")
                self.rt_code += 1
                return None

        return dask.delayed(safe_exec)(*subgraph, dask_key_name=str(u))

    def add_module(self, u: T) -> None:
        """Add node to the graph.

        Args:
            u: node to be added

        Returns:
            None
        """
        self.dag.add_node(str(u), element=u)

    def add_dependency(self, u: T, v: T) -> None:
        """Add edge to the graph.

        Args:
            u: source node
            v: destination node

        Returns:
            None
        """
        self.dag.add_edge(str(u), str(v))

    def __call__(self) -> int:
        """Execute the graph.

        Traverses the graph and executes all nodes in topological order.

        Returns:
            int - exit code, representing number of failed modules in pipeline.

        Raises:
            V2VGraphError - on graph runtime failure.
        """
        scheduled_processes = self.__node2process()
        terminal_nodes = self.__leafs()
        spawn_processes = [scheduled_processes[node] for node in terminal_nodes]
        try:
            dask.compute(*spawn_processes, workers=self.context.cpu_limit)
        except Exception as e:
            self.logger.error(f"Graph runtime failed: {traceback.format_exc()}")
            raise V2VGraphError(e)
        return self.rt_code

    def __leafs(self) -> List[T]:
        """Find leaf nodes in the graph.

        Returns:
            list of leaf nodes
        """
        return [
            node_hash
            for node_hash in self.dag.nodes()
            if self.dag.out_degree(node_hash) == 0
        ]

    def __node2process(self) -> Dict[str, Delayed]:
        processes = dict()
        for node_hash in nx.topological_sort(self.dag):
            u = self[node_hash]
            subgraph = [
                processes[predecessor]
                for predecessor in self.dag.predecessors(node_hash)
            ]
            process = self.__conv2process(u, subgraph)
            processes[node_hash] = process
        return processes

    def __getitem__(self, ele_id: T) -> T:
        """Get element from the graph.

        Args:
            ele_id: element id

        Returns:
            T - element
        """
        return self.dag.nodes[ele_id]["element"]

    def __iter__(self) -> T:
        """Iterate over the tree of T structs.

        Returns:
            Iterator of G[T]
        """
        for node_hash in nx.topological_sort(self.dag):
            yield self[node_hash]

    @staticmethod
    def build_from_config_file(
        config_file: str,
        workspace: str | Workspace | None = None,
        context: Context | None = Context(),
        logger: logging.Logger | None = None,
    ) -> Graph:
        """Build graph from config file [yaml, json].

        Args:
            config_file: path to config file
            workspace: path or workspace object for graph runtime
            context: system context control parameters to orchestrate execution of pipeline
            logger: logger object for debugging purposes

        Returns:
            Graph object

        Raises:
            V2VGraphError - on dynamic module loading failure
            V2VError - on any other unrecoverable error
        """
        try:
            m_tree = dict()
            graph_runtime_engine = Graph(
                context=context, workspace=workspace, logger=logger
            )
            config = io_read(config_file)
            for module_config in config:
                m_mapping = ModuleMapping(**module_config)
                mapped_class = dynamic_loading(
                    cls=m_mapping.module, workspace=os.getcwd()
                )
                cls_instance = mapped_class(
                    name=m_mapping.name,
                    depends_on=[m_tree[dep] for dep in m_mapping.depends_on],
                    logger=(
                        logger
                        if m_mapping.params.get(
                            "logging_enabled", context.logging_enabled
                        )
                        else None
                    ),
                    workspace=Workspace(
                        root=graph_runtime_engine.workspace.root,
                        workspace=m_mapping.name,
                    ),
                    **m_mapping.params,
                )
                m_tree[m_mapping.name] = cls_instance
                graph_runtime_engine.add_module(cls_instance)
            for m in graph_runtime_engine:
                for dep in m.depends_on:
                    graph_runtime_engine.add_dependency(dep, m)
            return graph_runtime_engine
        except V2VGraphError as e:
            if logger:
                logger.error(e)
            raise e
        except Exception as e:
            raise V2VError(e)

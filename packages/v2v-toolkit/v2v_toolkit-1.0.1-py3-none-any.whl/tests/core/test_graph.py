import os.path
import os.path
import tempfile
import time
import traceback
import unittest
from typing import Any
from unittest.mock import patch, MagicMock

from dask.delayed import Delayed

from v2v_toolkit.exceptions import V2VModuleError
from tests.mlogger import MockLogger
from v2v_toolkit.utils.common import get_current_os
from v2v_toolkit.core.graph import Graph, V2VGraphError, V2VError, Context
from v2v_toolkit.core.module import Module
from v2v_toolkit.core.workspace import Workspace
from v2v_toolkit.utils.logs import setup_logger

RUNTIME_ABS_DELTA = 0.025


class DummyModule(Module):
    def __init__(
        self,
        name=None,
        depends_on=None,
        workspace=None,
        logger=None,
        workload=0.0,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, **params)
        self.workload = workload

    def setup(self) -> None:
        time.sleep(self.workload)

    def run(self, *args, **kwargs):
        time.sleep(self.workload)
        return 42


class StreamProducer(DummyModule):
    def __init__(
        self,
        name=None,
        depends_on=None,
        workspace=None,
        logger=None,
        workload=0.0,
        stream_size=10,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, workload, **params)
        self.stream_size = stream_size

    def run(self):
        return [ele for ele in range(self.stream_size)]


class StreamConsumer(DummyModule):
    def __init__(
        self,
        name=None,
        depends_on=None,
        workspace=None,
        logger=None,
        workload=0.0,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, workload, **params)

    def run(self, stream: Any):
        if stream is None:
            raise ValueError("Stream required")
        return [ele * 2 for ele in stream]


class Aggregator(DummyModule):
    def __init__(
        self,
        name=None,
        depends_on=None,
        workspace=None,
        logger=None,
        workload=0.0,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, workload, **params)

    def run(self, stream1, stream2):
        if stream1 is None:
            return stream2
        if stream2 is None:
            return stream1
        return stream1 + stream2


class TestGraph(unittest.TestCase):
    def test_graph_initialization(self):
        Graph()

    def test_graph_initialization_with_str_workspace(self):
        runtime = Graph(context=Context(logging_enabled=False), workspace="workspace")
        self.assertEqual(
            runtime.workspace.workspace, os.path.join(os.getcwd(), "cache", "workspace")
        )

    @unittest.skipIf(get_current_os() == "windows", "Not supported on Windows")
    def test_graph_logger_initialization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Graph(
                context=Context(logging_enabled=True),
                workspace=Workspace(root=temp_dir),
            )
            with MockLogger() as logger:
                runtime.logger.info("Test")
                self.assertIn(("INFO", "Test"), logger.messages)

    def test_add_module(self):
        runtime = Graph(context=Context(logging_enabled=False))
        dummy_module = DummyModule(name="module_1")
        runtime.add_module(dummy_module)
        self.assertIn("module_1", runtime.dag.nodes)
        self.assertEqual(runtime.dag.nodes["module_1"]["element"], dummy_module)

    def test_add_dependency(self):
        runtime = Graph(context=Context(logging_enabled=False))
        module_1 = DummyModule(name="module_1")
        module_2 = DummyModule(name="module_2")

        runtime.add_module(module_1)
        runtime.add_module(module_2)

        runtime.add_dependency(module_1, module_2)
        self.assertTrue(runtime.dag.has_edge("module_1", "module_2"))

    def test_graph_iteration(self):
        runtime = Graph(context=Context(logging_enabled=False))
        module_1 = DummyModule(name="module_1")
        module_2 = DummyModule(name="module_2")
        module_3 = DummyModule(name="module_3")

        runtime.add_module(module_1)
        runtime.add_module(module_2)
        runtime.add_module(module_3)

        runtime.add_dependency(module_1, module_2)
        runtime.add_dependency(module_2, module_3)
        runtime.add_dependency(module_1, module_3)

        for module in runtime:
            self.assertIn(module.name, ["module_1", "module_2", "module_3"])

    def test_call(self):
        runtime = Graph(context=Context(logging_enabled=False))
        dummy_module = DummyModule(name="module_1")
        runtime.add_module(dummy_module)
        ret = runtime()
        self.assertEqual(ret, 0)

    @patch("dask.compute")
    def test_call_error_propagation(self, mock_dask_compute):
        mock_dask_compute.side_effect = Exception("Error")
        dummy_module = MagicMock()
        runtime = Graph(context=Context(logging_enabled=False))
        runtime.add_module(dummy_module)

        with MockLogger() as logger:
            with self.assertRaises(V2VGraphError):
                runtime()
                self.assertIn(
                    (
                        "ERROR",
                        f"Graph runtime failed due to exception: {traceback.format_exc()}",
                    ),
                    logger.messages,
                )

    def test_safe_exec_success(self):
        def success_function(*args):
            return 0

        subgraph = []
        runtime = Graph(context=Context(logging_enabled=False))
        process = runtime._Graph__conv2process(success_function, subgraph)
        self.assertIsInstance(process, Delayed)
        result = process.compute()
        self.assertEqual(result, 0)

    def test_safe_exec_failure(self):
        def failure_function(*args):
            raise V2VModuleError("Intentional Failure")

        subgraph = []
        runtime = Graph(context=Context(logging_enabled=False))
        process = runtime._Graph__conv2process(failure_function, subgraph)
        self.assertIsInstance(process, Delayed)
        process.compute()
        self.assertEqual(runtime.rt_code, 1)

    def test_streams(self):
        ctx = Context(cpu_limit=1)
        runtime = Graph(context=ctx)
        producer = DummyModule(name="producer")
        m1 = DummyModule(name="module_1", workload=0.1, depends_on=[producer])
        m2 = DummyModule(name="module_2", workload=0.1, depends_on=[producer])

        runtime.add_module(producer)
        runtime.add_module(m1)
        runtime.add_module(m2)

        runtime.add_dependency(producer, m1)
        runtime.add_dependency(producer, m2)

        ret = runtime()
        self.assertEqual(ret, 0)

    def test_parallel_streams(self):
        ctx = Context()
        runtime = Graph(context=ctx)
        producer = StreamProducer(name="producer")
        m1 = StreamConsumer(name="module_1", workload=0.1, depends_on=[producer])
        m2 = StreamConsumer(name="module_2", workload=0.1, depends_on=[producer])
        sink = DummyModule(name="sink", depends_on=[m1, m2])

        runtime.add_module(producer)
        runtime.add_module(m1)
        runtime.add_module(m2)
        runtime.add_module(sink)

        runtime.add_dependency(producer, m1)
        runtime.add_dependency(producer, m2)
        runtime.add_dependency(m1, sink)
        runtime.add_dependency(m2, sink)

        ret = runtime()
        self.assertEqual(ret, 0)

    @patch("v2v_toolkit.core.graph.dynamic_loading")
    @patch("v2v_toolkit.core.graph.io_read")
    def test_build_from_config_success(self, mock_io_read, mock_dynamic_loading):
        mock_io_read.return_value = [
            {
                "name": "module_1",
                "module": "DummyModule",
                "depends_on": [],
                "params": {},
            },
            {
                "name": "module_2",
                "module": "DummyModule",
                "depends_on": ["module_1"],
                "params": {},
            },
        ]
        mock_dynamic_loading.return_value = DummyModule

        graph = Graph.build_from_config_file(
            config_file="dummy_config.yaml",
            workspace=None,
            context=Context(),
            logger=None,
        )

        self.assertIsInstance(graph, Graph)
        self.assertEqual(len(graph.dag.nodes), 2)
        self.assertIn("module_1", graph.dag.nodes)
        self.assertIn("module_2", graph.dag.nodes)

    @patch("v2v_toolkit.core.graph.dynamic_loading")
    @patch("v2v_toolkit.core.graph.io_read")
    def test_build_from_config_graph_error(self, mock_io_read, mock_dynamic_loading):
        mock_io_read.return_value = [
            {
                "name": "module_1",
                "module": "InvalidModule",
                "depends_on": [],
                "params": {},
            },
        ]
        mock_dynamic_loading.side_effect = V2VGraphError("Dynamic loading failed")
        with self.assertRaises(V2VGraphError) as context:
            Graph.build_from_config_file(
                config_file="dummy_config.yaml",
                workspace=None,
                context=Context(),
                logger=None,
            )
        self.assertEqual(str(context.exception), "Dynamic loading failed")

    @patch("v2v_toolkit.core.graph.io_read")
    def test_build_from_config_base_error(self, mock_io_read):
        mock_io_read.side_effect = Exception("Unexpected error")
        with self.assertRaises(V2VError) as context:
            Graph.build_from_config_file(
                config_file="dummy_config.yaml",
                workspace=None,
                context=Context(),
                logger=None,
            )
        self.assertEqual(str(context.exception), "Unexpected error")

    @patch("v2v_toolkit.core.graph.dynamic_loading")
    @patch("v2v_toolkit.core.graph.io_read")
    def test_build_from_config_logger(self, mock_io_read, mock_dynamic_loading):
        mock_io_read.return_value = [
            {
                "name": "module_1",
                "module": "InvalidModule",
                "depends_on": [],
                "params": {},
            },
        ]
        mock_dynamic_loading.side_effect = V2VGraphError("Dynamic loading failed")
        with MockLogger() as logger:
            with self.assertRaises(V2VGraphError):
                Graph.build_from_config_file(
                    config_file="dummy_config.yaml",
                    context=Context(logging_enabled=True),
                    logger=setup_logger("test", filename=None),
                )
        self.assertIn(
            (
                "ERROR",
                "Dynamic loading failed",
            ),
            logger.messages,
        )

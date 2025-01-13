import os
import tempfile
import unittest

from v2v_toolkit.utils.common import get_current_os
from v2v_toolkit.core.workspace import Workspace
from tests.mlogger import MockLogger
from v2v_toolkit.core.module import Module, ModuleMapping


class DummyModule(Module):
    def __init__(
        self, name=None, depends_on=None, workspace=None, logger=None, **kwargs
    ):
        super().__init__(name, depends_on, workspace, logger, **kwargs)
        self.ram_expensive_stuff = None

    def setup(self) -> None:
        self.ram_expensive_stuff = [idx for idx in range(5)]

    def teardown(self) -> None:
        del self.ram_expensive_stuff

    def run(self, *args, **kwargs):
        self.logger.info("Running DummyModule")
        if self.ram_expensive_stuff is None:
            raise RuntimeError("Intentional failure.")
        return 0


class TestModule(unittest.TestCase):
    def test_default_initialization(self):
        module = DummyModule(name="TestModule")
        self.assertEqual(module.name, "TestModule")
        self.assertIsNone(module.workspace)
        self.assertNoLogs(module.logger, module.config.logging_level)

    def test_workspace_from_obj_initialization(self):
        module = DummyModule(
            name="TestModule", workspace=Workspace(workspace="test_workspace")
        )
        self.assertEqual(module.name, "TestModule")
        self.assertEqual(module.workspace.root, os.path.join(os.getcwd(), "cache"))
        self.assertEqual(
            module.workspace.workspace,
            os.path.join(os.getcwd(), "cache", "test_workspace"),
        )

    def test_workspace_from_str_initialization(self):
        module = DummyModule(name="TestModule", workspace="test_workspace")
        self.assertEqual(module.name, "TestModule")
        self.assertEqual(module.workspace.root, os.path.join(os.getcwd(), "cache"))
        self.assertEqual(
            module.workspace.workspace,
            os.path.join(os.getcwd(), "cache", "test_workspace"),
        )

    @unittest.skipIf(get_current_os() == "windows", "Not supported on Windows")
    def test_logging_automatically_enabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module = DummyModule(
                name="TestModule",
                workspace=Workspace(root=temp_dir),
                logging_enabled=True,
            )
            with MockLogger() as logger:
                module.logger.info("Logging enabled")
                self.assertIn(
                    (
                        "INFO",
                        "Logging enabled",
                    ),
                    logger.messages,
                )

    @unittest.skipIf(get_current_os() == "windows", "Not supported on Windows")
    def test_module_logging_enabled(self):
        params = {
            "logging_enabled": True,
            "logging_level": "INFO",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir, workspace="test_workspace")
            module = DummyModule(name="TestModule", workspace=workspace, **params)
            with MockLogger() as logger:
                module()
                self.assertEqual(module.name, "TestModule")
                self.assertIn(
                    (
                        "INFO",
                        "Running DummyModule",
                    ),
                    logger.messages,
                )

    def test_module_logging_enabled_without_serialization(self):
        params = {
            "logging_enabled": True,
            "logging_level": "INFO",
        }
        module = DummyModule(name="TestModule", **params)
        with MockLogger() as logger:
            module()
            self.assertEqual(module.name, "TestModule")
            self.assertIn(
                (
                    "INFO",
                    "Running DummyModule",
                ),
                logger.messages,
            )

    def test_dependency_management(self):
        module_a = DummyModule(name="ModuleA")
        module_b = DummyModule(name="ModuleB")

        module_a.add_dependency(module_b)
        self.assertIn(module_b, module_a.depends_on)
        module_a.remove_dependency(module_b)
        self.assertNotIn(module_b, module_a.depends_on)

    def test_call_execution(self):
        module = DummyModule(name="TestModule")
        result = module()
        self.assertEqual(result, 0)

    def test_metadata(self):
        module = DummyModule(name="TestModule")
        metadata = module.metadata
        self.assertEqual(metadata["name"], "TestModule")
        self.assertEqual(metadata["workspace"], None)
        self.assertIn("logging_enabled", metadata["params"])

    def test_run_method_raises_error_on_unallocated_memory(self):
        module = DummyModule(name="TestModule")
        with self.assertRaises(RuntimeError):
            module.run()

    def test_exception_handling_in_call(self):
        class FailingModule(Module):
            def run(self, *args, **kwargs):
                raise RuntimeError("Intentional failure.")

        module = FailingModule(name="FailingModule")
        with self.assertRaises(Exception):
            module()

    def test_module_mapping_name_resolution(self):
        module_mapping = ModuleMapping(module="tests.core.test_module.DummyModule")
        self.assertEqual(module_mapping.name, "DummyModule")
        self.assertEqual(module_mapping.module, "tests.core.test_module.DummyModule")

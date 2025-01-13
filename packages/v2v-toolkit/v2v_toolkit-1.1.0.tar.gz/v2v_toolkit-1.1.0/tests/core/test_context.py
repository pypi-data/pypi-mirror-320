import logging
import sys
import unittest
from unittest.mock import patch

from v2v_toolkit.core.context import Context

pythonpath = "v2v_toolkit.core.context"


class TestContext(unittest.TestCase):

    @patch(f"{pythonpath}.get_current_os", return_value="Linux")
    @patch(f"{pythonpath}.get_current_version", return_value="1.0.0")
    @patch(f"{pythonpath}.cpu_ct", return_value=4)
    def test_initialization_with_default_values(self, mock_os, mock_version, mock_cpu):
        ctx = Context()

        self.assertEqual(ctx.os, "Linux")
        self.assertEqual(ctx.version, "1.0.0")
        self.assertEqual(ctx.python, sys.executable)
        self.assertEqual(
            ctx.python_version,
            f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
        )
        self.assertEqual(ctx.cpu_limit, 4)
        self.assertEqual(ctx.scheduler, "processes")
        self.assertFalse(ctx.logging_enabled)
        self.assertEqual(ctx.logging_level, logging.INFO)
        self.assertFalse(ctx.caching)
        self.assertEqual(ctx.timeout, -1)

    @patch(f"{pythonpath}.get_current_os", return_value="Linux")
    @patch(f"{pythonpath}.get_current_version", return_value="1.0.0")
    @patch(f"{pythonpath}.cpu_ct", return_value=4)
    def test_initialization_with_custom_kwargs(self, mock_os, mock_version, mock_cpu):
        ctx = Context(
            cpu_limit=8,
            scheduler="threads",
            logging_enabled=True,
            logging_level="DEBUG",
            caching=True,
            timeout=300,
        )

        self.assertEqual(ctx.cpu_limit, 8)
        self.assertEqual(ctx.scheduler, "threads")
        self.assertTrue(ctx.logging_enabled)
        self.assertEqual(ctx.logging_level, logging.DEBUG)
        self.assertTrue(ctx.caching)
        self.assertEqual(ctx.timeout, 300)

    @patch(f"{pythonpath}.get_current_os", return_value="Linux")
    @patch(f"{pythonpath}.get_current_version", return_value="1.0.0")
    @patch(f"{pythonpath}.cpu_ct", return_value=4)
    def test_initialization_with_env_ctx(self, mock_os, mock_version, mock_cpu):
        env = {
            "V2V_CPU_LIMIT": "2",
            "V2V_SCHEDULER": "threads",
            "V2V_LOGGING_ENABLED": "True",
            "V2V_LOGGING_LEVEL": "DEBUG",
            "V2V_CACHING": "True",
            "V2V_TIMEOUT": "600",
        }
        ctx = Context(ctx=env)

        self.assertEqual(ctx.cpu_limit, 2)
        self.assertEqual(ctx.scheduler, "threads")
        self.assertTrue(ctx.logging_enabled)
        self.assertEqual(ctx.logging_level, logging.DEBUG)
        self.assertTrue(ctx.caching)
        self.assertEqual(ctx.timeout, 600)

    def test_str_method(self):
        ctx = Context(
            cpu_limit=8,
            scheduler="threads",
            logging_enabled=True,
            logging_level=logging.DEBUG,
            caching=True,
            timeout=300,
        )
        str_representation = str(ctx)
        self.assertIn("python:", str_representation)
        self.assertIn("os:", str_representation)
        self.assertIn("cpu_limit: 8;", str_representation)
        self.assertIn("scheduler: threads;", str_representation)
        self.assertIn("logging_enabled: True;", str_representation)
        self.assertIn("caching: True;", str_representation)

    def test_repr_method(self):
        ctx = Context(
            cpu_limit=8,
            scheduler="threads",
            logging_enabled=True,
            logging_level=logging.DEBUG,
            caching=True,
            timeout=300,
        )
        repr_representation = repr(ctx)
        self.assertEqual(repr_representation, str(ctx))

    @patch(f"{pythonpath}.get_current_os", return_value="Linux")
    @patch(f"{pythonpath}.get_current_version", return_value="1.0.0")
    @patch(f"{pythonpath}.cpu_ct", return_value=4)
    def test_from_ctx_method(self, mock_os, mock_version, mock_cpu):
        env = {
            "V2V_CPU_LIMIT": "2",
            "V2V_SCHEDULER": "threads",
            "V2V_LOGGING_ENABLED": "True",
            "V2V_LOGGING_LEVEL": "DEBUG",
            "V2V_CACHING": "True",
            "V2V_TIMEOUT": "600",
        }
        ctx = Context.from_ctx(env)

        self.assertEqual(ctx.cpu_limit, 2)
        self.assertEqual(ctx.scheduler, "threads")
        self.assertTrue(ctx.logging_enabled)
        self.assertEqual(ctx.logging_level, logging.DEBUG)
        self.assertTrue(ctx.caching)
        self.assertEqual(ctx.timeout, 600)

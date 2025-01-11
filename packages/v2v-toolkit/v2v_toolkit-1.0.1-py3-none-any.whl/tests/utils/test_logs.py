import os
import tempfile
import unittest

from tests.mlogger import MockLogger
from v2v_toolkit.utils.common import get_current_os
from v2v_toolkit.utils.io import read_default
from v2v_toolkit.utils.logs import setup_logger


class TestLogs(unittest.TestCase):
    @unittest.skipIf(get_current_os() == "windows", "Not supported on Windows")
    def test_logger_with_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file = os.path.join(temp_dir, "default.log")
            with MockLogger() as logs:
                logger = setup_logger("default", filename=file)
                logger.info("Testing")
                self.assertIsNotNone(logger)
                self.assertTrue(os.path.exists(file))
                self.assertTrue(os.path.isfile(file))
                self.assertIn(
                    (
                        "INFO",
                        "Testing",
                    ),
                    logs.messages,
                )
                log_content = read_default(file)
                self.assertTrue("INFO" in log_content and "Testing" in log_content)

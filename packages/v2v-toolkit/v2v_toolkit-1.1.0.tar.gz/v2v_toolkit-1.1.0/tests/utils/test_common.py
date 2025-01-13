import subprocess
import unittest
from unittest.mock import patch
from v2v_toolkit.exceptions import V2VError
from v2v_toolkit.utils.common import (
    cpu_ct,
    get_current_os,
    linux_os,
    git_hash,
    git_tag,
    get_current_version,
)

pythonpath = "v2v_toolkit.utils.common"


class TestCommon(unittest.TestCase):

    @patch(f"{pythonpath}.cpu_count", return_value=4)
    def test_cpu_ct(self, mock_cpu_count):
        result = cpu_ct()
        self.assertEqual(result, 4)

    @patch(f"{pythonpath}.cpu_count", return_value=0)
    def test_cpu_ct_when_zero(self, mock_cpu_count):
        result = cpu_ct()
        self.assertEqual(result, 1)

    @patch(f"{pythonpath}.cpu_count", side_effect=NotImplementedError)
    def test_cpu_ct_when_not_implemented(self, mock_cpu_count):
        result = cpu_ct()
        self.assertEqual(result, 1)

    @patch("platform.system", return_value="Darwin")
    def test_get_current_os_macos(self, mock_platform):
        result = get_current_os()
        self.assertEqual(result, "macos")

    @patch("platform.system", return_value="Windows")
    def test_get_current_os_windows(self, mock_platform):
        result = get_current_os()
        self.assertEqual(result, "windows")

    @patch("platform.system", return_value="Linux")
    def test_get_current_os_linux(self, mock_platform):
        result = get_current_os()
        self.assertEqual(result, "linux")

    @patch("platform.system", return_value="UnknownOS")
    def test_get_current_os_unknown(self, mock_platform):
        with self.assertRaises(V2VError):
            get_current_os()

    @patch("platform.platform", return_value="Linux")
    def test_linux_os_true(self, mock_platform):
        result = linux_os()
        self.assertTrue(result)

    @patch("platform.platform", return_value="Windows")
    def test_linux_os_false(self, mock_platform):
        result = linux_os()
        self.assertFalse(result)

    @patch("subprocess.check_output")
    def test_git_hash_success(self, mock_check_output):
        mock_check_output.return_value = b"abc123"
        result = git_hash()
        self.assertEqual(result, "abc123")

    @patch(
        "subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")
    )
    def test_git_hash_failure(self, mock_check_output):
        result = git_hash()
        self.assertIsNone(result)

    @patch("subprocess.check_output")
    def test_git_tag_success(self, mock_check_output):
        mock_check_output.return_value = b"v1.0.0"
        result = git_tag()
        self.assertEqual(result, "v1.0.0")

    @patch(
        "subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")
    )
    def test_git_tag_failure(self, mock_check_output):
        result = git_tag()
        self.assertIsNone(result)

    @patch("subprocess.check_output")
    @patch(f"{pythonpath}.git_tag", return_value="v1.0.0")
    def test_get_current_version_with_tag(self, mock_git_tag, mock_check_output):
        result = get_current_version()
        self.assertEqual(result, "v1.0.0")

    @patch("subprocess.check_output")
    @patch(f"{pythonpath}.git_tag", return_value=None)
    @patch(f"{pythonpath}.git_hash", return_value="abc123")
    def test_get_current_version_with_hash(
        self, mock_git_hash, mock_git_tag, mock_check_output
    ):
        result = get_current_version()
        self.assertEqual(result, "1.0.0-alpha-abc123")

    @patch("subprocess.check_output")
    @patch(f"{pythonpath}.git_tag", return_value=None)
    @patch(f"{pythonpath}.git_hash", return_value=None)
    def test_get_current_version_without_tag_or_hash(
        self, mock_git_hash, mock_git_tag, mock_check_output
    ):
        result = get_current_version()
        self.assertEqual(result, "1.0.0-alpha")

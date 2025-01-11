import unittest
import os
import tempfile

from v2v_toolkit.core.workspace import Workspace


class TestWorkspace(unittest.TestCase):

    def test_workspace_creation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir, workspace="test_workspace")

            self.assertTrue(os.path.isdir(workspace.root))
            self.assertTrue(os.path.isdir(workspace.workspace))

            self.assertEqual(workspace.root, temp_dir)
            self.assertEqual(
                workspace.workspace, os.path.join(temp_dir, "test_workspace")
            )

    def test_disk_memory_allocated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir, workspace="test_workspace")
            test_file = os.path.join(workspace.workspace, "test_file.txt")
            with open(test_file, "w") as f:
                f.write("Allocated memory")
            allocated_memory = workspace.disk_memory_allocated(workspace.workspace)
            self.assertGreater(allocated_memory, 0)
            self.assertEqual(allocated_memory, os.path.getsize(test_file))

    def test_disk_memory_allocated_skip_symlinks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir, workspace="test_workspace")
            test_file = os.path.join(workspace.workspace, "test_file.txt")
            with open(test_file, "w") as f:
                f.write("Allocated memory")
            os.symlink(test_file, os.path.join(workspace.workspace, "symlink.txt"))
            allocated_memory = workspace.disk_memory_allocated(workspace.workspace)
            self.assertGreater(allocated_memory, 0)
            self.assertEqual(allocated_memory, os.path.getsize(test_file))

    def test_cleanup_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rootcache = os.path.join(temp_dir, "cache")
            workspace = Workspace(root=rootcache, workspace="test_workspace")
            del workspace  # explicit deallocation
            self.assertFalse(os.path.isdir(os.path.join(rootcache, "test_workspace")))
            self.assertFalse(os.path.isdir(os.path.join(rootcache)))

    def test_workspace_repr(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir, workspace="test_workspace")

            expected_str = (
                f"root: {workspace.root} ({workspace.disk_memory_allocated(workspace.root)} bytes);"
                f"workspace: {workspace.workspace} ({workspace.disk_memory_allocated(workspace.workspace)} bytes);"
            )
            self.assertEqual(str(workspace), expected_str)
            self.assertEqual(repr(workspace), expected_str)

    def test_default_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Workspace(root=temp_dir)

            self.assertTrue(os.path.isdir(workspace.root))
            self.assertTrue(os.path.isdir(workspace.workspace))
            self.assertEqual(workspace.root, workspace.workspace)

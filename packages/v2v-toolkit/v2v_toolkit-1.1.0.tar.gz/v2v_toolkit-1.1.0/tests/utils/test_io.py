import json
import os
import tempfile
import unittest

import yaml

from v2v_toolkit.utils.io import (
    read_json,
    read_yaml,
    read_default,
    io_read,
    write_json,
    write_yaml,
    write_default,
    io_write,
)


class TestFileIO(unittest.TestCase):

    def setUp(self):
        """Set up temporary files and directories for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_read_json(self):
        filepath = os.path.join(self.temp_path, "test.json")
        data = {"key": "value"}
        with open(filepath, "w") as f:
            json.dump(data, f)
        self.assertEqual(read_json(filepath), data)

    def test_read_yaml(self):
        filepath = os.path.join(self.temp_path, "test.yaml")
        data = {"key": "value"}
        with open(filepath, "w") as f:
            yaml.dump(data, f)
        self.assertEqual(read_yaml(filepath), data)

    def test_read_default(self):
        filepath = os.path.join(self.temp_path, "test.txt")
        data = "This is a test."
        with open(filepath, "w") as f:
            f.write(data)
        self.assertEqual(read_default(filepath), data)

    def test_io_read_json(self):
        filepath = os.path.join(self.temp_path, "test.json")
        data = {"key": "value"}
        with open(filepath, "w") as f:
            json.dump(data, f)
        self.assertEqual(io_read(filepath), data)

    def test_io_read_yaml(self):
        filepath = os.path.join(self.temp_path, "test.yaml")
        data = {"key": "value"}
        with open(filepath, "w") as f:
            yaml.dump(data, f)
        self.assertEqual(io_read(filepath), data)

    def test_io_read_default(self):
        filepath = os.path.join(self.temp_path, "test.txt")
        data = "This is a test."
        with open(filepath, "w") as f:
            f.write(data)
        self.assertEqual(io_read(filepath), data)

    def test_io_read_missing_file(self):
        filepath = os.path.join(self.temp_path, "nonexistent.txt")
        with self.assertRaises(FileNotFoundError):
            io_read(filepath)

    def test_io_read_not_a_file(self):
        with self.assertRaises(ValueError):
            io_read(self.temp_path)  # Directory, not a file

    def test_write_json(self):
        filepath = os.path.join(self.temp_path, "test.json")
        data = {"key": "value"}
        write_json(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(json.load(f), data)

    def test_write_json_auto_add_extension(self):
        filepath = os.path.join(self.temp_path, "test")
        data = {"key": "value"}
        write_json(filepath, data)
        expected = filepath + ".json"
        with open(expected, "r") as fd:
            self.assertEqual(json.load(fd), data)

    def test_write_yaml(self):
        filepath = os.path.join(self.temp_path, "test.yaml")
        data = {"key": "value"}
        write_yaml(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(yaml.safe_load(f), data)

    def test_write_yaml_auto_add_extension(self):
        filepath = os.path.join(self.temp_path, "test")
        data = {"key": "value"}
        write_yaml(filepath, data)
        expected = filepath + ".yaml"
        with open(expected, "r") as fd:
            self.assertEqual(yaml.safe_load(fd), data)

    def test_write_default(self):
        filepath = os.path.join(self.temp_path, "test.txt")
        data = "This is a test."
        write_default(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), data)

    def test_io_write_json(self):
        filepath = os.path.join(self.temp_path, "test.json")
        data = {"key": "value"}
        io_write(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(json.load(f), data)

    def test_io_write_yaml(self):
        filepath = os.path.join(self.temp_path, "test.yaml")
        data = {"key": "value"}
        io_write(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(yaml.safe_load(f), data)

    def test_io_write_default(self):
        filepath = os.path.join(self.temp_path, "test.txt")
        data = "This is a test."
        io_write(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), data)

    def test_io_write_overwrite(self):
        filepath = os.path.join(self.temp_path, "test.txt")
        initial_data = "Initial data."
        new_data = "New data."
        io_write(filepath, initial_data)
        with self.assertRaises(FileExistsError):
            io_write(filepath, new_data)
        io_write(filepath, new_data, overwrite=True)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), new_data)

    def test_io_write_unsupported_extension(self):
        filepath = os.path.join(self.temp_path, "test.unsupported")
        data = "This is a test."
        io_write(filepath, data)
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), data)

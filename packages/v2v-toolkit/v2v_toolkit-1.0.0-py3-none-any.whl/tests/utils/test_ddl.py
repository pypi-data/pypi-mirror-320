import unittest
import tempfile
import os
import pathlib
from v2v_toolkit.utils.dll import dynamic_loading
from v2v_toolkit.exceptions import V2VGraphError


class TestDynamicLoading(unittest.TestCase):

    def test_dynamic_loading_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = pathlib.Path(temp_dir).joinpath("module", "submodule")
            os.makedirs(module_path, exist_ok=True)

            class_code = """
class DDL_Class:
    def __init__(self):
        self.name = "MyClass"
"""
            class_file = module_path.joinpath("ddl_class.py")
            with open(class_file, "w") as f:
                f.write(class_code)

            cls = "module.submodule.ddl_class.DDL_Class"
            result = dynamic_loading(cls, temp_dir)

            self.assertTrue(result().__class__.__name__ == "DDL_Class")

    def test_dynamic_loading_class_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = pathlib.Path(temp_dir) / "module" / "submodule"
            os.makedirs(module_path, exist_ok=True)

            class_code = """
class MyClassTypo:
    def __init__(self):
        self.name = "AnotherClass"
"""
            class_file = module_path / "myclasstypo.py"
            with open(class_file, "w") as f:
                f.write(class_code)

            cls = "module.submodule.MyClass"
            with self.assertRaises(V2VGraphError):
                dynamic_loading(cls, temp_dir)

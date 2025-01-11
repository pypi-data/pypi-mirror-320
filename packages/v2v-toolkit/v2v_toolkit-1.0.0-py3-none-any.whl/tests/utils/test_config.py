import unittest

from v2v_toolkit.utils.config import ConfigBaseStruct


class TestConfig(unittest.TestCase):
    def test_default_max_cache_memory_is_1gb(self):
        conf = ConfigBaseStruct(caching=True)
        self.assertEqual(conf.max_cache_size, 1024 * 1024 * 1024)

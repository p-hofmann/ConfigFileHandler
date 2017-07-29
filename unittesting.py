__author__ = 'hofmann'

import os
import unittest
from configparserwrapper import ConfigParserWrapper


class DefaultConfigParserWrapper(unittest.TestCase):
    test_config = 'unittest_example.cfg'
    log_file_path = 'unittest_log.txt'

    def setUp(self):
        self.cfg = ConfigParserWrapper(logfile=DefaultConfigParserWrapper.log_file_path, verbose=False)
        self.cfg.read(DefaultConfigParserWrapper.test_config)

    def tearDown(self):
        self.cfg = None
        if os.path.exists(DefaultConfigParserWrapper.log_file_path):
            os.remove(DefaultConfigParserWrapper.log_file_path)


class TestConfigParserMethods(DefaultConfigParserWrapper):
    def test_valid_input(self):
        list_of_options = {
            "values": ["string", "integer", "float", "empty", "bool"],
            "path": ["local", "home", "absolute"]
            }
        self.assertIsNone(self.cfg.validate_sections(list_of_options.keys()))

        test_array = [
            # [section, option, arguments, assertions, expected_result]
            ["values", "string", {}, self.assertIsInstance, str],
            ["values", "integer", {"is_digit": True}, self.assertIsInstance, int],
            ["values", "float", {"is_digit": True}, self.assertIsInstance, float],
            ["values", "empty", {}, self.assertIsNone, None],
            ["values", "bool", {"is_boolean": True}, self.assertIsInstance, bool],
            ["path", "local", {"is_path": True}, self.assertIsInstance, str],
            ["path", "home", {"is_path": True}, self.assertIsInstance, str],
            [None, "home", {"is_path": True}, self.assertIsInstance, str],
            ["path", "absolute", {"is_path": True}, self.assertIsInstance, str],
        ]

        for test in test_array:
            section, options, kargs, assertion, expected_result = test
            assertion(self.cfg.get_value(options, section, **kargs), expected_result)

    def test_invalid_input(self):
        list_of_options = {
            "values": ["string", "integer", "float", "empty", "bool"],
            "path": ["local", "home", "absolute"]
            }
        self.assertIsNone(self.cfg.validate_sections(list_of_options.keys()))

        test_array = [
            # [section, option, arguments, assertions, expected_result]
            ["values", "string", {"is_digit": True}, self.assertIsNone, None],
            ["values", "string", {"is_boolean": True}, self.assertIsNone, None],
            ["values", "string", {"is_digit": True}, self.assertIsNone, None],

            ["values", "integer", {"is_boolean": True}, self.assertIsNone, None],
            ["values", "float", {"is_boolean": True}, self.assertIsNone, None],

            ["values", "empty", {}, self.assertIsNone, None],
            ["values", "empty", {"is_digit": True}, self.assertIsNone, None],
            ["values", "empty", {"is_boolean": True}, self.assertIsNone, None],
            ["values", "empty", {"is_path": True}, self.assertIsNone, None],

            ["values", "bool", {"is_digit": True}, self.assertIsNone, None],

            ["path", "local", {"is_digit": True}, self.assertIsNone, None],
            ["path", "local", {"is_boolean": True}, self.assertIsNone, None],
            ["path", "home", {"is_digit": True}, self.assertIsNone, None],
            ["path", "home", {"is_boolean": True}, self.assertIsNone, None],
            ["path", "absolute", {"is_digit": True}, self.assertIsNone, None],
            ["path", "absolute", {"is_boolean": True}, self.assertIsNone, None],
        ]

        for test in test_array:
            section, options, kargs, assertion, expected_result = test
            assertion(self.cfg.get_value(section, options, **kargs), expected_result)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigParserMethods)
    unittest.TextTestRunner(verbosity=2, buffer=True).run(suite)

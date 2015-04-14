__author__ = 'hofmann'
__verson__ = '0.0.4'

import os
import io
import sys
import unittest
from ConfigParser import SafeConfigParser
from loggingwrapper import LoggingWrapper


class ConfigParserWrapper(object):
	_boolean_states = {
		'yes': True, 'true': True, 'on': True,
		'no': False, 'false': False, 'off': False,
		'y': True, 't': True, 'n': False, 'f': False}

	def __init__(self, config_file, logfile=None, verbose=True):
		"""
			Wrapper for the SafeConfigParser class for easy use.

			@attention: config_file argument may be file path or stream.

			@param config_file: file handler or file path to a config file
			@type config_file: file or FileIO or basestring
			@param logfile: file handler or file path to a log file
			@type logfile: file or FileIO or None
			@param verbose: No stdout or stderr messages. Warnings and errors will be only logged to a file, if one is given
			@type verbose: bool

			@return: None
		"""
		assert isinstance(config_file, (file, io.FileIO, basestring))
		assert logfile is None or isinstance(logfile, (file, io.FileIO, basestring))

		if verbose:
			self._logger = LoggingWrapper("ConfigParserWrapper")
		else:
			self._logger = LoggingWrapper("ConfigParserWrapper", stream=None)

		if logfile:
			self._logger.set_log_file(logfile)

		self._config = SafeConfigParser()

		if isinstance(config_file, basestring) and not os.path.isfile(config_file):
			self._logger.error("Config file does not exist: '{}'".format(config_file))
			raise Exception("File does not exist")

		if isinstance(config_file, basestring):
			self._config.read(config_file)
			self._config_file_path = config_file
		elif isinstance(config_file, file):
			self._config.readfp(config_file)
			self._config_file_path = config_file.name
		else:
			self._logger.error("Invalid config file argument '{}'".format(config_file))
			raise Exception("Unknown argument")

	def validate_sections(self, list_sections):
		"""
			Validate a list of section names for availability.

			@param list_sections: list of section names
			@type list_sections: list of basestring

			@return: None if all valid, otherwise list of invalid sections
		"""
		assert isinstance(list_sections, list)
		invalid_sections = []
		for section in list_sections:
			if not self._config.has_section(section):
				invalid_sections.append(section)
		if len(invalid_sections) > 0:
			return invalid_sections
		return None

	def log_invalid_sections(self, list_sections):
		"""
			print out a list of invalid section names to log.

			@param list_sections: list of section names
			@type list_sections: list of basestring

			@return: None if all valid, otherwise list of invalid sections
		"""
		assert isinstance(list_sections, list)
		for section in list_sections:
			self._logger.warning("Invalid section '{}'".format(section))

	def get_value(self, section, option, is_digit=False, is_boolean=False, is_path=False, obligatory=True):
		"""
			get a value of an option in a specific section of the config file.

			@attention: Set obligatory to False if a section or option that does not exist is no error.

			@param section: name of section
			@type section: basestring
			@param option: name of option in a section
			@type option: basestring
			@param is_digit: value is a number and will be returned as such
			@type is_digit: bool
			@param is_boolean: value is bool and will be returned as True or False
			@type is_boolean: bool
			@param is_path: value is a path and will be returned as absolute path
			@type is_path: bool
			@param obligatory: Set False if a section or option that does not exist is no error
			@type obligatory: bool


			@return: None if not available or ''. Else: depends on given arguments
		"""
		assert isinstance(section, basestring)
		assert isinstance(option, basestring)
		assert isinstance(is_digit, bool)
		assert isinstance(is_boolean, bool)
		assert isinstance(obligatory, bool)
		assert isinstance(is_path, bool)
		if not self._config.has_section(section):
			if obligatory:
				self._logger.error("Invalid section '{}'".format(section))
			return None
		if not self._config.has_option(section, option):
			if obligatory:
				self._logger.error("Invalid option in '{}': {}".format(section, option))
			return None

		value = self._config.get(section, option)
		if value == '':
			if obligatory:
				self._logger.debug("Invalid value in '{}': {}".format(section, option))
			return None

		if is_digit:
			return self._string_to_digit(value)

		if is_boolean:
			return self._is_true(value)

		if is_path:
			return self._get_full_path(value)
		return value

	def _string_to_digit(self, value):
		"""
			parse string to an int or float.

			@param value: some string to be converted
			@type value: basestring

			@return: None if invalid, otherwise int or float
		"""
		assert isinstance(value, basestring)
		try:
			if '.' in value:
				return float(value)
			return int(value)
		except ValueError:
			self._logger.error("Invalid digit value '{}'".format(value))
			return None

	def _is_true(self, value):
		"""
			parse string to True or False.

			@param value: some string to be converted
			@type value: basestring

			@return: None if invalid, otherwise True or False
		"""
		assert isinstance(value, basestring)

		if value.lower() not in ConfigParserWrapper._boolean_states:
			self._logger.error("Invalid bool value '{}'".format(value))
			return None
		return ConfigParserWrapper._boolean_states[value.lower()]

	@staticmethod
	def _get_full_path(value):
		"""
			convert string to absolute normpath.

			@param value: some string to be converted
			@type value: basestring

			@return: absolute normpath
		"""
		assert isinstance(value, basestring)
		value = os.path.expanduser(value)
		value = os.path.normpath(value)
		value = os.path.abspath(value)
		return value


class TestStringMethods(unittest.TestCase):
	test_config = 'unittest_example.cfg'
	log_file_path = 'unittest_log.txt'

	def test_valid_input(self):
		with open(TestStringMethods.log_file_path, 'a') as file_handle_log:
			cfg = ConfigParserWrapper(TestStringMethods.test_config, logfile=file_handle_log, verbose=True)
			# with open(TestStringMethods.test_config) as file_handle:
			# 	cfg2 = ConfigParserWrapper(file_handle, logfile=TestStringMethods.log_file_path, verbose=True)

			self.assertIsInstance(cfg, ConfigParserWrapper)
			list_of_options = {
				"values": ["string", "integer", "float", "empty", "bool"],
				"path": ["local", "home", "absolute"]
				}
			self.assertIsNone(cfg.validate_sections(list_of_options.keys()))

			test_array = [
				# [section, option, arguments, assertions, expected_result]
				["values", "string", {}, self.assertIsInstance, basestring],
				["values", "integer", {"is_digit": True}, self.assertIsInstance, int],
				["values", "float", {"is_digit": True}, self.assertIsInstance, float],
				["values", "empty", {}, self.assertIsNone, None],
				["values", "bool", {"is_boolean": True}, self.assertIsInstance, bool],
				["path", "local", {"is_path": True}, self.assertIsInstance, basestring],
				["path", "home", {"is_path": True}, self.assertIsInstance, basestring],
				["path", "absolute", {"is_path": True}, self.assertIsInstance, basestring],
			]

			for test in test_array:
				section, options, kargs, assertion, expected_result = test
				assertion(cfg.get_value(section, options, **kargs), expected_result)

	def test_invalid_input(self):
		with open(TestStringMethods.test_config) as file_handle_cfg, open(TestStringMethods.log_file_path, 'a') as file_handle_log:
			cfg = ConfigParserWrapper(file_handle_cfg, logfile=file_handle_log, verbose=False)

			self.assertIsInstance(cfg, ConfigParserWrapper)
			list_of_options = {
				"values": ["string", "integer", "float", "empty", "bool"],
				"path": ["local", "home", "absolute"]
				}
			self.assertIsNone(cfg.validate_sections(list_of_options.keys()))

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
				assertion(cfg.get_value(section, options, **kargs), expected_result)


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
	unittest.TextTestRunner(verbosity=2, buffer=True).run(suite)

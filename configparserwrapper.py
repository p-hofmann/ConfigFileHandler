__author__ = 'hofmann'
__verson__ = '0.0.3'

import os
import sys
from ConfigParser import SafeConfigParser
from loggingwrapper import LoggingWrapper


class ConfigParserWrapper(object):
	_boolean_states = {
		'yes': True, 'true': True, 'on': True,
		'no': False, 'false': False, 'off': False,
		'y': True, 't': True, 'n': False, 'f': False}

	def __init__(self, config_file, logfile=None, verbose=True):
		assert isinstance(config_file, file) or isinstance(config_file, basestring)
		assert logfile is None or isinstance(logfile, file) or isinstance(logfile, basestring)

		self._logger = LoggingWrapper("ConfigParserWrapper", verbose=verbose)
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
		assert isinstance(list_sections, list)
		invalid_sections = []
		for section in list_sections:
			if not self._config.has_section(section):
				invalid_sections.append(section)
		if len(invalid_sections) > 0:
			return invalid_sections
		return None

	def print_invalid_sections(self, list_sections):
		assert isinstance(list_sections, list)
		for section in list_sections:
			self._logger.warning("Invalid section '{}'".format(section))

	def get_value(self, section, option, is_digit=False, is_boolean=False, is_path=False, obligatory=True):
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
		try:
			if '.' in value:
				return float(value)
			return int(value)
		except ValueError:
			self._logger.error("Invalid digit value '{}'".format(value))
			return None

	def _is_true(self, value):
		if value is None or not isinstance(value, basestring):
			return None

		if value.lower() not in ConfigParserWrapper._boolean_states:
			self._logger.error("Invalid bool value '{}'".format(value))
			return None
		return ConfigParserWrapper._boolean_states[value.lower()]

	@staticmethod
	def _get_full_path(value):
		assert isinstance(value, basestring)
		value = os.path.expanduser(value)
		value = os.path.normpath(value)
		value = os.path.abspath(value)
		return value


def test(cfg_path="test.cfg", log_path="log.txt"):
	assert cfg_path is None or (isinstance(cfg_path, basestring) and os.path.isfile(cfg_path))
	print "cfg 1"
	cfg1 = ConfigParserWrapper(cfg_path, logfile=log_path, verbose=True)
	testing(cfg1)

	print "\ncfg 2"
	with open(cfg_path) as file_handle:
		cfg2 = ConfigParserWrapper(file_handle, logfile=log_path, verbose=True)
	testing(cfg2)


def testing(cfg):
	assert isinstance(cfg, ConfigParserWrapper)
	list_of_sections =  ["s0", "s1", "s2"]
	list_of_options = ["v0", "v1", "v2"]
	invalid_sections = cfg.validate_sections(list_of_sections)
	if invalid_sections:
		cfg.print_invalid_sections(invalid_sections)
	print cfg.get_value("s2", "v1")
	for section in list_of_sections[:2]:
		for options in list_of_options:
			print "string:", cfg.get_value(section, options)
			print "digit:", cfg.get_value(section, options, is_digit=True)
			print "bool:", cfg.get_value(section, options, is_boolean=True)
			print "path:", cfg.get_value(section, options, is_path=True)

	for options in list_of_options:
		print "path:", cfg.get_value("p", options, is_path=True)

if __name__ == "__main__":
	if len(sys.argv) == 2:
		test(sys.argv[1])
	else:
		test()

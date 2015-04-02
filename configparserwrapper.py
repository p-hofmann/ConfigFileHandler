__author__ = 'hofmann'
__verson__ = '0.0.1'

import os
from ConfigParser import SafeConfigParser
from loggingwrapper import LoggingWrapper


class ConfigParserWrapper(object):
	_boolean_states = {
		'1': True, 'yes': True, 'true': True, 'on': True,
		'0': False, 'no': False, 'false': False, 'off': False,
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
		missing_sections = []
		for section in list_sections:
			if not self._config.has_section(section):
				missing_sections.append(section)
		if len(missing_sections) > 0:
			return missing_sections
		return False

	def print_invalid_sections(self, list_sections):
		for section in list_sections:
			self._logger.warning("Invalid section '{}'".format(section))

	def get_value(self, section, option, is_digit=False, is_boolean=False, obligatory=True):
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
			return None

		if is_digit:
			return self._string_to_digit(value)

		if is_boolean:
			return self._is_true(value)
		return value

	def _string_to_digit(self, value):
		try:
			if '.' in value:
				return float(value)
			return int(value)
		except ValueError:
			self._logger.error("Invalid digit value '{}'".format(value))
			return None

	def _is_true(self, value=''):
		if value is None or not isinstance(value, basestring):
			return None

		if value.lower() not in ConfigParserWrapper._boolean_states:
			self._logger.error("Invalid bool value '{}'".format(value))
			return None
		return ConfigParserWrapper._boolean_states[value.lower()]

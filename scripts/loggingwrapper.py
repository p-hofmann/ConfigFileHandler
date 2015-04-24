__author__ = 'hofmann'
__version__ = '0.0.7'

import sys
import io
import StringIO
import logging


class LoggingWrapper(object):
	CRITICAL = logging.CRITICAL
	FATAL = logging.CRITICAL
	ERROR = logging.ERROR
	WARNING = logging.WARNING
	WARN = logging.WARN
	INFO = logging.INFO
	DEBUG = logging.DEBUG
	NOTSET = logging.NOTSET

	_levelNames = logging._levelNames
	_map_logfile_handler = dict()

	def __init__(self, label="", verbose=True, message_format=None, date_format=None, stream=sys.stderr):
		"""
			Wrapper for the logging module for easy use.

			@attention: 'labels' are unique, LoggingWrapper with the same label will have the same streams!

			@param label: unique label for a LoggingWrapper
			@type label: basestring
			@param verbose: Not verbose means that only warnings and errors will be past to stream
			@type verbose: bool
			@param message_format: "%(asctime)s %(levelname)s: [%(name)s] %(message)s"
			@type message_format: basestring
			@param date_format: "%Y-%m-%d %H:%M:%S"
			@type date_format: basestring
			@param stream: To have no output at all, use "stream=None", stderr by default
			@type stream: file | FileIO | StringIO | None

			@return: None
			@rtype: None
		"""
		assert isinstance(label, basestring)
		assert isinstance(verbose, bool)
		assert message_format is None or isinstance(message_format, basestring)
		assert message_format is None or isinstance(date_format, basestring)
		assert stream is None or self._is_stream(stream)

		if message_format is None:
			message_format = "%(asctime)s %(levelname)s: [%(name)s] %(message)s"
		if date_format is None:
			date_format = "%Y-%m-%d %H:%M:%S"
		self.message_formatter = logging.Formatter(message_format, date_format)

		self._label = label
		self._logger = logging.getLogger(label)
		if label in LoggingWrapper._map_logfile_handler:
			return

		LoggingWrapper._map_logfile_handler[label] = None
		self._logger.setLevel(logging.DEBUG)
		if stream is not None:
			if verbose:
				self.add_log_stream(stream=stream, level=logging.INFO)
			else:
				self.add_log_stream(stream=stream, level=logging.WARNING)

	def __exit__(self, type, value, traceback):
		self.close()

	def __enter__(self):
		return self

	@staticmethod
	def _is_stream(stream):
		return isinstance(stream, (file, io.FileIO, StringIO.StringIO)) or stream.__class__ is StringIO.StringIO

	def get_label(self):
		return self._label

	def close(self):
		"""
			Close all logfile handler, unless given as stream.
			Remove all stream handler from handler list, stopping the log service

			@attention: only files opened by LoggingWrapper will be closed!
			If given as stream, logfiles will be kept open!

			@return: None
			@rtype: None
		"""
		list_of_handlers = list(self._logger.handlers)
		for item in list_of_handlers:
			self._logger.removeHandler(item)
		if self._label not in LoggingWrapper._map_logfile_handler:
			return

		logfile_handler = LoggingWrapper._map_logfile_handler.pop(self._label)
		if logfile_handler is not None:
			logfile_handler.close()

	def info(self, message):
		"""
			Log general informative messages, that might be useful for the user.

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.info(message)

	def error(self, message):
		"""
			Log an significant error that occured.

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.error(message)

	def debug(self, message):
		"""
			Log a message for debugging puposes only.

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.debug(message)

	def critical(self, message):
		"""
			Log a catastrophic error!

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.critical(message)

	def exception(self, message):
		"""
			Log a exception with messages, that might be useful for the user.

			@attention: Call this only after an exception occurred, like in a "try..except.."!

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.exception(message)

	def warning(self, message):
		"""
			Log warning messages, that the user should pay attention to.

			@param message: Message to be logged
			@type message: basestring

			@return: None
			@rtype: None
		"""
		self._logger.warning(message)

	def set_level(self, level):
		"""
			Set the minimum level of messages to be logged.

			Level of Log Messages
			CRITICAL	50
			ERROR	40
			WARNING	30
			INFO	20
			DEBUG	10
			NOTSET	0

			@param level: minimum level of messages to be logged
			@type level: int or long

			@return: None
			@rtype: None
		"""
		assert level in self._levelNames

		list_of_handlers = self._logger.handlers
		for handler in list_of_handlers:
			handler.setLevel(level)

	def add_log_stream(self, stream=sys.stderr, level=logging.INFO):
		"""
			Add a stream where messages are outputted to.

			@param stream: stderr/stdout or a file stream
			@type stream: file | FileIO | StringIO
			@param level: minimum level of messages to be logged
			@type level: int | long

			@return: None
			@rtype: None
		"""
		assert self._is_stream(stream)
		# assert isinstance(stream, (file, io.FileIO))
		assert level in self._levelNames

		err_handler = logging.StreamHandler(stream)
		err_handler.setFormatter(self.message_formatter)
		err_handler.setLevel(level)
		self._logger.addHandler(err_handler)

	def set_log_file(self, log_file, mode='w', level=logging.INFO):
		"""
			Add a stream where messages are outputted to.

			@attention: file stream will only be closed if a file path is given!

			@param log_file: file stream or file path of logfile
			@type log_file: file | FileIO | StringIO | basestring
			@param mode: opening mode for logfile, if a file path is given
			@type mode: basestring
			@param level: minimum level of messages to be logged
			@type level: int or long

			@return: None
			@rtype: None
		"""
		assert isinstance(log_file, basestring) or self._is_stream(log_file)
		assert level in self._levelNames

		if LoggingWrapper._map_logfile_handler[self._label] is not None:
			self._logger.removeHandler(LoggingWrapper._map_logfile_handler[self._label])
			LoggingWrapper._map_logfile_handler[self._label].close()
			LoggingWrapper._map_logfile_handler[self._label] = None

		if isinstance(log_file, (file, io.FileIO)):
			self.add_log_stream(stream=log_file, level=level)
			return

		try:
			err_handler_file = logging.FileHandler(log_file, mode)
			err_handler_file.setFormatter(self.message_formatter)
			err_handler_file.setLevel(level)
			self._logger.addHandler(err_handler_file)
			LoggingWrapper._map_logfile_handler[self._label] = err_handler_file
		except Exception:
			sys.stderr.write("[LoggingWrapper] Could not open '{}' for logging\n".format(log_file))
			return
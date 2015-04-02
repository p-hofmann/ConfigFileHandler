__author__ = 'hofmann'
__verson__ = '0.0.3'

import sys
import logging


class LoggingWrapper(object):

	def __init__(self, label="", verbose=True, message_format=None, date_format=None, stream=sys.stderr):
		assert isinstance(label, basestring)
		assert isinstance(verbose, bool)
		assert message_format is None or isinstance(message_format, basestring)
		assert message_format is None or isinstance(date_format, basestring)

		if message_format is None:
			message_format = "%(asctime)s %(levelname)s: [%(name)s] %(message)s"

		if date_format is None:
			date_format = "%Y-%m-%d %H:%M:%S"

		self.message_formatter = logging.Formatter(message_format, date_format)

		self._logger = logging.getLogger(label)
		self._logger.setLevel(logging.DEBUG)
		if stream is not None:
			self.add_log_stream(stream=stream, verbose=verbose)
		self._handler_log_file = None

	def __exit__(self, type, value, traceback):
		self.close()

	def __enter__(self):
		return self

	def close(self):
		list_of_handlers = list(self._logger.handlers)
		for item in list_of_handlers:
			self._logger.removeHandler(item)
			if self._handler_log_file is not None:
				self._handler_log_file.close()
				self._handler_log_file = None

	def info(self, message):
		self._logger.info(message)

	def error(self, message):
		self._logger.error(message)

	def debug(self, message):
		self._logger.debug(message)

	def critical(self, message):
		self._logger.critical(message)

	def exception(self, message):
		self._logger.exception(message)

	def warning(self, message):
		self._logger.warning(message)

	def set_level(self, level):
		self._logger.setLevel(level)

	def add_log_stream(self, stream=sys.stderr, verbose=True):
		err_handler = logging.StreamHandler(stream)
		err_handler.setFormatter(self.message_formatter)
		if verbose:
			err_handler.setLevel(logging.INFO)
		else:
			err_handler.setLevel(logging.WARNING)
		self._logger.addHandler(err_handler)

	def set_log_file(self, log_file, mode='w'):
		assert isinstance(log_file, file) or isinstance(log_file, basestring)

		if self._handler_log_file is not None:
			self._logger.removeHandler(self._handler_log_file)
			self._handler_log_file.close()
			self._handler_log_file = None

		if isinstance(log_file, file):
			self.add_log_stream(stream=log_file)
			return

		try:
			err_handler_file = logging.FileHandler(log_file, mode)
			err_handler_file.setFormatter(self.message_formatter)
			err_handler_file.setLevel(logging.INFO)
			self._logger.addHandler(err_handler_file)
		except Exception:
			sys.stderr.write("[LoggingWrapper] Could not open '{}' for logging\n".format(log_file))
			return


def test(log_file_path=None):
	assert log_file_path is None or isinstance(log_file_path, basestring)
	log1 = LoggingWrapper("l1")
	if log_file_path:
		log1.set_log_file(log_file_path)
	log1.info("Test1")
	log2 = LoggingWrapper("l2")
	if log_file_path:
		log2.set_log_file(log_file_path, 'a')
	log1.info("Test2")
	log2.info("Test1")
	log2.info("Test2")
	log1.close()
	log2.close()

	if log_file_path:
		log3 = LoggingWrapper("l3", stream=None)
		with open(log_file_path, 'a') as log_file_handle:
			log3.set_log_file(log_file_handle)
			log3.info("Test1")
			list_of_methods = [log3.info, log3.debug, log3.warning, log3.error, log3.info, log3.critical, log3.exception]
			count = 2
			for methods in list_of_methods:
				methods("Test{}".format(count))
				count += 1
		log3.close()

if __name__ == "__main__":
	if len(sys.argv) == 2:
		test(sys.argv[1])
	else:
		test()

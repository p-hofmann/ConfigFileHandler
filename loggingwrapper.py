__author__ = 'hofmann'
__verson__ = '0.0.1'

import sys
import logging


class LoggingWrapper(object):

	def __init__(self, label="", verbose=True, message_format=None, stream=sys.stderr):
		assert isinstance(label, basestring)
		assert isinstance(verbose, bool)
		assert message_format is None or isinstance(message_format, basestring)

		self.message_formatter = logging.Formatter("%(asctime)s %(levelname)s: [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")

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
		self._logger.warning(self, message)

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

	def set_log_file(self, filename, mode='w'):
		assert isinstance(filename, basestring)
		if self._handler_log_file is not None:
			self._logger.removeHandler(self._handler_log_file)
			self._handler_log_file.close()
			self._handler_log_file = None
		try:
			err_handler_file = logging.FileHandler(filename, mode)
			err_handler_file.setFormatter(self.message_formatter)
			err_handler_file.setLevel(logging.INFO)
			self._logger.addHandler(err_handler_file)
		except Exception:
			sys.stderr.write("[LoggingWrapper] Could not open '{}' for logging\n".format(filename))
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

if __name__ == "__main__":
	if len(sys.argv) == 2:
		test(sys.argv[1])
	else:
		test()

#! /usr/bin/env python
import argparse
import json
import time

from systemd import journal

from kafka import KafkaProducer


def _convert_trivial(x):
	return x


def _convert_monotonic(x):
	return x[0]


BASIC_CONVERTERS = {
	'MESSAGE_ID': _convert_trivial,
	'_MACHINE_ID': _convert_trivial,
	'_BOOT_ID': _convert_trivial,
	'_SOURCE_REALTIME_TIMESTAMP': _convert_trivial,
	'__REALTIME_TIMESTAMP': _convert_trivial,
	'_SOURCE_MONOTONIC_TIMESTAMP': _convert_monotonic,
	'__MONOTONIC_TIMESTAMP': _convert_monotonic
}

SINCE_DB = "./sincedb"


class JournaldStream(object):
	messages_steps = 100
	logs_topic_name = "logs"
	kafka_sleep = 1

	def __init__(self, kafka_hosts, journal_path="/run/log/journal"):
		self.kafka_hosts = self._force_type_value(list, kafka_hosts)

		self.producer = KafkaProducer(
				bootstrap_servers=self.kafka_hosts,
				value_serializer=lambda v: json.dumps(v).encode('utf-8'))

		self.reader = journal.Reader(path=journal_path, converters=BASIC_CONVERTERS)
		self.cursor = ""
		self.read_messages = 0

	@staticmethod
	def _force_type_value(type_want, variable):
		assert type_want is type(variable)
		return variable

	def _save_cursor(self):
		if self.cursor != "":
			with open(SINCE_DB, 'w') as f:
				f.write(self.cursor)
		else:
			print "invalid cursor"

	def _get_cursor(self):
		try:
			with open(SINCE_DB, 'r') as f:
				self.cursor = f.read()
				return True if self.cursor else False
		except IOError:
			return False

	def _stream_to_seek(self):
		if self._get_cursor():
			print "using saved cursor \"%s\"" % self.cursor
			self.reader.seek_cursor(self.cursor)
			self.reader.get_next()
		else:
			print "using new cursor"

		for log in self.reader:
			self._kafka_send(log)

		print "seeked journal after %d messages" % self.read_messages

	def _stream_poller(self):
		i = 0
		print "start polling realtime messages"
		while self.reader.get_events():
			i += 1
			if self.reader.process() == journal.APPEND:
				for log in self.reader:
					self._kafka_send(log)
			else:
				time.sleep(self.kafka_sleep)
			self._periodic_sleep_task(i)

	def stream(self):
		self._stream_to_seek()
		self._stream_poller()

	def _periodic_send_task(self):
		if self.read_messages % self.messages_steps == 0:
			print "read %d messages, process flush" % self.read_messages
			ts = time.time()
			self.producer.flush()
			print "flush done in %d" % (time.time() - ts)

	@staticmethod
	def _periodic_sleep_task(nb_message):
		pass

	@staticmethod
	def _filter(full_log):
		filter_data = {}

		for key in full_log:
			new = key
			if new != "__CURSOR":
				while new[0] == "_":
					new = new[1:]
				filter_data[new.lower()] = full_log[key]
		return filter_data

	def _kafka_send(self, full_log):
		filter_data = self._filter(full_log)
		self.producer.send(self.logs_topic_name, filter_data)
		self.cursor = full_log["__CURSOR"]
		self._save_cursor()
		self.read_messages += 1
		self._periodic_send_task()

	def close(self):
		print "closing journald.Reader"
		self.reader.close()
		print "closing kafka connection"
		self.producer.close()


def comma_list(string):
	return string.split(',')


def fast_arg_parsing():
	args = argparse.ArgumentParser()
	args.add_argument("kafka_hosts", type=comma_list,
					  help="Kafka hosts \"HOST:PORT,HOST:PORT\" or HOST:PORT")

	args.add_argument("--sincedb_path", type=str, default="/run/log/journal/sincedb",
					  help="SinceDB path for Journald cursor")

	return args.parse_args().kafka_hosts, args.parse_args().sincedb_path


if __name__ == "__main__":
	hosts, SINCE_DB = fast_arg_parsing()
	print "hosts: %s sincedb: %s" % (hosts, SINCE_DB)
	js = JournaldStream(hosts)
	try:
		js.stream()
	except KeyboardInterrupt:
		js.close()
		print "gracefully close, read %d messages" % js.read_messages

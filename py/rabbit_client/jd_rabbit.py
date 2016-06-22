import json

from systemd import journal

import pika


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


class JournaldStream(object):
    messages_steps = 100
    rabbit_sleep = 2
    rabbit_data_events = 30
    logs_queue_name = "logs"
    cursor_path = "sincedb"
    rabbit_props = pika.BasicProperties(content_type='application/json', delivery_mode=2)

    def __init__(self, rabbit_host, rabbit_port=5672, journal_path="/run/log/journal"):
        self.rabbit_host = self._force_type_value(str, rabbit_host)
        self.rabbit_port = self._force_type_value(int, rabbit_port)
        self.connection = self._connect(self.rabbit_host, self.rabbit_port)
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue=self.logs_queue_name, durable=True)

        self.reader = journal.Reader(path=journal_path, converters=BASIC_CONVERTERS)
        self.cursor = ""
        self.read_messages = 0

    @staticmethod
    def _connect(host, port):
        return pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))

    @staticmethod
    def _force_type_value(type_want, variable):
        assert type_want is type(variable)
        return variable

    def _save_cursor(self):
        if self.cursor != "":
            with open(self.cursor_path, 'w') as f:
                f.write(self.cursor)
        else:
            print "invalid cursor"

    def _get_cursor(self):
        with open(self.cursor_path, 'r') as f:
            self.cursor = f.read()
            return True if self.cursor else False

    def _stream_to_seek(self):
        if self._get_cursor():
            print "using saved cursor \"%s\"" % self.cursor
            self.reader.seek_cursor(self.cursor)
            self.reader.get_next()
        else:
            print "using new cursor"

        for log in self.reader:
            self._rabbit_publish(log)

        print "seeked journal after %d messages" % self.read_messages

    def _stream_poller(self):
        i = 0
        print "start polling realtime messages"
        while self.reader.get_events():
            i += 1
            if self.reader.process() == journal.APPEND:
                for log in self.reader:
                    self._rabbit_publish(log)
            else:
                self.connection.sleep(self.rabbit_sleep)
            self._periodic_sleep_task(i)

    def stream(self):
        self._stream_to_seek()
        self._stream_poller()

    def _periodic_publish_task(self):
        if self.read_messages % self.messages_steps == 0:
            print "read %d messages, process data events" % self.read_messages
            self.connection.process_data_events()

    def _periodic_sleep_task(self, i):
        if i % self.rabbit_data_events == 0:
            print "read %d messages, time to process data events" % self.read_messages
            self.connection.process_data_events()

    def _rabbit_publish(self, full_log):
        try:
            if self.channel.basic_publish('', self.logs_queue_name, json.dumps(full_log), properties=self.rabbit_props):
                self.cursor = full_log["__CURSOR"]
                self._save_cursor()
                self.read_messages += 1
                self._periodic_publish_task()
            else:
                raise RuntimeError("BasicPublish failed")
        except pika.exceptions.ConnectionClosed:
            print "Rabbit timeout, reconnect..."
            self.connection = self._connect(self.rabbit_host, self.rabbit_port)

    def close(self):
        print "closing journald.Reader"
        self.reader.close()
        print "closing rabbitmq connection"
        self.connection.close()


if __name__ == "__main__":
    js = JournaldStream("localhost")
    try:
        js.stream()
    except KeyboardInterrupt:
        print "gracefully close, read %d messages" % js.read_messages
        js.close()

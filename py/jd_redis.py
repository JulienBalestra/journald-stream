import json
import sys

import os
import select

from systemd import journal
import redis


class JournaldStream(object):
    db_log_index = 0
    db_cursor_index = 1
    messages_steps = 1000

    def __init__(self, redis_host, redis_port=6379, journal_path="/run/log/journal"):
        self.redis_host = self._force_type_value(str, redis_host)
        self.redis_port = self._force_type_value(int, redis_port)
        self.log_db = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=self.db_log_index)
        self.cursor_db = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=self.db_cursor_index)
        self.reader = journal.Reader(path=journal_path)
        self.cursor = ""
        self.poll = select.poll()
        self.read_messages = 0
        self.redis_messages = 0

    @staticmethod
    def _force_type_value(type_want, variable):
        assert type_want is type(variable)
        return variable

    def _redis_connection_error(self):
        os.write(2,
                 "redis.exceptions.ConnectionError to %s:%d "
                 "session read_messages: %d, last update redis_messages: %d \n" % (
                     self.redis_host, self.redis_port, self.read_messages, self.redis_messages))
        sys.stderr.flush()
        self.close()
        exit(2)

    def count_redis_messages(self, update=False):
        if update:
            try:
                self.redis_messages = self.log_db.info("keyspace")["db%d" % self.db_log_index]["keys"]
            except redis.exceptions.ConnectionError:
                self._redis_connection_error()
            except KeyError:
                self.redis_messages = 0
        return self.redis_messages

    def _get_cursor(self):
        machine = self.reader.get_previous()["_MACHINE_ID"]
        self.cursor = self.cursor_db.get(machine)
        return self.cursor

    def _stream_to_seek(self):
        if self._get_cursor():
            print "using saved cursor \"%s\"" % self.cursor
            self.reader.seek_cursor(self.cursor)
            self.reader.get_next()
        else:
            print "using new cursor"
        for log in self.reader:
            self._redis_set(log)
        print "seeked journal after %d messages" % self.read_messages

    def _stream_poller(self):
        print "start polling realtime messages"
        self.poll.register(self.reader, self.reader.get_events())
        while self.poll.poll():
            if self.reader.process() == journal.APPEND:
                for log in self.reader:
                    self._redis_set(log)

    def _display_redis_status(self):
        print json.dumps(self.log_db.info())

    def stream(self):
        self._display_redis_status()
        self.count_redis_messages(update=True)
        self._stream_to_seek()
        self.count_redis_messages(update=True)
        self._stream_poller()

    def _displayer(self):
        if self.read_messages % self.messages_steps == 0:
            print "read %d messages, %d messages in redis" % (
                self.read_messages, self.count_redis_messages(update=True))
            if self.read_messages % (self.messages_steps * 10) == 0:
                self._display_redis_status()

    def _redis_set(self, full_log):
        try:
            self.log_db.set(name=full_log["__CURSOR"], value=full_log)
            self.cursor_db.set(name=full_log["_MACHINE_ID"], value=full_log["__CURSOR"])
            self.read_messages += 1
            self._displayer()
        except redis.exceptions.ConnectionError:
            self._redis_connection_error()

    def close(self):
        print "closing journald.Reader"
        self.reader.close()


if __name__ == "__main__":
    js = JournaldStream("localhost")
    try:
        js.stream()
    except KeyboardInterrupt:
        print "gracefully close, read %d messages, %d messages in redis" % (
            js.read_messages, js.count_redis_messages(update=True))
        js.close()

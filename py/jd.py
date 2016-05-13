import sys

import os
import select

from systemd import journal
import redis


class JournaldStream(object):
    def __init__(self, redis_host, redis_port=6379, journal_path="/run/log/journal"):
        self.redis_host = self._force_type_value(str, redis_host)
        self.redis_port = self._force_type_value(int, redis_port)
        self.log_db = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=0)
        self.cursor_db = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=1)
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
                self.redis_messages = len(self.log_db.keys("*"))
            except redis.exceptions.ConnectionError:
                self._redis_connection_error()
        return self.redis_messages

    def _get_cursor(self):
        machine = self.reader.get_previous()["_MACHINE_ID"]
        self.cursor = self.cursor_db.get(machine)
        return self.cursor

    def _stream_to_seek(self):
        if self._get_cursor():
            print "using saved cursor"
            self.reader.seek_cursor(self.cursor)
            self.reader.get_next()
        else:
            print "using new cursor"
        for log in self.reader:
            self._redis_set(log)
        print "seeked after %d messages" % self.read_messages

    def _stream_poller(self):
        print "polling"
        self.poll.register(self.reader, self.reader.get_events())
        while self.poll.poll():
            if self.reader.process() == journal.APPEND:
                for log in self.reader:
                    self._redis_set(log)

    def stream(self):
        self.count_redis_messages(update=True)
        self._stream_to_seek()
        self.count_redis_messages(update=True)
        self._stream_poller()

    def _redis_set(self, full_log):
        try:
            self.log_db.set(name=full_log["__CURSOR"], value=full_log)
            self.cursor_db.set(name=full_log["_MACHINE_ID"], value=full_log["__CURSOR"])
            self.read_messages += 1
            if self.read_messages % 1000 == 0:
                print "read %d messages, %d messages in redis" % (
                    self.read_messages, self.count_redis_messages(update=True))
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

import datetime


class ExpiringBool(object):
    def __init__(self, period):
        self._value = None

        self._period = period
        self._timedelta = datetime.timedelta(seconds=self._period)
        self._last_set = None

    def _is_stale(self, timestamp):
        if self._last_set is None:
            raise ValueError('cannot get before set')

        return timestamp - self._last_set > self._timedelta

    @property
    def stale(self):
        return self._is_stale(datetime.datetime.now())

    @property
    def value(self):
        return self._value if not self._is_stale(datetime.datetime.now()) else not self._value

    def _set_value(self, value, timestamp):
        if not isinstance(value, bool):
            raise TypeError('expected {0} got {1}'.format(
                type(True), type(value)
            ))

        self._value = value
        self._last_set = timestamp

    @value.setter
    def value(self, value):
        self._set_value(value, datetime.datetime.now())

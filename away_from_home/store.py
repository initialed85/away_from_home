class Store(object):
    def __init__(self, heartbeat):
        self._heartbeat = heartbeat

        self._data = {}

    def set(self, key, value):
        self._data.update({key: value})

    def get(self, key):
        return self._data.get(key)

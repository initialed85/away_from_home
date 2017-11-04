import inspect
import time
from logging import getLogger

from zmote.connector import TCPTransport, Connector


class Aircon(object):
    def __init__(self, ip, retries):
        self._connector = Connector(
            transport=TCPTransport(
                ip=ip,
            )
        )

        self._retries = retries

        self._on_message = '1:1,0,37000,1,1,1'
        self._off_message = '1:1,0,37000,1,1,0'

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); ip={1}, retries={2}'.format(
            inspect.currentframe().f_code.co_name, repr(ip), retries
        ))

    def connect(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._connector.connect()

    def on(self, sleep=1):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        for i in range(0, self._retries):
            self._connector.send(self._on_message)
            time.sleep(sleep)

    def off(self, sleep=1):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        for i in range(0, self._retries):
            self._connector.send(self._off_message)
            time.sleep(sleep)

    def disconnect(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._connector.disconnect()


_FUJITSU_ON = '1:1,0,37000,1,1,123,61,16,15,15,16,15,46,15,15,16,46,16,16,14,15,15,17,14,46,15,46,15,16,14,16,15,16,15,45,15,46,16,15,15,15,15,16,16,16,14,15,15,16,16,14,15,15,16,16,14,15,16,16,14,16,15,15,15,46,15,15,15,15,15,15,16,15,15,16,15,17,13,17,14,48,14,15,15,17,14,15,15,15,15,17,13,46,15,46,15,48,14,46,15,46,15,46,15,15,15,15,15,15,15,46,15,16,16,14,16,14,15,15,16,16,14,16,15,17,13,16,15,47,15,45,15,16,16,14,15,48,14,16,15,16,15,16,14,16,15,46,15,16,15,15,15,46,15,17,14,16,15,15,15,16,15,16,15,17,14,16,15,17,14,16,15,15,15,16,15,15,15,15,15,16,15,15,15,16,15,16,15,16,14,16,15,16,14,16,15,16,15,16,15,15,15,16,15,15,15,15,16,14,15,16,16,14,16,14,15,16,15,17,14,16,15,16,15,16,15,16,15,16,15,17,14,16,15,46,15,46,15,46,15,16,16,47,13,16,15,46,15,3692'
_FUJITSU_OFF = '1:1,0,37000,1,1,121,61,15,15,15,16,16,45,15,16,15,45,15,17,14,16,15,15,16,45,15,46,15,15,16,15,16,14,16,45,15,46,15,15,15,15,16,14,15,15,16,15,15,15,16,14,15,16,15,16,15,15,16,15,15,15,16,15,15,46,16,16,14,16,15,16,15,15,16,15,16,14,16,14,16,45,15,17,14,15,15,15,16,16,13,46,16,15,16,14,16,15,15,17,13,16,15,16,15,3692'


class FujitsuAircon(Aircon):
    def __init__(self, *args, **kwargs):
        super(FujitsuAircon, self).__init__(*args, **kwargs)

        self._on_message = _FUJITSU_ON
        self._off_message = _FUJITSU_OFF

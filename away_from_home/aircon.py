import inspect
import time
from logging import getLogger

from zmote.connector import TCPTransport, Connector
from zmote.discoverer import active_discover_zmotes


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


class AutoDiscoveringAircon(object):
    def __init__(self, uuid, retries, aircon_class):
        self._uuid = uuid
        self._retries = retries
        self._aircon_class = aircon_class

        self._aircon = None

    def _acquire_aircon(self):
        for i in range(0, 5):
            zmote = active_discover_zmotes(uuid_to_look_for=self._uuid).get(self._uuid)

            if zmote is None:
                time.sleep(1)
                continue

            self._aircon = self._aircon_class(
                ip=zmote['IP'],
                retries=self._retries
            )
            self._aircon.connect()

            return

    def _release_aircon(self):
        self._aircon.disconnect()
        self._aircon = None

    def on(self):
        self._acquire_aircon()
        self._aircon.on()
        self._release_aircon()

    def off(self):
        self._acquire_aircon()
        self._aircon.off()
        self._release_aircon()


_FUJITSU_ON = '1:1,0,37000,1,1,122,62,15,16,15,16,15,46,15,16,15,46,15,16,15,16,15,16,15,46,15,46,15,16,15,16,15,16,15,46,15,46,15,16,15,16,14,16,15,16,15,16,14,16,15,16,15,16,14,16,15,16,15,16,15,16,15,16,15,46,15,16,15,16,15,16,15,16,15,16,14,16,15,16,15,46,15,16,15,16,15,16,15,16,15,16,15,46,15,46,15,46,15,46,15,46,15,46,15,16,15,16,15,16,14,47,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,46,15,46,15,16,15,16,15,47,14,16,15,16,15,16,15,16,15,46,15,16,15,16,15,46,15,16,15,16,15,16,15,16,15,16,14,16,15,16,15,46,15,46,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,14,16,15,16,15,16,14,16,15,16,15,16,14,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,46,15,46,15,16,15,46,15,16,15,46,15,16,15,46,15,3692'
_FUJITSU_OFF = '1:1,0,37000,1,1,122,62,15,16,15,16,15,46,15,16,15,46,15,16,14,16,15,16,15,46,15,47,14,16,15,16,15,16,14,47,15,47,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,46,15,16,15,16,15,16,15,16,15,16,15,16,15,16,15,46,15,16,15,16,15,16,15,16,15,46,15,16,15,16,15,16,15,16,15,16,14,16,15,3692'


class FujitsuAircon(Aircon):
    def __init__(self, *args, **kwargs):
        super(FujitsuAircon, self).__init__(*args, **kwargs)

        self._on_message = _FUJITSU_ON
        self._off_message = _FUJITSU_OFF


class AutoDiscoveringFujitsuAircon(AutoDiscoveringAircon):
    def __init__(self, uuid, retries):
        super(AutoDiscoveringFujitsuAircon, self).__init__(
            uuid=uuid,
            retries=retries,
            aircon_class=FujitsuAircon,
        )

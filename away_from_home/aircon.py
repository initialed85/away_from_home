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
        ip = active_discover_zmotes(uuid_to_look_for=self._uuid).get(self._uuid)['IP']
        self._aircon = self._aircon_class(
            ip=ip,
            retries=self._retries
        )
        self._aircon.connect()

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


_FUJITSU_ON = '1:1,0,37000,1,1,123,61,16,15,15,16,15,46,15,15,16,46,16,16,14,15,15,17,14,46,15,46,15,16,14,16,15,16,15,45,15,46,16,15,15,15,15,16,16,16,14,15,15,16,16,14,15,15,16,16,14,15,16,16,14,16,15,15,15,46,15,15,15,15,15,15,16,15,15,16,15,17,13,17,14,48,14,15,15,17,14,15,15,15,15,17,13,46,15,46,15,48,14,46,15,46,15,46,15,15,15,15,15,15,15,46,15,16,16,14,16,14,15,15,16,16,14,16,15,17,13,16,15,47,15,45,15,16,16,14,15,48,14,16,15,16,15,16,14,16,15,46,15,16,15,15,15,46,15,17,14,16,15,15,15,16,15,16,15,17,14,16,15,17,14,16,15,15,15,16,15,15,15,15,15,16,15,15,15,16,15,16,15,16,14,16,15,16,14,16,15,16,15,16,15,15,15,16,15,15,15,15,16,14,15,16,16,14,16,14,15,16,15,17,14,16,15,16,15,16,15,16,15,16,15,17,14,16,15,46,15,46,15,46,15,16,16,47,13,16,15,46,15,3692'
_FUJITSU_OFF = '1:1,0,37000,1,1,121,61,15,15,15,16,16,45,15,16,15,45,15,17,14,16,15,15,16,45,15,46,15,15,16,15,16,14,16,45,15,46,15,15,15,15,16,14,15,15,16,15,15,15,16,14,15,16,15,16,15,15,16,15,15,15,16,15,15,46,16,16,14,16,15,16,15,15,16,15,16,14,16,14,16,45,15,17,14,15,15,15,16,16,13,46,16,15,16,14,16,15,15,17,13,16,15,16,15,3692'


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

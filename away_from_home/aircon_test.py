import datetime
import unittest

from hamcrest import assert_that, equal_to
from mock import patch, call, MagicMock

from away_from_home.aircon import Aircon, FujitsuAircon, _FUJITSU_ON, _FUJITSU_OFF, AutoDiscoveringAircon

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)

_IP = '192.168.137.90'
_RETRIES = 2
_UUID = 'CI00a1b2c3'


class AirconTest(unittest.TestCase):
    @patch('away_from_home.aircon.TCPTransport')
    @patch('away_from_home.aircon.Connector')
    def setUp(self, connector, transport):
        self._subject = Aircon(
            ip=_IP,
            retries=_RETRIES,
        )

        assert_that(
            transport.mock_calls,
            equal_to([
                call(ip=_IP),
            ])
        )

        assert_that(
            connector.mock_calls,
            equal_to([
                call(transport=transport())
            ])
        )

    def test_connect(self):
        self._subject.connect()

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.connect()
            ])
        )

    def test_on(self):
        self._subject.on(sleep=0)

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.send('1:1,0,37000,1,1,1'),
                call.send('1:1,0,37000,1,1,1'),
            ])
        )

    def test_off(self):
        self._subject.off(sleep=0)

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.send('1:1,0,37000,1,1,0'),
                call.send('1:1,0,37000,1,1,0'),
            ])
        )

    def test_disconnect(self):
        self._subject.disconnect()

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.disconnect()
            ])
        )


class AutoDiscoveringAirconTest(unittest.TestCase):
    def setUp(self):
        self._subject = AutoDiscoveringAircon(
            uuid='CI00a1b2c3',
            retries=2,
            aircon_class=MagicMock(),
        )

    @patch('away_from_home.aircon.active_discover_zmotes')
    def test_acquire_aircon(self, active_discover_zmotes):
        active_discover_zmotes.return_value = {_UUID: {
            'IP': '192.168.1.12',
            'UUID': 'CI00a1b2c3',
            'Make': 'zmote.io',
            'Config-URL': 'http://192.168.1.12',
            'Model': 'ZV-2',
            'Type': 'ZMT2',
            'Revision': '2.1.4'
        }}

        assert_that(
            self._subject._acquire_aircon(),
            equal_to(None)
        )

        assert_that(
            active_discover_zmotes.mock_calls,
            equal_to([
                call(uuid_to_look_for=_UUID)
            ])
        )

        assert_that(
            self._subject._aircon_class.mock_calls,
            equal_to([
                call(ip='192.168.1.12', retries=2),
                call().connect(),
            ])
        )

        assert_that(
            self._subject._aircon,
            equal_to(self._subject._aircon_class())
        )

    def test_release_aircon(self):
        mock_aircon = MagicMock()
        self._subject._aircon = mock_aircon

        self._subject._release_aircon()

        assert_that(
            mock_aircon.mock_calls,
            equal_to([
                call.disconnect()
            ])
        )

        assert_that(
            self._subject._aircon,
            equal_to(None)
        )

    def test_on(self):
        self._subject._acquire_aircon = MagicMock()
        self._subject._aircon = MagicMock()
        self._subject._release_aircon = MagicMock()

        self._subject.on()

        assert_that(
            self._subject._acquire_aircon.mock_calls,
            equal_to([
                call()
            ])
        )

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.on()
            ])
        )

        assert_that(
            self._subject._release_aircon.mock_calls,
            equal_to([
                call()
            ])
        )

    def test_off(self):
        self._subject._acquire_aircon = MagicMock()
        self._subject._aircon = MagicMock()
        self._subject._release_aircon = MagicMock()

        self._subject.off()

        assert_that(
            self._subject._acquire_aircon.mock_calls,
            equal_to([
                call()
            ])
        )

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.off()
            ])
        )

        assert_that(
            self._subject._release_aircon.mock_calls,
            equal_to([
                call()
            ])
        )


class FujitsuAirconTest(unittest.TestCase):
    @patch('away_from_home.aircon.TCPTransport')
    @patch('away_from_home.aircon.Connector')
    def setUp(self, connector, transport):
        self._subject = FujitsuAircon(
            ip=_IP,
            retries=_RETRIES,
        )

        assert_that(
            transport.mock_calls,
            equal_to([
                call(ip=_IP),
            ])
        )

        assert_that(
            connector.mock_calls,
            equal_to([
                call(transport=transport())
            ])
        )

    def test_on(self):
        self._subject.on(sleep=0)

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.send(_FUJITSU_ON),
                call.send(_FUJITSU_ON),
            ])
        )

    def test_off(self):
        self._subject.off(sleep=0)

        assert_that(
            self._subject._connector.mock_calls,
            equal_to([
                call.send(_FUJITSU_OFF),
                call.send(_FUJITSU_OFF),
            ])
        )

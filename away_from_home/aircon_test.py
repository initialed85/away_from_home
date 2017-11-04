import datetime
import unittest

from hamcrest import assert_that, equal_to
from mock import patch, call

from away_from_home.aircon import Aircon, FujitsuAircon, _FUJITSU_ON, _FUJITSU_OFF

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)

_IP = '192.168.137.90'
_RETRIES = 2


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

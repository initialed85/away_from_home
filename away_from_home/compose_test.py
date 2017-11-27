import datetime
import logging
import unittest

from hamcrest import assert_that, equal_to
from mock import MagicMock, call

from away_from_home.composer import Composer

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)


class ComposerTest(unittest.TestCase):
    def setUp(self):
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )

        logger = logging.getLogger(Composer.__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        self._subject = Composer(
            weather=MagicMock(),
            aircon=MagicMock(),
            on_threshold=29,
            off_threshold=27,
        )

        self._subject._weather.mock_calls = []
        self._subject._aircon.mock_calls = []

    def test_check_above_on_threshold_true(self):
        self._subject._weather.apparent_temperature = 30

        assert_that(
            self._subject._check_above_on_threshold(),
            equal_to(True)
        )

    def test_check_above_on_threshold_false(self):
        self._subject._weather.apparent_temperature = 26

        assert_that(
            self._subject._check_above_on_threshold(),
            equal_to(False)
        )

    def test_turn_aircon_on(self):
        self._subject._turn_aircon_on()

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.on()
            ])
        )

    def test_turn_aircon_on_already_on(self):
        self._subject._last_action = 'on'

        self._subject._turn_aircon_on()

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([])
        )

    def test_turn_aircon_off(self):
        self._subject._turn_aircon_off()

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.off()
            ])
        )

    def test_turn_aircon_off_already_off(self):
        self._subject._last_action = 'off'

        self._subject._turn_aircon_off()

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([])
        )

    def test_run_above_on_threshold(self):
        self._subject._check_above_on_threshold = MagicMock()
        self._subject._check_above_on_threshold.return_value = True
        self._subject._turn_aircon_on = MagicMock()

        self._subject.run()

        assert_that(
            self._subject._turn_aircon_on.mock_calls,
            equal_to([
                call()
            ])
        )

    def test_run_above_on_threshold_aircon_already_on(self):
        self._subject._check_above_on_threshold = MagicMock()
        self._subject._check_above_on_threshold.return_value = True
        self._subject._turn_aircon_on = MagicMock()
        self._subject._last_action = 'on'

        self._subject.run()

        assert_that(
            self._subject._turn_aircon_on.mock_calls,
            equal_to([])
        )

    def test_run_above_off_threshold(self):
        self._subject._check_above_on_threshold = MagicMock()
        self._subject._check_above_on_threshold.return_value = False
        self._subject._check_below_off_threshold = MagicMock()
        self._subject._check_below_off_threshold.return_value = True
        self._subject._turn_aircon_off = MagicMock()

        self._subject.run()

        assert_that(
            self._subject._turn_aircon_off.mock_calls,
            equal_to([
                call()
            ])
        )

    def test_run_above_off_threshold_aircon_already_off(self):
        self._subject._check_above_on_threshold = MagicMock()
        self._subject._check_above_on_threshold.return_value = False
        self._subject._check_below_off_threshold = MagicMock()
        self._subject._check_below_off_threshold.return_value = True
        self._subject._turn_aircon_off = MagicMock()
        self._subject._last_action = 'off'

        self._subject.run()

        assert_that(
            self._subject._turn_aircon_off.mock_calls,
            equal_to([])
        )

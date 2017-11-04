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
            threshold=25,
            debounce=datetime.timedelta(
                minutes=30
            )
        )

    def test_check_above_threshold_true(self):
        self._subject._weather.temperature = 26

        assert_that(
            self._subject._check_above_threshold(),
            equal_to(True)
        )

    def test_check_above_threshold_false(self):
        self._subject._weather.temperature = 24

        assert_that(
            self._subject._check_above_threshold(),
            equal_to(False)
        )

    def test_turn_aircon_on(self):
        self._subject._turn_aircon_on(_TEST_TIMESTAMP)

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.on()
            ])
        )

        assert_that(
            self._subject._last_action_timestamp,
            equal_to(_TEST_TIMESTAMP)
        )

    def test_turn_aircon_on_already_on(self):
        self._subject._aircon_is_on = True

        self._subject._turn_aircon_on(_TEST_TIMESTAMP)

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([])
        )

        assert_that(
            self._subject._last_action_timestamp,
            equal_to(None)
        )

    def test_turn_aircon_off(self):
        self._subject._turn_aircon_off(_TEST_TIMESTAMP)

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([
                call.off()
            ])
        )

        assert_that(
            self._subject._last_action_timestamp,
            equal_to(_TEST_TIMESTAMP)
        )

    def test_turn_aircon_off_already_off(self):
        self._subject._aircon_is_on = False

        self._subject._turn_aircon_off(_TEST_TIMESTAMP)

        assert_that(
            self._subject._aircon.mock_calls,
            equal_to([])
        )

        assert_that(
            self._subject._last_action_timestamp,
            equal_to(None)
        )

    def test_check_need_to_defer_first(self):
        assert_that(
            self._subject._check_need_to_defer(_TEST_TIMESTAMP),
            equal_to(False)
        )

    def test_check_need_to_defer_true(self):
        self._subject._last_action_timestamp = _TEST_TIMESTAMP
        assert_that(
            self._subject._check_need_to_defer(_TEST_TIMESTAMP),
            equal_to(True)
        )

    def test_check_need_to_defer_false(self):
        self._subject._last_action_timestamp = _TEST_TIMESTAMP - self._subject._debounce
        assert_that(
            self._subject._check_need_to_defer(_TEST_TIMESTAMP),
            equal_to(False)
        )

    def test_run_normal_on(self):
        self._subject._check_need_to_defer = MagicMock()
        self._subject._check_need_to_defer.return_value = False
        self._subject._check_above_threshold = MagicMock()
        self._subject._check_above_threshold.return_value = True
        self._subject._turn_aircon_on = MagicMock()
        self._subject._turn_aircon_off = MagicMock()

        self._subject.run(_TEST_TIMESTAMP)

        assert_that(
            self._subject._turn_aircon_on.mock_calls,
            equal_to([
                call(_TEST_TIMESTAMP)
            ])
        )

    def test_run_normal_on_deferred(self):
        self._subject._check_need_to_defer = MagicMock()
        self._subject._check_need_to_defer.return_value = True
        self._subject._check_above_threshold = MagicMock()
        self._subject._check_above_threshold.return_value = True
        self._subject._turn_aircon_on = MagicMock()
        self._subject._turn_aircon_off = MagicMock()

        self._subject.run(_TEST_TIMESTAMP)

        assert_that(
            self._subject._turn_aircon_on.mock_calls,
            equal_to([])
        )

    def test_run_normal_off(self):
        self._subject._check_need_to_defer = MagicMock()
        self._subject._check_need_to_defer.return_value = False
        self._subject._check_above_threshold = MagicMock()
        self._subject._check_above_threshold.return_value = False
        self._subject._turn_aircon_on = MagicMock()
        self._subject._turn_aircon_off = MagicMock()

        self._subject.run(_TEST_TIMESTAMP)

        assert_that(
            self._subject._turn_aircon_off.mock_calls,
            equal_to([
                call(_TEST_TIMESTAMP)
            ])
        )

    def test_run_normal_off_deferred(self):
        self._subject._check_need_to_defer = MagicMock()
        self._subject._check_need_to_defer.return_value = True
        self._subject._check_above_threshold = MagicMock()
        self._subject._check_above_threshold.return_value = True
        self._subject._turn_aircon_on = MagicMock()
        self._subject._turn_aircon_off = MagicMock()

        self._subject.run(_TEST_TIMESTAMP)

        assert_that(
            self._subject._turn_aircon_off.mock_calls,
            equal_to([])
        )

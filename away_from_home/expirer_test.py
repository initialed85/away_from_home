import datetime
import unittest

from hamcrest import assert_that, equal_to, calling, raises, not_

from away_from_home.expirer import ExpiringBool

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)


class ExpiringBoolTest(unittest.TestCase):
    def setUp(self):
        self._subject = ExpiringBool(
            period=5
        )

    def test_is_stale_first(self):
        assert_that(
            calling(self._subject._is_stale).with_args(_TEST_TIMESTAMP),
            raises(ValueError)
        )

    def test_is_stale_set_false(self):
        self._subject._last_set = _TEST_TIMESTAMP - datetime.timedelta(seconds=4)

        assert_that(
            self._subject._is_stale(_TEST_TIMESTAMP),
            equal_to(False)
        )

    def test_is_stale_set_true(self):
        self._subject._last_set = _TEST_TIMESTAMP - datetime.timedelta(seconds=8)

        assert_that(
            self._subject._is_stale(_TEST_TIMESTAMP),
            equal_to(True)
        )

    def test_value_getter(self):
        self._subject._value = True
        self._subject._last_set = datetime.datetime.now()

        assert_that(
            self._subject.value,
            equal_to(True)
        )

    def test_set_value_wrong_type(self):
        assert_that(
            calling(self._subject._set_value).with_args(None, _TEST_TIMESTAMP),
            raises(TypeError)
        )

    def test_set_value(self):
        self._subject._set_value(True, _TEST_TIMESTAMP)

        assert_that(
            self._subject._value,
            equal_to(True)
        )

        assert_that(
            self._subject._last_set,
            equal_to(_TEST_TIMESTAMP)
        )

    def test_value_setter(self):
        self._subject.value = True

        assert_that(
            self._subject._value,
            equal_to(True)
        )

        assert_that(
            self._subject._last_set,
            not_(equal_to(None))
        )

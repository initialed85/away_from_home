import datetime
import unittest

from hamcrest import assert_that, equal_to, close_to
from mock import patch, MagicMock, call

from away_from_home.weather import Weather, get_apparent_temperature

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)

_OWM_KEY = 'd59f6762bf26d648a301f363cd84405f'
_LAT = -31.923145
_LON = 115.894571
_CACHE_PERIOD = 300


class FunctionsTest(unittest.TestCase):
    def test_get_apparent_temperature(self):
        assert_that(
            get_apparent_temperature(32.0, 25.6, 0.0),
            close_to(32.0, 0.00001)
        )


class WeatherTest(unittest.TestCase):
    @patch('away_from_home.weather.ExpiringBool')
    @patch('away_from_home.weather.OWM')
    def setUp(self, owm, expiring_bool):
        self._subject = Weather(
            owm_key=_OWM_KEY,
            lat=_LAT,
            lon=_LON,
            cache_period=_CACHE_PERIOD,
        )

        assert_that(
            owm.mock_calls,
            equal_to([
                call(_OWM_KEY)
            ])
        )

        assert_that(
            expiring_bool.mock_calls,
            equal_to([
                call(300)
            ])
        )

    def test_check_need_to_update_not_yet_updated(self):
        assert_that(
            self._subject._check_need_to_update(),
            equal_to(True)
        )

    def test_check_need_to_update_not_needed(self):
        self._subject._weather = MagicMock()
        self._subject._need_to_update.value = False

        assert_that(
            self._subject._check_need_to_update(),
            equal_to(False)
        )

    def test_check_need_to_update_needed(self):
        self._subject._weather = MagicMock()
        self._subject._need_to_update.value = True

        assert_that(
            self._subject._check_need_to_update(),
            equal_to(True)
        )

    def test_update(self):
        self._subject._check_need_to_update = MagicMock()
        self._subject._check_need_to_update.return_value = True

        weather = self._subject._owm.weather_at_coords.return_value.get_weather.return_value

        weather.get_temperature.return_value = {
            'temp': 32
        }
        weather.get_humidity.return_value = 25
        weather.get_wind.return_value = {
            'speed': 5,
            'deg': 330
        }
        weather.get_sunrise_time.return_value = 1509743779
        weather.get_sunset_time.return_value = 1509792245

        self._subject._update()

        assert_that(
            self._subject._check_need_to_update.mock_calls,
            equal_to([
                call()
            ])
        )

        assert_that(
            self._subject._owm.mock_calls,
            equal_to([
                call.weather_at_coords(lat=-31.923145, lon=115.894571),
                call.weather_at_coords().get_weather(),
                call.weather_at_coords().get_weather().get_temperature(unit='celsius'),
                call.weather_at_coords().get_weather().get_humidity(),
                call.weather_at_coords().get_weather().get_wind(),
                call.weather_at_coords().get_weather().get_sunrise_time(timeformat='unix'),
                call.weather_at_coords().get_weather().get_sunset_time(timeformat='unix'),
            ])
        )

        assert_that(
            self._subject._temperature,
            equal_to(32.0)
        )
        assert_that(
            self._subject._humidity,
            equal_to(25.0)
        )
        assert_that(
            self._subject._wind_speed,
            equal_to(5.0)
        )
        assert_that(
            self._subject._apparent_temperature,
            equal_to(28.41)
        )
        assert_that(
            self._subject._sunrise,
            equal_to(datetime.datetime.strptime(
                '2017-11-04 05:16:19', '%Y-%m-%d %H:%M:%S'
            ))
        )
        assert_that(
            self._subject._sunset,
            equal_to(datetime.datetime.strptime(
                '2017-11-04 18:44:05', '%Y-%m-%d %H:%M:%S'
            ))
        )

        assert_that(
            self._subject._need_to_update.value,
            equal_to(False)
        )

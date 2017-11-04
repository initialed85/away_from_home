import datetime
import inspect
from logging import getLogger

from pyowm import OWM

from expirer import ExpiringBool


class Weather(object):
    def __init__(self, owm_key, lat, lon, cache_period):
        self._lat = lat
        self._lon = lon

        self._owm = OWM(owm_key)

        self._need_to_update = ExpiringBool(cache_period)

        self._weather = None

        self._humidity = None
        self._temperature = None
        self._sunrise = None
        self._sunset = None

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); owm_key={1}, lat={2}, lon={3}, cache_period={4}'.format(
            inspect.currentframe().f_code.co_name, repr(owm_key), lat, lon, cache_period
        ))

    def _check_need_to_update(self):
        need_to_update = self._weather is None or self._need_to_update.value

        self._logger.debug('{0}(); need_to_update={1}'.format(
            inspect.currentframe().f_code.co_name, need_to_update
        ))

        return need_to_update

    def _update(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        if self._check_need_to_update():
            self._weather = self._owm.weather_at_coords(
                lat=self._lat,
                lon=self._lon,
            ).get_weather()

            self._temperature = self._weather.get_temperature(unit='celsius').get('temp')
            self._humidity = self._weather.get_humidity()
            self._sunrise = datetime.datetime.fromtimestamp(self._weather.get_sunrise_time(timeformat='unix'))
            self._sunset = datetime.datetime.fromtimestamp(self._weather.get_sunset_time(timeformat='unix'))

            self._logger.debug('{0}(); temperature={1}, humidity={2}, sunrise={3}, sunset={4}'.format(
                inspect.currentframe().f_code.co_name, self._temperature, self._humidity, self._sunrise, self._sunset
            ))

            self._need_to_update.value = False

    @property
    def temperature(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._update()
        temperature = self._temperature

        self._logger.debug('{0}(); temperature={1}'.format(
            inspect.currentframe().f_code.co_name, temperature
        ))

        return temperature

    @property
    def humidity(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._update()
        humidity = self._humidity

        self._logger.debug('{0}(); humidity={1}'.format(
            inspect.currentframe().f_code.co_name, humidity
        ))

        return humidity

    @property
    def sunrise(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._update()
        sunrise = self._sunrise

        self._logger.debug('{0}(); sunrise={1}'.format(
            inspect.currentframe().f_code.co_name, sunrise
        ))

        return sunrise

    @property
    def sunset(self):
        self._logger.debug('{0}()'.format(
            inspect.currentframe().f_code.co_name
        ))

        self._update()
        sunset = self._sunset

        self._logger.debug('{0}(); sunset={1}'.format(
            inspect.currentframe().f_code.co_name, sunset
        ))

        return sunset

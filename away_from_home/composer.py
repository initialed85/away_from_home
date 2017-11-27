import inspect
from logging import getLogger


class Composer(object):
    def __init__(self, weather, aircon, on_threshold, off_threshold):
        self._weather = weather
        self._aircon = aircon
        self._on_threshold = on_threshold
        self._off_threshold = off_threshold

        self._last_action = None

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); weather={1}, aircon={2}, on_threshold={3}, off_threshold={4}'.format(
            inspect.currentframe().f_code.co_name, self._weather, self._aircon, self._on_threshold, self._off_threshold
        ))

    def _check_above_on_threshold(self):
        temperature = self._weather.apparent_temperature
        above_on_threshold = temperature >= self._on_threshold

        self._logger.debug('{0}(); temperature={1}, above_on_threshold={2}'.format(
            inspect.currentframe().f_code.co_name, temperature, above_on_threshold
        ))

        return above_on_threshold

    def _check_below_off_threshold(self):
        temperature = self._weather.apparent_temperature
        below_off_threshold = temperature <= self._off_threshold

        self._logger.debug('{0}(); temperature={1}, below_off_threshold={2}'.format(
            inspect.currentframe().f_code.co_name, temperature, below_off_threshold
        ))

        return below_off_threshold

    def _turn_aircon_on(self):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._last_action is None or self._last_action != 'on':
            self._aircon.on()
            self._last_action = 'on'

    def _turn_aircon_off(self):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._last_action is None or self._last_action != 'off':
            self._aircon.off()
            self._last_action = 'off'

    def run(self):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._check_above_on_threshold():
            self._logger.debug('{0}(); temperature above on threshold'.format(inspect.currentframe().f_code.co_name))
            if self._last_action != 'on':
                self._logger.debug('{0}(); turning aircon on'.format(inspect.currentframe().f_code.co_name))
                self._turn_aircon_on()
        elif self._check_below_off_threshold():
            self._logger.debug('{0}(); temperature below off threshold'.format(inspect.currentframe().f_code.co_name))
            if self._last_action != 'off':
                self._logger.debug('{0}(); turning aircon off'.format(inspect.currentframe().f_code.co_name))
                self._turn_aircon_off()

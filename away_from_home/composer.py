import datetime
import inspect
from logging import getLogger


class Composer(object):
    def __init__(self, weather, aircon, threshold, debounce):
        self._weather = weather
        self._aircon = aircon
        self._threshold = threshold
        self._debounce = debounce

        self._last_action_timestamp = None
        self._last_action = None

        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('{0}(); weather={1}, aircon={2}, threshold={3}, debounce={4}'.format(
            inspect.currentframe().f_code.co_name, self._weather, self._aircon, self._threshold, self._debounce
        ))

    def _check_above_threshold(self):
        temperature = self._weather.temperature
        above_temperature_threshold = temperature >= self._threshold

        self._logger.debug('{0}(); temperature={1}, above_temperature_threshold={2}'.format(
            inspect.currentframe().f_code.co_name, temperature, above_temperature_threshold
        ))

        return above_temperature_threshold

    def _turn_aircon_on(self, timestamp):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._last_action is None or self._last_action is not 'on':
            self._aircon.on()
            self._last_action_timestamp = timestamp
            self._last_action = 'on'

    def _turn_aircon_off(self, timestamp):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._last_action is None or self._last_action is not 'off':
            self._aircon.off()
            self._last_action_timestamp = timestamp
            self._last_action = 'off'

    def _check_need_to_defer(self, timestamp):
        no_last_action = self._last_action_timestamp is None
        time_since_last_action = timestamp - self._last_action_timestamp if not no_last_action else None
        time_difference_greater_than_debounce = time_since_last_action >= self._debounce if not no_last_action else None

        need_to_defer = False if no_last_action else not time_difference_greater_than_debounce

        self._logger.debug(
            '{0}(); no_last_action={1}, time_since_last_action={2}, time_difference_greater_than_debounce={3}, need_to_defer={4}'.format(
                inspect.currentframe().f_code.co_name,
                no_last_action,
                time_since_last_action,
                time_difference_greater_than_debounce,
                need_to_defer
            )
        )

        return need_to_defer

    def run(self, timestamp=None):
        timestamp = timestamp if timestamp is not None else datetime.datetime.now()

        if self._check_above_threshold():
            if not self._check_need_to_defer(timestamp):
                self._turn_aircon_on(timestamp)
            return True
        else:
            if not self._check_need_to_defer(timestamp):
                self._turn_aircon_off(timestamp)
            return False

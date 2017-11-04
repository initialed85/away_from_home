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
        self._aircon_is_on = None

        self._logger = getLogger(self.__class__.__name__)

    def _check_above_threshold(self):
        temperature = self._weather.temperature
        above_temperature_threshold = temperature >= self._threshold

        self._logger.debug('{0}(); temperature={1}, above_temperature_threshold={2}'.format(
            inspect.currentframe().f_code.co_name, temperature, above_temperature_threshold
        ))

        return above_temperature_threshold

    def _turn_aircon_on(self, timestamp):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._aircon_is_on is None or not self._aircon_is_on:
            self._aircon.on()
            self._aircon_is_on = True
            self._last_action_timestamp = timestamp

    def _turn_aircon_off(self, timestamp):
        self._logger.debug('{0}()'.format(inspect.currentframe().f_code.co_name))

        if self._aircon_is_on is None or self._aircon_is_on:
            self._aircon.off()
            self._aircon_is_on = False
            self._last_action_timestamp = timestamp

    def _check_need_to_defer(self, timestamp):
        no_last_action = self._last_action_timestamp is None
        time_since_last_action = timestamp - self._last_action_timestamp if not no_last_action else None
        time_difference_greater_than_debounce = time_since_last_action >= self._debounce if not no_last_action else None

        need_to_defer = False if no_last_action else not time_difference_greater_than_debounce

        self._logger.debug(
            '{0}(); no_last_action={1}, time_since_last_action={2}, time_difference_greater_than_debouce={3}, need_to_defer={4}'.format(
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

        if not self._check_need_to_defer(timestamp):
            if self._check_above_threshold():
                self._turn_aircon_on(timestamp)
                return True
            else:
                self._turn_aircon_off(timestamp)
                return False

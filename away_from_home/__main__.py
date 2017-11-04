import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from zmote.discoverer import active_discover_zmotes

from aircon import FujitsuAircon
from composer import Composer
from config import *
from weather import Weather

if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    for cls in [Weather.__name__, FujitsuAircon.__name__, Composer.__name__, 'apscheduler.scheduler', 'apscheduler.executors.default']:
        logger = logging.getLogger(cls)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    weather = Weather(
        owm_key=OWM_KEY,
        lat=LAT,
        lon=LON,
        cache_period=CACHE_PERIOD,
    )

    zmotes = active_discover_zmotes(uuid_to_look_for=UUID)

    zmote = zmotes.get(UUID)
    if zmote is None:
        raise ValueError('zmote {0} was not in returned zmotes'.format(UUID))

    aircon = FujitsuAircon(
        ip=zmote.get('IP'),
        retries=RETRIES,
    )
    aircon.connect()

    composer = Composer(
        weather=weather,
        aircon=aircon,
        threshold=THRESHOLD,
        debounce=DEBOUNCE,
    )

    sched = BlockingScheduler()

    sched.add_job(composer.run, 'cron', minute=CRON_MINUTES)

    while 1:
        try:
            sched.start()
        except KeyboardInterrupt:
            break

    aircon.disconnect()

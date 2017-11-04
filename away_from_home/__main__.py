import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from zmote.discoverer import active_discover_zmotes

from aircon import FujitsuAircon
from composer import Composer
from config import *
from heartbeat import Heartbeat
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

    logger = logging.getLogger('away_from_home')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    logger.debug('creating Weather object')
    weather = Weather(
        owm_key=OWM_KEY,
        lat=LAT,
        lon=LON,
        cache_period=CACHE_PERIOD,
    )

    logger.debug('discovering zmotes')
    zmotes = active_discover_zmotes(uuid_to_look_for=UUID)

    zmote = zmotes.get(UUID)
    if zmote is None:
        raise ValueError('zmote {0} was not in returned zmotes'.format(UUID))

    logger.debug('got {0}'.format(zmote))

    logger.debug('creating FujitsuAircon object')
    aircon = FujitsuAircon(
        ip=zmote.get('IP'),
        retries=RETRIES,
    )
    aircon.connect()

    logger.debug('creating Composer object')
    composer = Composer(
        weather=weather,
        aircon=aircon,
        threshold=THRESHOLD,
        debounce=DEBOUNCE,
    )

    logger.debug('creating Heartbeat object with priority {0}'.format(HA_PRIORITY))
    heartbeat = Heartbeat(priority=HA_PRIORITY)
    heartbeat.start()

    logger.debug('sleeping for a second')
    time.sleep(1)

    logger.debug('creating BackgroundScheduler object')
    sched = BackgroundScheduler()
    sched.start()

    composer_run_job = None

    while 1:
        try:
            if heartbeat.active and composer_run_job is None:
                composer_run_job = sched.add_job(composer.run, 'cron', minute=CRON_MINUTES)
            elif not heartbeat.active and composer_run_job is not None:
                sched.remove_all_jobs()

            time.sleep(1)
        except KeyboardInterrupt:
            break

    heartbeat.stop()

    sched.shutdown()

    aircon.disconnect()

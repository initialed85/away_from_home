import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from aircon import FujitsuAircon, StaticFujitsuAircon
from composer import Composer
from config import *
from heartbeat import Heartbeat
from weather import Weather

if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    class_names_to_log = [
        Weather.__name__,
        'Connector',
        'Transport',
        'Discoverer',
        FujitsuAircon.__name__,
        Composer.__name__,
        Heartbeat.__name__,
        'apscheduler.scheduler',
        'apscheduler.executors.default',
    ]

    for cls in class_names_to_log:
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

    logger.debug('creating StaticFujitsuAircon object')
    aircon = StaticFujitsuAircon(
        ip=IP,
        retries=RETRIES,
    )

    logger.debug('creating Composer object')
    composer = Composer(
        weather=weather,
        aircon=aircon,
        on_threshold=ON_THRESHOLD,
        off_threshold=OFF_THRESHOLD
    )

    logger.debug('creating Heartbeat object with priority {0}'.format(HA_PRIORITY))
    heartbeat = Heartbeat(priority=HA_PRIORITY)
    heartbeat.start()

    logger.debug('sleeping for 5 seconds')
    time.sleep(5)

    logger.debug('creating BackgroundScheduler object')
    sched = BackgroundScheduler()
    sched.start()

    composer_run_job = None

    while 1:
        try:
            if heartbeat.active and composer_run_job is None:
                logger.info('going into active')
                composer_run_job = sched.add_job(composer.run, 'cron', second=CRON_SECONDS)
            elif not heartbeat.active and composer_run_job is not None:
                logger.info('going into standby')
                sched.remove_all_jobs()
                composer_run_job = None

            time.sleep(1)
        except KeyboardInterrupt:
            break

    heartbeat.stop()

    sched.shutdown()

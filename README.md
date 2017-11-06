# away_from_home

This repo contains some fairly brittle Python scripts for automating an old Fujitsu aircon via a 
[http://zmote.io/](zmote.io) device using [my zmote module](https://github.com/initialed85/zmote).

The weather tie-in comes from [OpenWeatherMap](http://www.openweathermap.com/) using 
[csarpa's pyowm](https://github.com/csparpa/pyowm) module.

## Prerequisites

* supervisor
    * ```apt-get install supervisor```
* pip 
    * ```apt-get install pip```
* virtualenvwrapper
    * ```pip install virtualenvwrapper```
    
### How to setup

These steps will assume you're on a Raspberry Pi running Raspbian Lite as the "pi"" user.

* pull this repo down
    * ```git clone https://github.com/initialed85/away_from_home```
* change the pulled folder
    * ```cd away_from_home```
* install the pip requirements
    * ```pip install -r requirements.txt```
* install the supervisor config file
    * ```sudo cp away_from_home.conf /etc/supervisor/conf.d/```
* copy example_config.py to config.py and make the necessary edits; of note:
    * OWM_KEY (sign up at [OpenWeatherMap](http://www.openweathermap.com/))
    * LAT and LON of the location you want to pull weather for
    * UUID of the target [http://zmote.io/](zmote.io) device
    * ON_THRESHOLD temperature (in celsius) for turning on the aircon
    * OFF_THRESHOLD temperature (in celsius) for turning off the aircon
* reload the supervisor config file
    * ```sudo supervisorctl reread```
    * ```sudo supervisorctl update```
    
At this point, you should now be running- validate by looking at ```/tmp/supervisor_stderr_away_from_home.log```

from aprs import run

import os
import sys
import time

apiKey = os.environ.get('API_KEY')
stationId = os.environ.get('STATION_ID')
comment = os.environ.get('COMMENT')

# these two are mandatory
if apiKey is None or stationId is None:
    print("API_KEY *and* STATION_ID should be set")
    sys.exit(1)

# TODO: validate the comment is max n chars
#   I have no idea what is the limit at this point
if comment is None:
    comment = ''

while True:
    run(apiKey, stationId, comment)
    time.sleep(600)

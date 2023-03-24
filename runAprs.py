from aprs import run

import os
import time

apiKey = os.environ.get('API_KEY')
stationId = os.environ.get('STATION_ID')
comment = os.environ.get('COMMENT')

while True:
    run(apiKey, stationId, comment)
    time.sleep(5)

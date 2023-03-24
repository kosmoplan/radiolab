import os
import sys
from pathlib import Path

import requests

apiKey = os.environ.get('API_KEY')
stationId = os.environ.get('STATION_ID')
comment = os.environ.get('COMMENT')

if apiKey is None or stationId is None:
    print("API_KEY *and* STATION_ID should be set")
    sys.exit(1)

# TODO: validate the comment is max n chars
if comment is None:
    comment = ''

url = "https://api.weather.com/v2/pws/observations/current"
url += "?stationId=%s&format=json&units=m&apiKey=%s" % (stationId, apiKey)

headers = {"Accept": "application/vnd.github.v3+json"}
r = requests.get(url, headers=headers)

# abort if not 200 OK
if r.status_code != 200:
    if r.status_code == 401:
        print(f"Non-auth. API_KEY?")
    print(f"Status code: {r.status_code}")
    sys.exit(1)

data = r.json()
obs = data['observations'][0]

# wind direction in deg
winDir = obs['winddir']
# wind speed in km/h - round to integer and add padding
windSpeed = obs['metric']['windSpeed']
windSpeedMph = str(round(windSpeed / 1.609344)).rjust(3, '0')
# wind gust in km/h - round to int and add padding
windGust = obs['metric']['windGust']
windGustMph = str(round(windGust / 1.609344)).rjust(3, '0')
# rain in mm - convert to inches, get rid of 0s, padding, first 3
rain = obs['metric']['precipRate'] * 0.0039370
rainPad = str(rain).replace('.', '').rjust(3, '0')[0: 3]
# rainT in mm - convert to inches, get rid of 0s, padding, first 3
rainT = obs['metric']['precipTotal'] * 0.0039370
rainTPad = str(rainT).replace('.', '').rjust(3, '0')[0: 3]
# temp in deg C - convert to F, round and add padding
temp = obs['metric']['temp']
tempF = str(round((temp * 9 / 5) + 32)).rjust(3, '0')
# humidity % - pretty much ready to go
humidity = obs['humidity']
# barometric pressure - round to 1 digit precision and get rid of .
baroPres = str(round(obs['metric']['pressure'], 1)).replace('.', '')

timeLocal = obs['obsTimeLocal']
weatherData = f"{winDir}/{windSpeedMph}g{windGustMph}t{tempF}r{rainPad}p{rainTPad}h{humidity}b{baroPres}{comment}"

# print for fast feedback
print(timeLocal)
print(weatherData)

# last but not least, write the file
path = Path('wxcurrent.txt')
contents = timeLocal + "\n"
contents += weatherData + "\n"
path.write_text(contents)
# done :)

import sys
from pathlib import Path

import requests


def run(api_key, station_id, comment):

    url = "https://api.weather.com/v2/pws/observations/all/1day"
    url += "?stationId=%s&format=json&units=m&apiKey=%s" % (
        station_id, api_key)

    headers = {"Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)

    # abort if not 200 OK
    if r.status_code != 200:
        if r.status_code == 401:
            print(f"Non-auth. API_KEY?")
        print(f"Status code: {r.status_code}")
        sys.exit(1)

    data = r.json()
    aprs_string = process(data, comment)

    print(aprs_string)


def process(data, comment):
    # last observation
    last = len(data['observations']) - 1
    obs = data['observations'][last]

    # wind direction in deg
    win_dir = obs['winddirAvg']
    # wind speed in km/h - round to integer and add padding
    wind_speed = obs['metric']['windspeedAvg']
    wind_speed_mph = str(round(wind_speed / 1.609344)).rjust(3, '0')
    # wind gust in km/h - round to int and add padding
    wind_gust = obs['metric']['windgustAvg']
    wind_gust_mph = str(round(wind_gust / 1.609344)).rjust(3, '0')

    # rain needs to be computed using all the measurements
    rain_data = compute_rain(data)

    # rain in mm - convert to inches, get rid of 0s, padding, first 3
    rain = rain_data['avg'] * 0.0039370
    rain_pad = str(rain).replace('.', '').rjust(3, '0')[0: 3]
    # rain in mm - convert to inches, get rid of 0s, padding, first 3
    rain_t = rain_data['total'] * 0.0039370
    rain_t_pad = str(rain_t).replace('.', '').rjust(3, '0')[0: 3]
    # rain last 5m in mm - convert to inches, get rid of 0s, padding, first 3
    rain_l5 = rain_data['last_5m'] * 0.0039370
    rain_l5m_pad = str(rain_l5).replace('.', '').rjust(3, '0')[0: 3]

    # temp in deg C - convert to F, round and add padding
    temp = obs['metric']['tempAvg']
    temp_f = str(round((temp * 9 / 5) + 32)).rjust(3, '0')
    # humidity % - pretty much ready to go
    humidity = obs['humidityAvg']
    # barometric pressure - round to 1 digit precision and get rid of .
    baro_pres = str(round(obs['metric']['pressureMax'], 1)).replace('.', '')

    time_local = obs['obsTimeLocal']
    aprs_packet = f"{win_dir}/{wind_speed_mph}g{wind_gust_mph}t{temp_f}r{rain_pad}p{rain_t_pad}P{rain_l5m_pad}h{humidity}b{baro_pres}{comment}"

    # last but not least, write the file
    path = Path('wxcurrent.txt')
    contents = time_local + "\n"
    contents += aprs_packet + "\n"
    path.write_text(contents)
    # done :)

    return aprs_packet


def compute_rain(data):
    rain_total = 0
    rain_total_prev = 0
    # as far as I have seen this is the interval
    rain_last_5m = 0
    # guess this is the average?
    rain_rate = 0.0

    rain_data = {'total': rain_total, 'last_5m': rain_last_5m, 'avg': rain_rate}

    for i in range(len(data['observations'])):

        # need to get the previous value off the total, except for the first
        if i != 0:
            rain_total_prev = (data['observations'][i - 1]['metric']['precipTotal'])

        rain_total = data['observations'][i]['metric']['precipTotal']
        rain_last_5m = (rain_total - rain_total_prev)

        # overwrite this until the last value, it is OK
        rain_rate = data['observations'][i]['metric']['precipRate']

        rain_data['total'] = rain_total
        rain_data['last_5m'] = rain_last_5m
        rain_data['avg'] = rain_rate

    return rain_data

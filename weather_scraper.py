import argparse
import json
import pickle
import re
from lxml import html
import requests
import sys

DEFAULT_PICKLE = 'weather.pickle'

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', '--pickled', action='store_true', default=False)
PARSER.add_argument('-f', '--file', default=DEFAULT_PICKLE)

pickled = False

WEBPAGE = 'https://weather.com/weather/today/l/USAZ0166:1:US'
JSON_RIP_PATTERN = r'var adaptorParams = (?P<JSON_DUMP>\{.*\});$'
JSON_RIP = re.compile(JSON_RIP_PATTERN)

def main(args=None):
    if args is not None:
        pickled = args.pickled
    else:
        pickled = False
    
    page = None
    if pickled:
        page = unpickle_page(args.filename)
    else:
        try:
            page = get_web_page(WEBPAGE)
        except:
            print("Request Exception {}".format(sys.exc_info()[0]))
            page  = unpickle_page(args.filename)
            


    json_data = get_JSON(page)
    # print(page)
    # print(json_data)

    data = json.loads(json_data)
    # print(data['dailyForecast']['data']['vt1dailyForecast'][1:])
    # print(data['observation']['data'])
    # print(data['dailyForecast']['data']['vt1dailyForecast'][0])

    _current_temp = data['observation']['data']['vt1observation']['temperature']
    _current_max_temp = data['observation']['data']['vt1observation']['temperatureMaxSince7am']
    _current_wind_speed = data['observation']['data']['vt1observation']['windSpeed']
    # descriptor of the current weather
    _current_phrase = data['observation']['data']['vt1observation']['phrase']

    _forecast = []
    for day in data['dailyForecast']['data']['vt1dailyForecast'][1:]:
        _forecast.append({"day":day['dayOfWeek'], 'temp':day['day']['temperature'], 'phrase':day['day']['phrase']})

    print('Temp: {}\nMax: {}\nWind: {}\n{}'.format(_current_temp, _current_max_temp, _current_wind_speed, _current_phrase))
    print(_forecast)


def unpickle_page(filename = None):
    if filename is None:
        filename = DEFAULT_PICKLE

    with open(filename, 'rb') as f:
        page = pickle.load(f).text

def get_web_page(address):
    """
    grab the web page and dump it's text
    """
    _page_text = requests.get(address).text
    return _page_text

def get_JSON(page):
    """
    given the html page text from weather.com produce the JSON chunck we're looking for
    """
    for line in page.splitlines():
        if line.find('var adaptorParams') != -1:
            # DEBUG
            # print(line)
            return rip_JSON(line)

def rip_JSON(line):
    # DEBUG
    # print(JSON_RIP.search(line))
    return JSON_RIP.search(line).group('JSON_DUMP')


if __name__ == '__main__':
    _args = PARSER.parse_args(sys.argv[1:])
    main(_args)

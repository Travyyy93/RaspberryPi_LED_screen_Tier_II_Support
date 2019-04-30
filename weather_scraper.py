import argparse
import json
import pickle
import re
import sys

import requests
from lxml import html


DEFAULT_PICKLE = 'weather.pickle'

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', '--pickled', action='store_true', default=False)
PARSER.add_argument('-f', '--filename', default=DEFAULT_PICKLE)
PARSER.add_argument('-c', '--cache',action='store_true', default=False)

WEBPAGE = 'https://weather.com/weather/today/l/USAZ0166:1:US'
JSON_RIP_PATTERN = r'var adaptorParams = (?P<JSON_DUMP>\{.*\});$'
JSON_RIP = re.compile(JSON_RIP_PATTERN)

DAY_ABBREV = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
              'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat',
              'Sunday': 'Sun'}

def main(args=None):
    outstring = ''
    page = None

    if args is not None:
        pickled = args.pickled
        cache = args.cache

        if cache and pickled:
            print('bad arguments - cannot cache page and use pickle')
            return outstring
    else:
        pickled = False
        cache = False

    if pickled:
        page = unpickle_page(args.filename)

    else:
        try:
            page = get_web_page(WEBPAGE)
        except:
            print("Request Exception {}".format(sys.exc_info()[0]))
            page = unpickle_page(args.filename)

    if cache:
        pickle_page(args.filename, page)

    json_data = get_JSON(page)

    data = json.loads(json_data)

    _current_temp = data['observation']['data']['vt1observation']['temperature']
    _current_max_temp = data['observation']['data']['vt1observation']['temperatureMaxSince7am']
    # TODO remove, unused
    # _current_wind_speed = data['observation']['data']['vt1observation']['windSpeed']

    # descriptor of the current weather
    _current_phrase = data['observation']['data']['vt1observation']['phrase']

    _forecast = []
    outstring += 'CURRENT: {} {} HI:{}    '.format(_current_phrase,
                                                   _current_temp,
                                                   _current_max_temp)

    for day in data['dailyForecast']['data']['vt1dailyForecast'][1:6]:
        outstring += '{}: {}-{}     '.format(DAY_ABBREV[day['dayOfWeek']],
                                             day['day']['phrase'],
                                             day['day']['temperature'])

        # TODO remove legacy code
        # _forecast.append({"day":day['dayOfWeek'], 'temp':day['day']['temperature'], 'phrase':day['day']['phrase']})

    # print('Temp: {}\nMax: {}\nWind: {}\n{}'.format(_current_temp, _current_max_temp, _current_wind_speed, _current_phrase))
    # print(outstring)

    return outstring

def unpickle_page(filename=None):
    """
    unpickle a page for use later in the function
    Params:
        filename - the path to the file to use. Defaults to None
    """
    page = ''
    if filename is None:
        filename = DEFAULT_PICKLE

    with open(filename, 'rb') as f:
        page = pickle.load(f)

    return page

def pickle_page(filename=None, page=None):
    """
    pickle / cache a page under the provided filename
    """
    if filename is None:
        filename = DEFAULT_PICKLE

    with open(filename, 'wb') as f:
        pickle.dump(page, f)

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

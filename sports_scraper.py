import argparse
import datetime
import pickle
import sys

from selenium import webdriver
from selenium import common
from lxml import html

# this will need to be changed when deployed
driver_path = r'C:\Users\yockyjo\AppData\Local\Programs\Python\Python36-32\selenium\webdriver\geckodriver-v0.19.0-win32\geckodriver.exe'

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', '--pickled', action='store_true', default=False)
# indicate that the page should be cached for later
PARSER.add_argument('-c', '--cache', action='store_true', default=False)
# NFL week
PARSER.add_argument('-w', '--week', default=1)

# TODO get the pages for the day before
PAGES = ['http://www.espn.com/nfl/scoreboard',
         'http://www.espn.com/nba/scoreboard',
         'http://www.espn.com/mlb/scoreboard',
         'http://www.espn.com/nhl/scoreboard']

PICKLE_NAMES = ['/home/pi/Documents/Git/RPi_Code/nfl.pickle', '/home/pi/Documents/Git/RPi_Code/nba.pickle', '/home/pi/Documents/Git/RPi_Code/mlb.pickle', '/home/pi/Documents/Git/RPi_Code/nhl.pickle',
                '/home/pi/Documents/Git/RPi_Code/nfl_h.pickle', '/home/pi/Documents/Git/RPi_Code/nba_h.pickle', '/home/pi/Documents/Git/RPi_Code/mlb_h.pickle', '/home/pi/Documents/Git/RPi_Code/nhl_h.pickle']
SCORE_LABLES = ['---NFL---', '---NBA---', '---MLB---', '---NHL---',
                '---NFL (last week)---', '---NBA (yesterday)---',
                '---MLB (yesterday)---', '---NHL (yesterday)---']

SCOREBOARD_FINAL = '//section[@class="sb-score final"]'
AWAY = './/tr[@class="away"]'
HOME = './/tr[@class="home"]'

TEAM_ABBREV = './/span[@class="sb-team-abbrev"]'
SCORE_TOTAL = './/td[@class="total"]/span'


def main(args=None):
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    if args is not None:
        pickled = args.pickled
        cache = args.cache

    else:
        pickled = False
        cache = False

    content = []
    outstring = ''
    build_historical_scores(date=yesterday, week=int(args.week))

    if pickled:
        for i, page in enumerate(PAGES):
            content.append(get_page(page, filename=PICKLE_NAMES[i],
                                    is_cache=cache, is_pickled=pickled))

    else:
        try:
            driver = webdriver.Firefox(executable_path=driver_path)

            for i, page in enumerate(PAGES):
                content.append(get_page(page, filename=PICKLE_NAMES[i],
                                        is_cache=cache, is_pickled=pickled,
                                        driver=driver))
            driver.quit()

        except common.exceptions.WebDriverException as e:
            print(e)
            print('defaulting to pickle. . .')
            content.append(get_page(page, filename=PICKLE_NAMES[i],
                                    is_cache=cache, is_pickled=True))
        except Exception as e:
            raise e

    score_string = []
    outstring = ''
    for i, page in enumerate(content):
        score_string.append(scrape_page(page, i))

    if i > 3:
        if score_string [i] == score_string[i-4]:
            score_string[i] == ''

    for i, string in enumerate(score_string):
        if string != '':
            outstring += SCORE_LABLES[i] + string

    print(outstring)
    return outstring

def scrape_page(content, index):
    outstring = ''
    tree = html.fromstring(content)
    # DEBUG
    # print('scraping . . .')
    # print(tree.getchildren())
    final_scores = tree.xpath(SCOREBOARD_FINAL)
    # print('final scores size: {}'.format(len(final_scores)))
    if len(final_scores) == 0:
        return ''
    for score in final_scores:
        _away = list(map(lambda x: x.xpath(AWAY), score))[0]

        _away_name = list(map(lambda x: x.xpath(TEAM_ABBREV), _away))[0]
        _away_score = list(map(lambda x: x.xpath(SCORE_TOTAL), _away))[0]


        _home = list(map(lambda x: x.xpath(HOME), score))[0]

        _home_name = list(map(lambda x: x.xpath(TEAM_ABBREV), _home))[0]
        _home_score = list(map(lambda x: x.xpath(SCORE_TOTAL), _home))[0]

        # DEBUG
        # print('{}'.format(_away_score[0].getchildren()))
        if len(_home_score)>0 and len(_away_score)>0:
            outstring += ('{}(H), {} :{}, {}     '.format(_home_name[0].text,
                                                          _home_score[0].text,
                                                          _away_name[0].text,
                                                          _away_score[0].text))
        # check if historical scores are the same, if so, set to empty

    # print(outstring)
    return outstring

def get_page(name='', filename='', is_cache=False, is_pickled=False, driver=None):
    if is_pickled:
        with open(filename, 'rb') as f:
            source = pickle.load(f)
            return source

    if name != '' and driver != None:
        # print(name)
        driver.get(name)
        # print(driver.page_source)

    if is_cache:
        with open(filename, 'wb') as f:
            pickle.dump(driver.page_source, f)
        print('{} written as {}'.format(name, filename))
    return driver.page_source

def get_pagename(board:str='nfl',date: datetime.datetime=
                 datetime.datetime(2017, 1, 1), week:int=1):
    """
    return the historic page name
    """
    if board is 'nfl':
        if week > 1:
            return PAGES[0] + '/_/year/2017/seasontype/2/week/{}'.format(week-1)
        else:
            return PAGES[0] + '/_/year/2017/seasontype/2/week/{}'.format(week)

    if board is 'nba':
        return PAGES[1] + '/_/date/{}{}{}'.format(date.year, date.month, date.day)

    if board is 'mlb':
        return PAGES[2] + '/_/date/{}{}{}'.format(date.year, date.month, date.day)

    if board is 'nhl':
        return PAGES[3] + '?date={}{}{}'.format(date.year, date.month, date.day)

def build_historical_scores(date: datetime.datetime=
                            datetime.datetime(2017, 1, 1), week: int=1):
    """
    update the PAGES list to include scores from yesterday
    """
    if len(PAGES) == 8:
        PAGES[4] = (get_pagename('nfl', date, week))
        PAGES[5] = (get_pagename('nba', date, week))
        PAGES[6] = (get_pagename('mlb', date, week))
        PAGES[7] = (get_pagename('nhl', date, week))

    else:
        PAGES.append(get_pagename('nfl', date, week))
        PAGES.append(get_pagename('nba', date, week))
        PAGES.append(get_pagename('mlb', date, week))
        PAGES.append(get_pagename('nhl', date, week))

if __name__ == '__main__':
    _args = PARSER.parse_args(sys.argv[1:])
    if _args.cache and _args.pickled:
        print('Cannot cache and use pickled modes simultaneously')
    main(_args)

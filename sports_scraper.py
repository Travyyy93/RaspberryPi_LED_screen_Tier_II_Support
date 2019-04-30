from lxml import html
from selenium import webdriver

# this will need to be changed when deployed
driver_path =r'C:\Users\yockyjo\AppData\Local\Programs\Python\Python36-32\selenium\webdriver\geckodriver-v0.19.0-win32\geckodriver.exe'

driver = webdriver.Firefox(executable_path=driver_path)

PAGES = ['http://www.espn.com/nfl/scoreboard','http://www.espn.com/nba/scoreboard','http://www.espn.com/mlb/scoreboard']

scoreboard_final = '//div[@class="sb-score final"]'
away = '//tr[@class="away"]'
home = '//tr[@class="home"]'

team_abbrev = '//span[@class="sb-team-abbrev"]'
score_total = '//td[@class="total"]'

def getPage(name = ''):
    if name != '':
        source = driver.get(name)
    return source.page_source


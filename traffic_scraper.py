import argparse
from lxml import html
import pickle
import re
import requests
import sys


WEBPAGE = 'http://www.az511.gov/traffic/ttindex.jsp'

BASE_LXML_TARGET = '//ul[@id="tree1"]/li/ul/li/ul/table'
BRANCH = 'tr/td'
LABEL = '/span'

TIME_PATTERN = r'[0-9]* min'
TIME_REGEX = re.compile(TIME_PATTERN)

LABELS = ['Avg','Current']


page = requests.get(WEBPAGE)

tree = html.fromstring(page.content)
base = tree.xpath(BASE_LXML_TARGET)
print (len(base))
headers = []

_target = list((map(lambda x: x.xpath(BRANCH), base)))


for e in _target:
    headers += e
outString = ''

_first = True
for i in headers:
    if i.getchildren() is not None:
        # check for span, this is the label for the time
        for c in i.getchildren():
            if c.tag == 'span':
                _first = True
                outString += c.text + ':'
                continue

        if i.text in LABELS or i.text is None:
            continue

        elif TIME_REGEX.search(i.text) is not None and _first:
            _first = False
            # the first data element is curent time
            outString += i.text + '  '

"""
    print(i)
    print('TAG: {}'.format(i.tag))
    print('TEXT: {}'.format(i.text))
    print('TAIL: {}'.format(i.tail))
    print('CHILDREN: {}'.format(i.getchildren()))

    # NOTE the data I'm after is in here
    for j in i.getchildren():
        print('INNER {}'.format(type(j)))
        print('INNER TAG: {}'.format(j.tag))
        print('INNER TEXT: {}'.format(j.text))
        print('INNER TAIL: {}'.format(j.tail))
"""

print(outString)
# TODO
# IMPLEMENTATION

import argparse
import pickle
import re
import sys

import requests
from lxml import html


WEBPAGE = 'http://www.az511.gov/traffic/ttindex.jsp'
DEFAULT_PICKLE = 'traffic.pickle'

BASE_LXML_TARGET = '//ul[@id="tree1"]/li/ul/li/ul/table'
BRANCH = 'tr/td'
LABEL = '/span'

TIME_PATTERN = r'[0-9]* min'
TIME_REGEX = re.compile(TIME_PATTERN)

LABELS = ['Avg', 'Current']

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', '--pickled', action='store_true', default=None)
PARSER.add_argument('-c', '--cache', action='store_true', default=None)
PARSER.add_argument('-f', '--filename', default=DEFAULT_PICKLE)

def main(args=None):
    pickled = False
    cache = False

    if args != None:
        pickled = args.pickled
        cache = args.cache

    if pickled:
        if args.filename is None:
            with open(DEFAULT_PICKLE, 'rb') as f:
                page = pickle.load(f)
        else:
            with open(args.filename, 'rb') as f:
                page = pickle.load(f)

    else:
        page = requests.get(WEBPAGE)

    if cache:
        with open(args.filename, 'wb') as f:
            pickle.dump(page, f)

    tree = html.fromstring(page.content)
    base = tree.xpath(BASE_LXML_TARGET)
    print(len(base))
    headers = []

    _target = list((map(lambda x: x.xpath(BRANCH), base)))

    for e in _target:
        headers += e

    outstring = ''

    _first = True
    for i in headers:
        if i.getchildren() is not None:
            # check for span, this is the label for the time
            for c in i.getchildren():
                if c.tag == 'span':
                    _first = True
                    outstring += c.text + ':'
                    continue

            if i.text in LABELS or i.text is None:
                continue

            elif TIME_REGEX.search(i.text) is not None and _first:
                _first = False
                # the first data element is curent time
                outstring += i.text + '    '

    print(outstring)
    return outstring

if __name__ == '__main__':
    _args = PARSER.parse_args(sys.argv[1:])
    main(_args)
# TODO
# IMPLEMENTATION

import argparse
import pickle
import requests
import sys
from selenium import webdriver

PARSER = argparse.ArgumentParser(description='Main parser for this program')
PARSER.add_argument('url', nargs='*')
PARSER.add_argument('-n', '--name', nargs='*',
                    help='name of the pickle file to be stored')
PARSER.add_argument('-f','--force', action='store_true')
PARSER.add_argument('-r','--rendered', action='store_true', default=False, help='indicate whether or not the ')

DEFAULT = 'pickle.conf'

def pickle_url(url, name='', render=0):
    # render not used at this time
    if len(url) <= 0:
        print('empty string passed to url')
        return
    print(url)
    page = requests.get(url.strip())
    filename = name + '.pickle'

    if page.ok:
        with  open(filename, 'wb') as f:
            outdata = pickle.dump(page, f)
        print('page {} pickled under {}'.format(url, filename))
    else:
        print('Status Code: {}\npage {} unpickled'.format(page.status_code, url))

def read_default():
    with open(DEFAULT, 'r') as f:
        content = f.readlines()
    return content

def main(argv):
    args = PARSER.parse_args(argv[1:])
    if len(args.url) <= 0:
        for u in read_default():
            tup = u.split(',')
            pickle_url(tup[0],tup[1],tup[2])

    for u in args.url:
        pickle_url(u)

if __name__ == '__main__':
    main(sys.argv)

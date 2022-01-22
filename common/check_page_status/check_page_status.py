from urllib.request import Request, urlopen
import json
import requests
import argparse
import logging
from bs4 import BeautifulSoup


def get_sitemap(url):
    req = Request(url + '/sitemap/?format=json')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    content = json.loads(urlopen(req).read().decode('utf-8'))
    return content


def main():
    parser = argparse.ArgumentParser(description='Check status of all pages of a given IoGT site.')
    parser.add_argument('url', help='Full URL of the site, e.g. https://global.iogt.site/')
    parser.add_argument('logfile', nargs='?', help='Log file to write the output to.', default='warnings.log')
    parser.add_argument('level', nargs='?', choices=["warn", "all"], help='warn: only log broken pages. all: log all pages.', default='warn')
    args = parser.parse_args()

    if args.level == 'warn':
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(filename=args.logfile, level=level, filemode='w')

    for page in get_sitemap(args.url):
        r = requests.get(page)
        if r.ok:
            logging.info(f"{r.status_code} {page}")
        else:
            logging.warning(f"{r.status_code} {page}")

        soup = BeautifulSoup(r.text, features="html.parser")
        images = soup.findAll('img')
        for image in images:
            ri = requests.get(args.url + image['src'])
            if ri.ok:
                logging.info(f"{r.status_code} {image['src']} refenced by {page}")
            else:
                logging.warning(f"{r.status_code} {image['src']} refenced by {page}")



if __name__ == '__main__':
    main()



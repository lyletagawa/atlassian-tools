#!/usr/bin/env python3
#
# Atlassian Confluence allows its users to export a single page to PDF.
# However, exporting multiple pages (in one operation) is prohibited
# without the `Export Space` permission...
#
# Instead, we can use the Atlassian REST API to export a Confluence space
# by reconstructing the Confluence space hierarchy and exporting each page.
#
# Usage: confluence_export_space.py [SPACE]
#
# Environment variables:
#   ATLASSIAN_URL_PREFIX (e.g. https://example.atlassian.net/wiki)
#   ATLASSIAN_USER       (e.g. name@example.com)
#   ATLASSIAN_TOKEN      (e.g. API token, not your password)

from atlassian import Confluence
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool
import os
import re
import sys
#mport time

c = Confluence(
    url=os.environ["ATLASSIAN_URL_PREFIX"],
    username=os.environ["ATLASSIAN_USER"],
    password=os.environ["ATLASSIAN_TOKEN"],
    api_version='cloud'
)

DEBUG = os.getenv('DEBUG')

def debug(message: str):
    if DEBUG:
        print(message)

def get_page_path(page_id: int, page_path: str):
    """
    Recursively populate dict that maps page_id to the path on disk
    :param page_id: int
    :param page_path: str
    :return: None
    """
    title = f'{re.sub(r"[^-_0-9A-Za-z]+", "_", c.get_page_by_id(page_id)["title"])}'

    debug(f'Adding: {page_id:-12d} {page_path}/{title}.pdf')
    page_id_path[page_id] = f'{page_path}/{title}.pdf'
    page_ids.append(page_id)

    for page in c.get_child_pages(page_id):
        get_page_path(int(page["id"]), f'{page_path}/{title}')

def get_page(page_id: int, page_path: str):
    """
    Export page as standard pdf exporter and write to disk
    :param page_id: int
    :param page_path: str
    :return: None
    """
    d = os.path.dirname(page_path)
    f = os.path.basename(page_path)

    print(f'Exporting page to PDF: {d}/{f}')
    os.makedirs(d, exist_ok=True)

    fh = open(f'{d}/{f}', "wb")
    chars = fh.write(c.export_page(page_id))
    fh.close()

def main():
    global page_ids
    global page_id_path

    try:
        space = sys.argv[1]
    except:
        print(f'Usage: {os.path.basename(__file__)} [SPACE]\n\n' \
              f'Environment variables:\n' \
              f'  ATLASSIAN_URL_PREFIX (e.g. https://example.atlassian.net/wiki)\n' \
              f'  ATLASSIAN_USER       (e.g. username@example.com)\n' \
              f'  ATLASSIAN_TOKEN      (e.g. API token, not your password)\n')
        exit(1)

    try:
        pool = ThreadPool(4)

        debug('Exporting home page')
        home_page_id = int(c.get_space(space)["homepage"]["id"])
        get_page(home_page_id, f'{space}/_Overview.pdf')
        page_id_path = {}

        print('Generating page hierarchy')
        page_ids = [int(p["id"]) for p in c.get_child_pages(home_page_id)]
        pool.starmap(get_page_path, zip(page_ids, repeat(space)))

        debug('Exporting child pages')
        page_ids = sorted(set(page_ids))
        page_id_paths = [page_id_path[id] for id in page_ids]
        pool.starmap(get_page, zip(page_ids, page_id_paths))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

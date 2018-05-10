from bs4 import BeautifulSoup
from threading import Thread
from pathlib import Path
import requests
import re
import shutil
import time
from utils import *

MAX_THREAD = 30
SORT_BY_YEAR = True
SORT_BY_PAPER = True
ROOT_DIR = Path('PapaCambridge')
ROOT_URL = 'https://pastpapers.co'

logger = Logger('PapaCrawler')

def getUrl(url, **options):
    try:
        web = requests.get(url, **options)
    except requests.packages.urllib3.exceptions.ReadTimeoutError:
        logger.error('Timeout, url: {}'.format(url))
        return -1
    except requests.exceptions.ConnectionError:
        logger.error('Connection error, url: {}'.format(url))
        return -1
    except Exception as e:
        logger.error('Uncaught exception ({}): {} when requesting url: {}'.format(e.__class__.__name__, e, url))
        return -1
    else:
        return web

def iterate_page_items(url, selector='a.item.dir'):
    web = getUrl(url)
    if web == -1:
        return -1
    soup = BeautifulSoup(web.text, 'lxml')
    for item in soup.select(selector):
        if item.get_text().strip() == '..':
            continue
        yield item

def getCourseUrls(*courseIds):
    courseIds = list(courseIds)
    # regex = re.compile(r'(?:.* \((\d{4})\))|(?:.* - (\d{4}))')
    regex = re.compile(r'.+-(\d{4})')
    url = ROOT_URL + '/cie/?dir=IGCSE'
    web = getUrl(url)
    if web == -1:
        exit()
    soup = BeautifulSoup(web.text, 'lxml')
    for course in soup.select('a.item.dir'):
        result = regex.findall(course.get_text().strip())
        if not result:
            continue
        courseId = result[0]
        if courseId in courseIds:
            courseIds.remove(courseId)
            yield course.get_text().strip(), ROOT_URL + course.get('href')
    if courseIds:
        logger.warning('Course code(s) not found: {}'.format(', '.join(courseIds)))

def getPaperUrls(courseName, courseUrl):
    regex = re.compile(r'[0-9]{4}_([swm])([0-9]{1,2})_(' + '|'.join(types) + r')_([' + ''.join(papers) + r'][0-9])\.pdf')
    for yearFolder in iterate_page_items(courseUrl):
        yearText = yearFolder.get_text().strip()
        for monthFolder in iterate_page_items(ROOT_URL + yearFolder.get('href')):
            monthText = monthFolder.get_text().strip()
            for file in iterate_page_items(ROOT_URL + monthFolder.get('href'), 'a.item.pdf'):
                filename = file.get_text().strip()
                info = regex.findall(filename)
                if info and years[0] <= int(info[0][1]) <= years[1]:
                    fileUrl = '{}/cie/IGCSE/{}/{}/{}/{}'.format(ROOT_URL, courseName, yearText, monthText, filename)
                    if SORT_BY_YEAR:
                        monthChar, yearNum = info[0][:2]
                        filename = filename.replace(monthChar + yearNum, yearNum + monthChar)
                    if SORT_BY_PAPER:
                        paperType, paperId = info[0][2:]
                        filename = filename.replace('{}_{}'.format(paperType, paperId), '{}_{}'.format(paperId, paperType))
                    yield fileUrl, filename

def downloadFile(url, dirName, filename=None):
    name = filename or url.split('/')[-1]
    req = getUrl(url, timeout=60, stream=True)
    if req == -1:
        return -1
    if req.status_code == 200:
        with (ROOT_DIR / dirName / name).open('wb') as file:
            try:
                req.raw.decode_content = True
                shutil.copyfileobj(req.raw, file)
            except Exception as e:
                logger.error('Uncaught exception ({}): {} when copying file object "{}" from URL "{}"'.format(e.__class__.__name__, e, name, url))
                return -1
    else:
        logger.error('Error response [{}], url: {}'.format(req.status_code, url))
        return -1

try:
    courses = input('Input the course codes, separate using spaces: ').split(' ')
    papers = input('Input the paper numbers, separate using spaces (default: all): ') or '0123456789'
    types = input('Inpute the types of document, separate using spaces (default: qp ms in pre): ') or 'qp ms in pre'
    years = input('Input the range of years (last two digit), separate by a dash(-) (default: all): ') or '0-99'
    papers = papers.split(' ')
    types = types.split(' ')
    years = list(map(int, years.split('-')))
    logger.info('Getting course URLs')

    for courseName, courseUrl in getCourseUrls(*courses):
        regex = re.compile(r'(.+)-(\d{4})')
        courseTitle, courseCode = regex.findall(courseName)[0]
        courseNameBeautified = '{} ({})'.format(' '.join(courseTitle.split('-')), courseCode)
        logger.info('Crawling: \033[4m{}\033[0m'.format(courseNameBeautified))
        (ROOT_DIR / courseNameBeautified).mkdir(parents=True, exist_ok=True)
        allPapers = list(getPaperUrls(courseName, courseUrl))
        if not allPapers:
            logger.info('No files match your requirements!')
            continue
        logger.info('Downloading {} files'.format(len(allPapers)))

        threadPool = []
        for fileUrl, filename in allPapers:
            thread = Thread(target=downloadFile, args=(fileUrl, courseNameBeautified, filename))
            threadPool.append(thread)
            if len(threadPool) == MAX_THREAD:
                for thread in threadPool:
                    thread.start()
                thread.join()
                threadPool = []
        for thread in threadPool:
            thread.start()
        thread.join()
    logger.info('Completed!')
except KeyboardInterrupt:
    logger.info('Keyboard interrupted')
    exit()

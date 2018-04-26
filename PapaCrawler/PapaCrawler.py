from bs4 import BeautifulSoup
from threading import Thread
from pathlib import Path
import requests
import re
import shutil
import time
from utils import *

MAX_THREAD = 30
ROOT_DIR = Path('PapaCambridge')
ROOT_URL = 'http://pastpapers.papacambridge.com/'

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

def getCourseUrls(*courses):
    courses = list(courses)
    # regex = re.compile(r'(?:.* \((\d{4})\))|(?:.* - (\d{4}))')
    regex = re.compile(r'\d{4}')
    url = ROOT_URL + '?dir=Cambridge%20International%20Examinations%20%28CIE%29/IGCSE'
    web = getUrl(url)
    if web == -1:
        exit()
    soup = BeautifulSoup(web.text, 'lxml')
    for courseTitle in soup.select('span.file-name'):
        courseId = regex.findall(courseTitle.get_text())
        if courseId and courseId[0] in courses:
            courses.remove(courseId[0])
            yield courseTitle.get_text().strip(), ROOT_URL + courseTitle.parent.parent.get('href')
    if courses:
        logger.warning('Course code(s) not found: {}'.format(', '.join(courses)))

def getPaperUrls(courseUrl):
    regex = re.compile(r'[0-9]{4}_[swm]([0-9]{1,2})_(?:' + '|'.join(types) + r')_[' + ''.join(papers) + r'][0-9]\.pdf')
    courseWeb = getUrl(courseUrl)
    if courseWeb == -1:
        return -1
    courseSoup = BeautifulSoup(courseWeb.text, 'lxml')
    for folder in courseSoup.select('span.file-name'):
        if folder.get_text().strip() == '..':
            continue
        web = getUrl(ROOT_URL + folder.parent.parent.get('href'))
        if web == -1:
            return -1
        soup = BeautifulSoup(web.text, 'lxml')
        for file in soup.select('span.file-name'):
            year = regex.findall(file.get_text())
            if year and years[0] <= int(year[0]) <= years[1]:
                yield ROOT_URL + file.parent.parent.get('href').replace('view.php?id=', '')

def downloadFile(url, dirName):
    name = url.split('/')[-1]
    req = getUrl(url, timeout=60, stream=True)
    if req == -1:
        return -1
    if req.status_code == 200:
        with (ROOT_DIR / dirName / name).open('wb') as file:
            try:
                req.raw.decode_content = True
                shutil.copyfileobj(req.raw, file)
            except Exception as e:
                logger.error('Uncaught exception ({}): {} when copying file object: {}'.format(e.__class__.__name__, e, name))
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
        logger.info('Crawling: \033[4m{}\033[0m'.format(courseName))
        (ROOT_DIR / courseName).mkdir(parents=True, exist_ok=True)
        allPapers = list(getPaperUrls(courseUrl))
        if not allPapers:
            logger.info('No files match your requirements!')
            continue
        logger.info('Downloading {} files'.format(len(allPapers)))

        threadPool = []
        for fileUrl in allPapers:
            thread = Thread(target=downloadFile, args=(fileUrl, courseName))
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

import time
import sys

class Logger(object):
    '''Parent class for all logging methods.'''
    def __init__(self, loggerName='default', logType=0):
        '''logType: 0 print only, 1 file only, 2 print and file'''
        self._name = loggerName.strip('_')
        self._logType = logType
        self._LEVELS = {0: 'DEBUG', 1: 'INFO', 2: 'WARNING', 3: 'ERROR', 4: 'CRITICAL'}
        self._COLORS = {'DEBUG': '', 'INFO': '\033[36m', 'WARNING': '\033[93m', 'ERROR': '\033[91m', 'CRITICAL': '\u001b[48;5;9m'}
        self._MSG = '{} ({}) {}\033[1m[{}]\033[0m {}'

    def log(self, level, msg, callback=None):
        '''Base method for all levels of logging.'''
        currentTime = time.strftime('%Y-%m-%d %H:%M:%S')
        level = self._LEVELS.get(level, level)
        if level not in self._LEVELS.values():
            self.error('Unknown log type: [{}], message: {}'.format(level, msg))
            return -1
        print(self._MSG.format(currentTime, self._name, self._COLORS.get(level, ''), level, msg))
        if level == 'CRITICAL':
            if callback in (0, None):
                pass
            elif callback in (1, 'PAUSE'):
                input('A critical error occurred, the program has paused, press enter to continue.')
            elif callback in (2, 'EXIT'):
                exit()

    def debug(self, msg):
        self.log('DEBUG', msg)

    def info(self, msg):
        self.log('INFO', msg)

    def warning(self, msg):
        self.log('WARNING', msg)

    def error(self, msg):
        self.log('ERROR', msg)

    def critical(self, msg, callback=None):
        self.log('CRITICAL', msg, callback)


class ProgressBar(object):
    '''Parent class for progress bars.'''
    def __init__(self, count, width=50, char='-'):
        self.amount = 0
        self.width = width
        self.count = count
        self.char = char[0]
        self.done = 0
        sys.stdout.write('[{}]'.format(' ' * self.width))
        sys.stdout.flush()
        sys.stdout.write('\b' * (self.width + 1))

    def update(self):
        if self.done == self.count:
            raise Exception('too much updates!')
        self.amount %= self.count
        self.amount += self.width
        length = self.amount // self.count
        if length > 1:
            self.done += 1
        sys.stdout.write(self.char * length)
        if self.done == self.count:
            sys.stdout.write('\n')
        sys.stdout.flush()

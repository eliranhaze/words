import cPickle as cpkl
import os

from logger import get_logger
logger = get_logger('pkl')

def save(data, name):
    filename = _format_filename(name)
    logger.debug('saving data to %s' % filename)
    cpkl.dump(data, open(filename, 'wb'))
    logger.debug('saved data to %s' % filename)

def load(name, default = None):
    filename = _format_filename(name)
    if os.path.exists(filename):
        logger.debug('loading data from %s' % filename)
        data = cpkl.load(open(filename, 'rb'))
        logger.debug('loaded data from %s' % filename)
        return data
    logger.debug('%s does not exist', name)
    return default

def _format_filename(name):
    return '.%s.pkl' % name

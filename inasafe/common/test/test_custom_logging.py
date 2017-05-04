# coding=utf-8
__author__ = 'etienne'

import unittest
import logging
import os
from inasafe.common.custom_logging import setup_logger


class TestCustomLogging(unittest.TestCase):

    def test_logger(self):

        LOGGER = logging.getLogger('SaVap')
        setup_logger('SaVap')

        handlers = [class_name.__class__.__name__
                    for class_name in LOGGER.handlers]

        self.assertTrue('FileHandler' in handlers)
        self.assertTrue('StreamHandler' in handlers)
        self.assertTrue('QgsLogHandler' in handlers)

        if 'INASAFE_SENTRY' in os.environ:
            self.assertTrue('SentryHandler' in handlers)

if __name__ == '__main__':
    unittest.main()

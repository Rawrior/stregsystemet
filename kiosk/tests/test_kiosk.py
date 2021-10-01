# -*- coding: utf8 -*-

from django.test import TestCase, Client
# import logging
from decorators import suppress_request_warnings


class KioskTests(TestCase):
    # setUp and tearDown together effectively suppress django's warnings
    # about '/kiosk/next_real' not existing. We know that, that's what
    # the test is for, so this is just to keep the output clean
    # def setUp(self) -> None:
    #     """Reduce the log level to avoid errors like 'not found'"""
    #     logger = logging.getLogger("django.request")
    #     self.previous_level = logger.getEffectiveLevel()
    #     logger.setLevel(logging.ERROR)
    #
    # def tearDown(self) -> None:
    #     """Reset the log level back to normal"""
    #     logger = logging.getLogger("django.request")
    #     logger.setLevel(self.previous_level)

    @suppress_request_warnings
    def test_kiosk_empty(self):
        c = Client()
        response = c.get('/kiosk/next_real')
        self.assertEqual(404, response.status_code)

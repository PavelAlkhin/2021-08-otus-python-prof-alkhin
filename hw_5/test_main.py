from unittest import TestCase

import requests


class Test(TestCase):
    def test_main(self):
        requests.get(url='http://127.0.0.1:9999')

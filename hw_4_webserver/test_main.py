from unittest import TestCase

import requests

from .httpd import parse_request_line

HEADER = {'Content-Type': 'text/html'}
TEXT_REQUEST = b'GET /sa/index.html HTTP/1.1\r\nHost: 127.0.0.1:9999'


class Test(TestCase):
    def test_main(self):
        answer = requests.get(url='http://127.0.0.1:9999')
        self.assertEqual(answer.headers, HEADER)

    def test_parse_request_line(self):
        data = parse_request_line(TEXT_REQUEST.decode())
        method = data['method']
        resource = data['resource']
        self.assertEqual(method, 'GET')
        self.assertEqual(resource, '/sa/index.html')

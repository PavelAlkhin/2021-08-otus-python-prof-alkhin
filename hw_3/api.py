#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import models

import scoring

SALT = 'Otus'
ADMIN_LOGIN = 'admin'
ADMIN_SALT = '42'
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: 'Bad Request',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND: 'Not Found',
    INVALID_REQUEST: 'Invalid Request',
    INTERNAL_ERROR: 'Internal Server Error',
}


class RequestHandler:
    def validate_handle(self, request, arguments, ctx, store):
        if not arguments.is_valid:
            return arguments.errfmt, INVALID_REQUEST
        return self.handle(request, arguments, ctx, store)

    def handle(self, request, arguments, ctx, store):
        return {}, OK


class RequestMeta(type):
    def __new__(mcs, name, bases, attrs):
        field_list = []
        for k, v in attrs.items():
            if isinstance(v, models.Field):
                v.name = k
                field_list.append(v)

        cls = super(RequestMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = field_list
        return cls


class Request(metaclass=RequestMeta):

    def __init__(self, request):
        self.errors = []
        self.request = request
        self.is_cleaned = False

    def clean(self):
        for f in self.fields:
            pass  # code here

    def is_valid(self):
        if not self.is_cleaned:
            self.clean()
        return not self.errors

    def errfmt(self):
        return ', '.join(self.errors)


class ClientsInterestsRequest(Request):
    client_ids = models.ClientIDsField(required=True)
    date = models.DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = models.CharField(required=False, nullable=True)
    last_name = models.CharField(required=False, nullable=True)
    email = models.EmailField(required=False, nullable=True)
    phone = models.PhoneField(required=False, nullable=True)
    birthday = models.BirthDayField(required=False, nullable=True)
    gender = models.GenderField(required=False, nullable=True)

    def is_valid(self):
        default_valid = super(OnlineScoreRequest, self).is_valid()
        if not default_valid:
            return default_valid
        pass  # code here


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


class OnlineScoreHandler(RequestHandler):
    request_type = OnlineScoreRequest

    def handle(self, request, arguments, ctx, store):
        score = 0

        errors = {}

        try:
            request.login = request.login.check(request.request['login'])
        except:
            errors['login'] = 'not valid'

        try:
            request.account = request.account.check(request.request['account'])
        except:
            errors['account'] = 'not valid'

        try:
            request.arguments = request.arguments.check(request.request['arguments'])
        except:
            errors['arguments'] = 'not valid'

        for field in self.request_type.fields:
            name = field.name
            value = request.request['arguments'][name]
            try:
                n_value = getattr(arguments, name).check(value)
                setattr(arguments, name, n_value)
            except:
                setattr(arguments, name, None)
                errors[name] = 'not valid'

        if request.is_admin:
            score = 42

        score += scoring.get_score(0, arguments.phone, arguments.email, arguments.birthday,
                                   arguments.gender, arguments.first_name, arguments.last_name)

        return {'score': score, 'errors': errors}, OK


class ClientsInterestsRequest(Request):
    client_ids = models.ClientIDsField(required=True)
    date = models.DateField(required=False, nullable=True)


class ClientsInterestsHandler(RequestHandler):
    request_type = ClientsInterestsRequest

    def handle(self, request, arguments, ctx, store):
        ctx['nclients'] = len(arguments.client_ids)
        return {cid: scoring.get_interests(store, cid) for cid in arguments.client_ids}, OK


class MethodRequest(Request):
    account = models.CharField(required=False, nullable=True)
    login = models.CharField(required=True, nullable=True)
    token = models.CharField(required=True, nullable=True)
    arguments = models.ArgumentsField(required=True, nullable=True)
    method = models.CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def method_handler(request, ctx, store):
    methods_map = {
        'online_score': OnlineScoreHandler,
        'clients_interests': ClientsInterestsHandler,
    }
    response, code = None, 200
    body = request['body']
    method_request = MethodRequest(request['body'])

    try:
        method = method_request.request['method']
    except KeyError as e:
        return {}, 422

    handler_cls = methods_map.get(method)
    if not handler_cls:
        return 'Method Not Found', NOT_FOUND
    response, code = handler_cls().validate_handle(method_request,
                                                   handler_cls.request_type(method_request.arguments),
                                                   ctx, store)

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        'method': method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {'request_id': self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip('/')
            logging.info('%s: %s %s' % (self.path, data_string, context['request_id']))
            if path in self.router:
                try:
                    response, code = self.router[path]({'body': request, 'headers': self.headers}, context, self.store)
                except Exception as e:
                    logging.exception('Unexpected error: %s' % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if code not in ERRORS:
            r = {'response': response, 'code': code}
        else:
            r = {'error': response or ERRORS.get(code, 'Unknown Error'), 'code': code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-p', '--port', action='store', type=int, default=8080)
    op.add_option('-l', '--log', action='store', default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename='./log/log.log',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(('localhost', opts.port), MainHTTPHandler)
    logging.info('Starting server at %s' % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

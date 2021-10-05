#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
# from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'
# logging.basicConfig(filename='./log/log.log',
#                     # encoding='utf-8',
#                     level=logging.DEBUG,
#                     format=FORMAT
#                     )
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class CharField(object):
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        # self.value = None

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a string")


class ArgumentsField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def check(self, value):
        if isinstance(value, dict):
            return value
        raise ValueError("value is not a dictionary")


class EmailField(CharField):
    def check(self, value):
        value = super(EmailField, self).check(value)
        if "@" in value:
            return value
        raise ValueError("value is not an email")


class PhoneField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a phone")


class DateField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def check(self, value):
        if type(value) in (datetime.datetime, datetime.date):
            return value
        raise ValueError("value is not a datetime")


class BirthDayField(DateField):
    def check(self, value):
        value = super(EmailField, self).check(value)
        return value


class GenderField(object):
    def __init__(self, required, nullable):
        self.required = required
        self.nullable = nullable

    def check(self, value):
        if value in [0, 1, 2]:
            return GENDERS[value]
        raise ValueError("value is not a datetime")


class ClientIDsField(object):
    def __init__(self, required):
        self.required = required

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a phone")


class RequestHandler(object):
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
            if isinstance(v, Field):
                v.name = k
                field_list.append(v)

        cls = super(RequestMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = field_list
        return cls


class Request(object):
    __metaclass__ = RequestMeta

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
        return ", ".join(self.errors)


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class OnlineScoreHandler(RequestHandler):
    request_type = OnlineScoreRequest

    def handle(self, request, arguments, ctx, store):
        self.score = 0
        if request.is_admin:
            self.score = 42

        errors = {}

        try:
            arg_phone = arguments.phone.check(request.request['arguments']['phone'])
        except:
            arg_phone = None
            errors['phone'] = 'not valid'

        try:
            arg_email = arguments.email.check(request.request['arguments']['email'])
        except:
            arg_email = None
            errors['email'] = 'not valid'

        try:
            arg_birthday = arguments.birthday.check(request.request['arguments']['birthday'])
        except:
            arg_birthday = None
            errors['birthday'] = 'not valid'

        try:
            arg_first_name = arguments.first_name.check(request.request['arguments']['first_name'])
        except:
            arg_first_name = None
            errors['first_name'] = 'not valid'

        try:
            arg_last_name = arguments.last_name.check(request.request['arguments']['last_name'])
        except:
            arg_last_name = None
            errors['last_name'] = 'not valid'

        try:
            arg_gender = arguments.gender.check(request.request['arguments']['gender'])
        except:
            arg_gender = None
            errors['gender'] = 'not valid'

        self.score += scoring.get_score(0, arg_phone, arg_email, arg_birthday,
                                        arg_gender, arg_first_name, arg_last_name)

        return {'score': self.score, 'errors': errors}, OK


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class ClientsInterestsHandler(RequestHandler):
    request_type = ClientsInterestsRequest

    def handle(self, request, arguments, ctx, store):
        ctx["nclients"] = len(arguments.client_ids)
        return {cid: scoring.get_interests(store, cid) for cid in arguments.client_ids}, OK


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def method_handler(request, ctx, store):
    methods_map = {
        "online_score": OnlineScoreHandler,
        "clients_interests": ClientsInterestsHandler,
    }
    response, code = None, 200
    body = request['body']
    method_request = MethodRequest(request["body"])
    handler_cls = methods_map.get(method_request.request['method'])
    if not handler_cls:
        return "Method Not Found", NOT_FOUND
    response, code = handler_cls().validate_handle(method_request,
                                                   handler_cls.request_type(method_request.arguments),
                                                   ctx, store)

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        # filename='./log/log.log',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

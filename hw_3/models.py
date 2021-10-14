from datetime import datetime

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field:
    def __init__(self, nullable=False, required=False):
        self.nullable = nullable
        self.required = required

    def check(self, value):
        return value


class CharField(Field):

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a string")


class ArgumentsField(Field):

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


class PhoneField(Field):

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a phone")


class DateField(Field):

    def check(self, value):
        try:
            d = datetime.strptime(value, '%d.%m.%Y')
            return value
        except:
            raise ValueError("value is not a datetime")


class BirthDayField(DateField):
    def check(self, value):
        value = super(BirthDayField, self).check(value)
        return value


class GenderField(Field):

    def check(self, value):
        if value in [0, 1, 2]:
            return GENDERS[value]
        raise ValueError("value is not a datetime")


class ClientIDsField(Field):

    def check(self, value):
        if isinstance(value, str):
            return value
        raise ValueError("value is not a phone")

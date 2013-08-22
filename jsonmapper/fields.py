from types import NoneType
from jsonmapper.exceptions import ValidationError
import numbers

class Field(object):

    def __init__(self, *args, **kwargs):

        if 'default' in kwargs:
            self.default = kwargs.pop('default')

        self.validators = []

        if 'validator' in kwargs:
            self.validators.append(kwargs.pop('validator'))

        if kwargs:
            raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

        if len(args) > 0:
            raise TypeError("Field.__init__() takes no positional arguments")

    def contribute_to_class(self, cls, name):
        self.name = name
        cls._fields.append(self)

    def validate(self, value):
        for validator in self.validators:
            validator(value)

    def load(self, source):
        self.validate(source)
        return source

    def json_encode(self, value):
        return value


class NumericField(Field):

    def __init__(self,  min_val=None, max_val=None, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
        self.validators.append(self.check_numeric)

        if not isinstance(min_val, NoneType):
            self.min_val = min_val
            self.validators.append(self.check_min_val)

        if not isinstance(max_val, NoneType):
            self.max_val = max_val
            self.validators.append(self.check_max_val)

    @staticmethod
    def check_numeric(value):
        if not isinstance(value, numbers.Number):
            raise ValidationError("Value '%s' is not numeric" % repr(value))

    def check_max_val(self, value):
        if value > self.max_val:
            raise ValidationError("Value %d exceeds maximum %d" % (value, self.max_val))

    def check_min_val(self, value):
        if value < self.min_val:
            raise ValidationError("Value %d less than minimum %d" % (value, self.min_val))


class IntField(NumericField):

    def __init__(self, *args, **kwargs):
        NumericField.__init__(self, *args, **kwargs)
        self.validators.append(self.validate_int)

    def validate_int(self, value):
        if int(value) != value:
            raise ValidationError("Value '%s' is not integral" % repr(value))


class SequenceField(Field):

    def __init__(self, max_len=None, min_len=None, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

        if not isinstance(max_len, NoneType):
            self.max_len = max_len
            self.validators.append(self.check_max_len)

        if not isinstance(min_len, NoneType):
            self.min_len = min_len
            self.validators.append(self.check_min_len)

    def check_max_len(self, value):
        if len(value) > self.max_len:
            raise ValidationError('Length %d exceeds maximum %d' % (len(value), self.max_len))

    def check_min_len(self, value):
        if len(value) < self.min_len:
            raise ValidationError('Length %d less than minimum %d' % (len(value), self.min_len))


class StringField(SequenceField):

    def __init__(self, allow_unicode=True, *args, **kwargs):
        SequenceField.__init__(self, *args, **kwargs)
        self.allow_unicode = allow_unicode
        self.validators.append(self.validate_string)

    def validate_string(self, value):
        if self.allow_unicode:
            allowed_types = (str, unicode)
        else:
            allowed_types = (str,)

        if not isinstance(value, allowed_types):
            raise ValidationError('Value %s is not a string' % repr(value))

class ArrayField(SequenceField):

    def __init__(self, field_type, *args, **kwargs):
        SequenceField.__init__(self, *args, **kwargs)
        self.field_type = field_type
        self.validators.append(self.validate_array)
        self.validators.append(self.validate_items)

    @staticmethod
    def validate_array(value):
        if not isinstance(value, list):
            raise ValidationError("Value '%s' is not a valid array" % repr(value))

    def validate_items(self, value):
        for item in value:
            self.field_type.validate(item)

    def json_encode(self, value):
        return [self.field_type.json_encode(item) for item in value]


class DictField(SequenceField):

    def __init__(self, field_type, *args, **kwargs):
        SequenceField.__init__(self, *args, **kwargs)
        self.field_type = field_type
        self.validators.append(self.validate_dict)
        self.validators.append(self.validate_items)

    @staticmethod
    def validate_dict(value):
        if not isinstance(value, dict):
            raise ValidationError("Value '%s' is not a valid dict" % repr(value))

    def validate_items(self, value):
        for key, item in value.items():
            self.field_type.validate(item)

    def json_encode(self, value):
        return {key: self.field_type.json_encode(item) for (key, item) in value.items()}


class ObjectField(Field):

    def __init__(self, object_type, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
        self.object_type = object_type
        self.validators.append(self.validate_fields)

    def validate_fields(self, value):
        for field in self.object_type._fields:
            if not hasattr(value, field.name):
                raise ValidationError("Missing field %s" % field.name)

            field.validate(getattr(value, field.name))

    def load(self, value):
        value = self.object_type.load(value)
        return value

    def json_encode(self, value):
        return value.json_equivalent()
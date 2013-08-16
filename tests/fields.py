__author__ = 'MegabytePhreak'

import unittest

from jsonmapper.fields import *
from jsonmapper import Loadable
import jsonmapper.exceptions as exceptions


class TestFields(unittest.TestCase):

    def test_IntField(self):

        f = IntField()

        f.validate(1)
        f.validate(1.0)
        f.validate(1L)
        self.assertRaises(exceptions.ValidationError, f.validate, "")
        self.assertRaises(exceptions.ValidationError, f.validate, 1.1)

        self.assertEquals(f.load(10), 10)
        self.assertEquals(f.load(11.0), 11)
        self.assertRaises(exceptions.ValidationError, f.load, 1.21)

        self.assertFalse(hasattr(f, 'default'))

        f = IntField(min_val=0, max_val=10, default=1)

        self.assertTrue(hasattr(f, 'default'))
        self.assertEquals(f.default, 1)

        f.validate(2)
        f.validate(0)
        f.validate(10)
        self.assertRaises(ValidationError, f.validate, -1)
        self.assertRaises(ValidationError, f.validate, 11)

        self.assertEquals(f.load(5), 5)
        self.assertRaises(ValidationError, f.load, -1)
        self.assertRaises(ValidationError, f.load, 11)

    def test_StringField(self):

        f = StringField()

        f.validate("")
        f.validate(u"")
        f.validate("Hello, World!")
        f.validate(u"Hello, World!")
        self.assertRaises(exceptions.ValidationError, f.validate, 1)

        f = StringField(allow_unicode=False)

        f.validate("")
        f.validate("Hello, World!")
        self.assertRaises(exceptions.ValidationError, f.validate, u"")
        self.assertRaises(exceptions.ValidationError, f.validate, u"Hello, World!")

        f = StringField(default=" ", max_len=5, min_len=1)

        self.assertEquals(f.default, ' ')
        self.assertRaises(exceptions.ValidationError, f.validate, '')
        f.validate('1')
        f.validate('12')
        f.validate('123')
        f.validate('1234')
        f.validate('12345')
        self.assertRaises(exceptions.ValidationError, f.validate, '123456')

    def test_ArrayField(self):

        f = ArrayField(IntField())

        f.validate([1, 2, 3])
        f.validate([])
        self.assertRaises(exceptions.ValidationError, f.validate, [1, 2, '3'])
        self.assertRaises(exceptions.ValidationError, f.validate, ['1', 2, 3])

        f = ArrayField(NumericField(min_val=0.0, max_val=1.0), min_len=1, max_len=3)

        f.validate([0])
        f.validate([0.0, 0.5, 1.0])

        self.assertRaises(exceptions.ValidationError, f.validate, [-1])
        self.assertRaises(exceptions.ValidationError, f.validate, [1.1])
        self.assertRaises(exceptions.ValidationError, f.validate, [])
        self.assertRaises(exceptions.ValidationError, f.validate, [0, 1, 2, 3])

        self.assertRaises(exceptions.ValidationError, f.validate, {'a': 1})

    def test_DictField(self):

        f = DictField(IntField())

        f.validate({'a': 1, 'b': 2})

    def test_validator(self):

        def my_validator(value):
            if value == 42:
                raise ValidationError("You can't just throw the meaning of life the universe and everything around")

        f = Field(validator=my_validator)

        f.validate(1.0)
        self.assertRaises(ValidationError, f.validate, 42)

        self.assertEquals(f.load(1.21), 1.21)
        self.assertRaises(ValidationError, f.load, 42)

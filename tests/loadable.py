__author__ = 'MegabytePhreak'

import unittest

from jsonmapper import Loadable
from jsonmapper.fields import *
import jsonmapper.exceptions as exceptions


class TestLoadable(unittest.TestCase):

    def test_basic(self):
        class basic(Loadable):
            foo = IntField(default=1, min_val=0, max_val=10)

        self.assertEquals(basic.load({}).foo, 1)
        self.assertEquals(basic().foo, 1)
        self.assertEquals(basic(9).foo, 9)
        self.assertEquals(basic(foo=8).foo, 8)
        self.assertEquals(basic.load({'foo': 7}).foo, 7)


        self.assertRaises(exceptions.ValidationError, basic, 11)
        self.assertRaises(exceptions.ValidationError, basic, foo=-1)
        self.assertRaises(exceptions.ValidationError, basic.load, {'foo': 11})
        self.assertRaises(exceptions.ValidationError, basic.load, {'foo': -1})

        class c2(Loadable):
            foo = IntField()
            bar = IntField(default=1)

        self.assertRaises(TypeError, c2)
        self.assertRaises(exceptions.LoadError,c2.load,{})
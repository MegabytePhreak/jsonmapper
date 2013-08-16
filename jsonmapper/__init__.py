from jsonmapper.fields import *
from jsonmapper.exceptions import LoadError


class LoadableBase(type):

    """
    Metaclass for loadable objects
    """

    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        new_class = super(LoadableBase, cls).__new__(cls, name, bases, {'__module__': module})

        new_class._fields = []
        for attrname, attrvalue in attrs.items():
            new_class.add_to_class(attrname, attrvalue)

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Loadable(object):
    """ Base class for loadable data types.

    >>> class foo(Loadable):
    ...     bar = IntField(default=0)
    ...     baz = StringField()
    >>> quincrux = foo.load({ 'baz': 'foobar' })
    >>> quincrux.bar
    0
    >>> quincrux.baz
    'foobar'

    """
    __metaclass__ = LoadableBase

    def __init__(self, *args, **kwargs):

        args_len = len(args)
        if args_len > len(self._fields):
            raise IndexError("Number of args exceeds number of fields")

        field_iter = iter(self._fields)
        for value, field in zip(args, field_iter):
            field.validate(value)
            setattr(self, field.name, value)
            if field.name in kwargs:
                field.validate(kwargs[field.name])
                setattr(self, field.name, kwargs.pop(field.name))

        for field in field_iter:
            if field.name in kwargs:
                field.validate(kwargs[field.name])
                setattr(self, field.name, kwargs.pop(field.name))
            elif hasattr(field, 'default'):
                setattr(self, field.name, field.default)
            else:
                raise TypeError("No value or default for field %s" % field.name)

        if kwargs:
            raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

    @classmethod
    def load(cls, source):
        fields = {}

        for field in cls._fields:
            if field.name in source:
                fields[field.name] = field.load(source[field.name])
            elif hasattr(field, 'default'):
                fields[field.name] = field.default
            else:
                raise LoadError("Missing field '%s' " % field.name)

        for key, value in source.items():
            if not key in fields:
                raise LoadError("Excess element %s in data" % key)

        return cls(**fields)

if __name__ == "__main__":

    class test1(Loadable):
        var1 = IntField(default=0, min_val=1, max_val=3)

    class test2(Loadable):
        name = StringField(allow_unicode=False)
        var1 = IntField(default=0, min_val=0, max_val=16)
        var2 = ObjectField(test1, default=None)

        def foo(self):
            print 'This is foo'

    test2.load({'name': 'UsesDefault'}).foo()
    #test.load({'var1': -1})
    loaded = test2.load({'name': u'a', 'var1': 8, 'var2': {'var1': 1.0}})
    print loaded.var1

    #test.load({'var1': 17})
    #test.load({'var1': 8, 'stuff': None})

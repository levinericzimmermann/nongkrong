import functools
import operator


def __make_timeline(name, nested_structure):
    def make_property_function(name, depth, attribute_names):
        if depth == 0:

            def getter(self) -> tuple:
                return self._TimeLine__iterable

        else:

            def getter(self) -> tuple:
                iterable = self._TimeLine__iterable
                current_attribute = attribute_names[depth]
                iterable = tuple(
                   getattr(item, current_attribute) for item in iterable
                )
                iterable = functools.reduce(operator.add, iterable)
                return tuple(iterable)

        return getter

    def make_size_per_attribute_property(name):
        def getter(self) -> tuple:
            return tuple(item.size for item in getattr(self, name))

        return getter

    def make_amount_per_attribute_property(name):
        def getter(self) -> tuple:
            return len(getattr(self, name))

        return getter

    def make_size_property(highest_attribute):
        def getter(self) -> int:
            return sum(getattr(self, "{0}_size".format(highest_attribute)))

        return getter

    class TimeLine(object):
        def __init__(self, *item):
            self.__iterable = tuple(item)

        def __repr__(self) -> str:
            return str(self.__iterable)

        def reverse(self) -> "TimeLine":
            return type(self)(*tuple(reversed(self.__iterable)))

        def add(self, item) -> "TimeLine":
            return type(self)(self.__iterable + (item,))

    attribute_names = tuple(c.__name__.lower() for c in nested_structure)
    for depth, attribute in enumerate(attribute_names):
        getter_method = make_property_function(attribute, depth, attribute_names)
        size_method = make_size_per_attribute_property(attribute)
        amount_method = make_amount_per_attribute_property(attribute)
        setattr(TimeLine, attribute, property(getter_method))
        setattr(TimeLine, "{0}_size".format(attribute), property(size_method))
        setattr(TimeLine, "{0}_amount".format(attribute), property(amount_method))

    TimeLine.__name__ = name
    TimeLine.__hierarchy = attribute_names
    TimeLine.nested_structure = property(lambda self: self.__hierarchy)
    setattr(TimeLine, "size", property(make_size_property(attribute_names[0])))
    return TimeLine


class Unit(object):
    def __init__(self, size: int) -> None:
        self.__size = size

    def __repr__(self) -> str:
        return "U{0}".format(self.size)

    @property
    def size(self) -> int:
        return self.__size


Compound = __make_timeline("Compound", (Unit,))
Metre = __make_timeline("Metre", (Compound, Unit))
TimeFlow = __make_timeline("TimeFlow", (Metre, Compound, Unit))

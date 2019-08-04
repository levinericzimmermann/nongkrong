import functools
import itertools
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
                iterable = tuple(getattr(item, current_attribute) for item in iterable)
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


class DividedUnit(Unit):
    """Class for Units that are divided in
    middle kecapi pitches and high kecapi pitches
    """

    def __init__(self, divisions: tuple) -> None:
        Unit.__init__(self, sum(divisions))
        self.__divisions = divisions

    @property
    def divisions(self) -> tuple:
        return self.__divisions

    @property
    def amount_divisions(self) -> int:
        return len(self.divisions)

    def __repr__(self) -> str:
        return "DU{0}".format(self.size)


class SingleDividedUnit(DividedUnit):
    def __init__(self, size: int, division_size: int) -> None:
        assert size % division_size == 0
        self.__division_size = division_size
        DividedUnit.__init__(self, (division_size,) * (size // division_size))

    @property
    def division_size(self) -> int:
        return self.__division_size

    def __repr__(self) -> str:
        return "SU{0}({1} * {2})".format(
            self.size, self.amount_divisions, self.division_size
        )


Compound = __make_timeline("Compound", (Unit,))
Metre = __make_timeline("Metre", (Compound, Unit))
TimeFlow = __make_timeline("TimeFlow", (Metre, Compound, Unit))


def define_metre_by_structure(structure: tuple) -> Metre:
    m = []
    for com in structure:
        c = []
        for size in com:
            c.append(Unit(size))
        m.append(Compound(*c))
    return Metre(*m)


class MetreMaker(object):
    """Input expect tuples with two elements per tuple.

    First element has to be an iterable thats infinitly callable.
    The second element is of type bool.
    It declares if the iterable shall repeat the same element
    for multiple
    """

    def __init__(self, *iterable_shall_repeat_pair):
        self.__data = iterable_shall_repeat_pair
        self.__length_data = len(iterable_shall_repeat_pair)

    def make_n_of_m(self, m: int, n: int) -> tuple:
        if self.__data[m][1]:
            return tuple((next(self.__data[m][0]),) * n)
        else:
            return tuple(next(self.__data[m][0]) for i in range(n))

    def _test_if_big_enough(self, needed):
        try:
            assert self.__length_data >= needed
        except AssertionError:
            msg = "Not enough information to make units. "
            msg += "Only {0} iterables has been added, but ".format(self.__length_data)
            msg += " {0} iterables are necessary.".format(needed)

    def make_n_units(self, n: int) -> tuple:
        self._test_if_big_enough(2)
        kecapi0_sizes = self.make_n_of_m(1, n)
        kecapi1_sizes = tuple(self.make_n_of_m(0, k0size) for k0size in kecapi0_sizes)
        units = []
        for k0size, k1size in zip(kecapi0_sizes, kecapi1_sizes):
            if len(set(k1size)) == 1:
                un = SingleDividedUnit(k0size * k1size[0], k1size[0])
            else:
                un = DividedUnit(k1size)
            units.append(un)
        return tuple(units)

    def make_n_compounds(self, n: int) -> tuple:
        self._test_if_big_enough(3)
        return tuple(
            Compound(*self.make_n_units(csize)) for csize in self.make_n_of_m(2, n)
        )

    def make_n_metres(self, n: int) -> tuple:
        self._test_if_big_enough(4)
        return tuple(
            Metre(*self.make_n_compounds(msize)) for msize in self.make_n_of_m(3, n)
        )


class LoopMaker(MetreMaker):
    """Automatically converts the incoming tuples to endless cycles"""

    def __init__(self, *tuple_shall_repeat_pair):
        iterable_shall_repeat_pairs = tuple(
            (itertools.cycle(pair[0]), pair[1]) for pair in tuple_shall_repeat_pair
        )
        MetreMaker.__init__(self, *iterable_shall_repeat_pairs)

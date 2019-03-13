class Mode(object):
    """A Mode represents a specific repertoire of musical pitches.

    Every Mode contains three elementar prime numbers (x, y, z)
    and one prime number that's missing (N). Additionaly
    every Mode has a gender (True or False, ^+1 vs ^-1).
    """

    def __init__(self, x, y, z, U, gender=True):
        for p in (x, y, z, U):
            try:
                assert type(p) == int
            except AssertionError:
                raise TypeError("X, Y, Z and U has to be integer.")

        try:
            assert type(gender) == bool
        except AssertionError:
            raise TypeError("Gender has to be True or False.")

        self.__x = x
        self.__y = y
        self.__z = z
        self.__U = U
        self.__gender = gender

    @property
    def x(self) -> int:
        return int(self.__x)

    @property
    def y(self) -> int:
        return int(self.__y)

    @property
    def z(self) -> int:
        return int(self.__z)

    @property
    def U(self) -> int:
        return int(self.__U)

    @property
    def gender(self) -> bool:
        return bool(self.__gender)

    @property
    def __key(self) -> tuple:
        return (self.x, self.y, self.z, self.gender)

    def __hash__(self) -> int:
        return hash(self.__key)

    def __repr__(self) -> str:
        if self.gender:
            sep = "+"
        else:
            sep = "-"
        return "{0}{3}{1}{3}{2}".format(*self.__key[:-1], sep)

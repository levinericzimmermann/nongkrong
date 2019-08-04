from nongkrong.harmony import expattern


"""This module provides a pool of handwritten Expansion - Pattern."""


PATTERN = (
    expattern.Pattern(expattern.Splinter((2, 1), "o o", "o a", "o o")),
    expattern.Pattern(
        expattern.Splinter((2, 2), "o o o o", "o o a o", "o a o a"),
        expattern.Splinter((2, 2), "o o o o", "o o a o", "o o o a"),
    ),
    expattern.Pattern(
        expattern.Splinter((2, 3), "o o o o o o", "o o o a o o", "o a b a o a"),
        expattern.Splinter((2, 3), "o o o o o o", "o o o a o o", "o o b a b a"),
    ),
    expattern.Pattern(
        expattern.Splinter((3, 1), "o o o", "o a b", "o o o"),
        expattern.Splinter((3, 1), "o o o", "a b a", "o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter((3, 1), "o o o", "o a a", "o o o"),
        expattern.Splinter((3, 1), "o o o", "o o a", "o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter((3, 2), "o o o a o o", "o o a o a o", "o a o o o a")
    ),
    expattern.Pattern(
        expattern.Splinter((3, 2), "o o o o o o", "o o a o b o", "o a o a b a"),
        expattern.Splinter((3, 2), "o o o o o o", "a o b o a o", "o a b a o a"),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (3, 3), "o o o o o o o o o", "o o o a o o b o o", "o a b a o a b a a"
        ),
        expattern.Splinter(
            (3, 3), "o o o o o o o o o", "a o o b o o a o o", "o a a b a o a b a"
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (3, 3), "o o o o o o o o o", "o o o a o o a o o", "o a b a o b a o a"
        )
    ),
    expattern.Pattern(
        expattern.Splinter((4, 1), "o o a o", "o a o a", "o o o o"),
        expattern.Splinter((4, 1), "o o a o", "o o o a", "o o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (4, 2), "o o o o o o o o", "o o a o b o a o", "o a a b o b a b"
        ),
        expattern.Splinter(
            (4, 2), "o o o o o o o o", "o o o o b o a o", "o b a b b b a a"
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (4, 2), "o o o o a o o o", "o o a o o o a o", "o a o a o a o a"
        ),
        expattern.Splinter(
            (4, 2), "o o o o a o o o", "o o o o o o a o", "o a o a o a o a"
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (4, 3),
            "o o o o o o o o o o o o",
            "o o o a o o b o o a o o",
            "o a b a o a b a o a b a",
        )
    ),
    expattern.Pattern(
        expattern.Splinter(
            (4, 3),
            "o o o o o o o o o o o o",
            "o o o a o o b o o a o o",
            "o b a o a b o b a o a o",
        ),
        expattern.Splinter(
            (4, 3),
            "o o o o o o o o o o o o",
            "o o o o o o b o o a o o",
            "o b a o a b o b a a o a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter((5, 1), "o o a a o", "o a o o a", "o o o o o"),
        expattern.Splinter((5, 1), "o o o a o", "o o a o a", "o o o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (5, 2), "o o o o o o o o o o", "o o a o b o b o a o", "o a o a b o b a o a"
        ),
        expattern.Splinter(
            (5, 2), "o o o o o o o o o o", "o o o o a o b o a o", "o a b a o a b a o a"
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (5, 3),
            "o o o o o o o o o o o o o o o",
            "o o o a o o b o o b o o a o o",
            "o b a o a b o b b o b a o a b",
        ),
        expattern.Splinter(
            (5, 3),
            "o o o o o o o o o o o o o o o",
            "o o o o o o a o o b o o a o o",
            "o b a o a b o b b o b a o a a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter((6, 1), "o o o b o o", "o a b- o b- a", "o o o o o o"),
        expattern.Splinter((6, 1), "o o o a o o", "o a b- a b- a", "o o o o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (6, 2),
            "o o o o o o o o o o o o",
            "o o a o b o o o b o a o",
            "o a a b o b a b o b a a",
        ),
        expattern.Splinter(
            (6, 2),
            "o o o o o o o o o o o o",
            "o o a o b o o o o o a o",
            "o a a b o b a b o b a a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (6, 3),
            "o o o o o o o o o o o o o o o o o o",
            "o o o a o o b o o o o o b o o a o o",
            "o b a o a b o b a a a b o b a o o a",
        ),
        expattern.Splinter(
            (6, 3),
            "o o o o o o o o o a o o o o o o o o",
            "o o o a o o b o o a o o b o o a o o",
            "o b a o a b o b a o a b o b a a a b",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter((7, 1), "o o o o b o o", "o a a b- o b- a", "o o o o o o o"),
        expattern.Splinter((7, 1), "o o o o b o o", "o o a b- o b- a", "o o o o o o o"),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (7, 2),
            "o o o o o o o o o o o o o o",
            "o o a o b o a o o o a o b o",
            "o a a b o b a a o a a b b a",
        ),
        expattern.Splinter(
            (7, 2),
            "o o o o o o a o o o o o o o",
            "a o b o a o o o a o b o a o",
            "o a b a o a o a o a b a o a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (7, 2),
            "o o o o o o o o o o o o o o",
            "o o a o b o a o o o b o a o",
            "o a a b o o a b o a b a o a",
        ),
        expattern.Splinter(
            (7, 2),
            "o o o o o o o o o o o o o o",
            "o o a o b o o o o o b o a o",
            "o a a b o b o b o b o b a a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (7, 3),
            "o o o o o o o o o o o o o o o o o o o o o",
            "o o o a o o b o o a o o o o o b o o a o o",
            "o a b a a b o b a o a b a a b o b a o a a",
        ),
        expattern.Splinter(
            (7, 3),
            "o o o o o o o o o o o o o o o o o o o o o",
            "o o o a o o b o o o o o o o o b o o a o o",
            "o a b a a b o b a o a b o a b o b a a a a",
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (8, 1), "o o o o a o o o", "o a o a o a o a", "o o a o o o a o"
        ),
        expattern.Splinter(
            (8, 1), "o o o o a o o o", "o a o a o o o a", "o o a o o o a o"
        ),
    ),
    expattern.Pattern(
        expattern.Splinter(
            (8, 2),
            "o o o o o o o o a o o o o o o o",
            "o o a o b o a o a o o o b o a o",
            "o a a b o b a a o a a b o b a a",
        )
    ),
    expattern.Pattern(
        expattern.Splinter(
            (8, 3),
            "o o o o o o o o o o o o a o o o o o o o o o o o",
            "o o o a o o b o o a o o o o o a o o b o o a o o",
            "o a a o a b o b a o a a o a a o a b o b a o a a",
        )
    ),
)

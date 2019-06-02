from nongkrong.harmony import functions


def is_m(f) -> bool:
    return f.identity == ("y", "z")


def is_w(f) -> bool:
    return f.identity == ("x", "z")


def is_o(f) -> bool:
    return f.identity == ("x", "y")


def is_n(f) -> bool:
    return f.identity == ("U", "z")


def is_om(f) -> bool:
    return f.identity == ("U", "y")


def is_ow(f) -> bool:
    return f.identity == ("U", "x")


def convert_relevant_prime_due_to_modulation(
    relevant_prime, mode0, mode1
) -> tuple:
    """Return 2-element tuple (Function, prime index)
    where Function is of type nongkrong.harmony.functions.Function
    and 'prime index' indicates which prime one of
    (x, y, z, U) from the first mode will be played.
    """

    mode0_primes = (mode0.x, mode0.y, mode0.z, mode0.U)
    mode1_primes = (mode1.x, mode1.y, mode1.z, mode1.U)
    return mode0_primes.index(mode1_primes[relevant_prime])


def convert_function_due_to_modulation(func, mode0, mode1) -> functions.Function:
    """Return 2-element tuple (Function, prime index)
    where Function is of type nongkrong.harmony.functions.Function
    and 'prime index' indicates which prime one of
    (x, y, z, U) from the first mode will be played.
    """

    function_primes = func._Function__key(mode1)
    mode0_primes = (mode0.x, mode0.y, mode0.z, mode0.U)
    mode0_prime_names = ("x", "y", "z", "U")
    prime_names = tuple(
        mode0_prime_names[mode0_primes.index(p)] for p in function_primes
    )
    rev_prime_names = tuple(reversed(prime_names))
    for func_name in functions.FUNCTIONS:
        func = functions.FUNCTIONS[func_name]
        identity = func.identity
        if identity == prime_names or identity == rev_prime_names:
            return func

    msg = "Function with combination {0} doesn't exist yet.".format(prime_names)
    raise NotImplementedError(msg)

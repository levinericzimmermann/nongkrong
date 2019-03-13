import unittest

from nongkrong.harmony import genesis


class ModeTest(unittest.TestCase):
    def test_attributes(self):
        a, b, c, d = (3, 5, 7, 9)
        gen = genesis.Genesis(a, b, c, d)
        mode0_key = "3+5+7"
        mode0_parallel_key = "3+5+9"
        mode0_left_neighbour_key = "5+3+7"
        mode0_right_neighbour_key = "3+7+5"
        mode0_opposite_key = "3-5-7"
        mode0 = gen.mode(mode0_key)
        mode0_parallel = gen.parallel(mode0)
        mode0_left_neighbour = gen.left_neighbour(mode0)
        mode0_right_neighbour = gen.right_neighbour(mode0)
        mode0_opposite = gen.opposite(mode0)
        self.assertEqual(repr(mode0), mode0_key)
        self.assertEqual(mode0, gen.mode(mode0))
        self.assertEqual(mode0_parallel, gen.mode(mode0_parallel_key))
        self.assertEqual(mode0_left_neighbour, gen.mode(mode0_left_neighbour_key))
        self.assertEqual(mode0_right_neighbour, gen.mode(mode0_right_neighbour_key))
        self.assertEqual(mode0_opposite, gen.mode(mode0_opposite_key))

    def test_false_init(self):
        with self.assertRaises(ValueError):
            genesis.Genesis(7, 5, 7, 9)  # not unique

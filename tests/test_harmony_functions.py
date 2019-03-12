import unittest

from nongkrong.harmony import modes


class ModeTest(unittest.TestCase):
    def test_attributes(self):
        x, y, z, N, gender = (3, 5, 7, 9, True)
        mode = modes.Mode(x, y, z, N, True)
        self.assertEqual(mode.x, x)
        self.assertEqual(mode.y, y)
        self.assertEqual(mode.z, z)
        self.assertEqual(mode.N, N)
        self.assertEqual(mode.gender, gender)
        self.assertEqual(repr(mode), "{0}+{1}+{2}".format(x, y, z))

    def test_false_init(self):
        with self.assertRaises(TypeError):
            modes.Mode(1.3, "hi", 4, 3, True)
        with self.assertRaises(TypeError):
            modes.Mode(3, 5, 7, 9, "HI")

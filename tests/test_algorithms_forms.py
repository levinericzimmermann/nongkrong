import unittest

from nongkrong.metre import metre
from nongkrong.harmony import cadence
from nongkrong.harmony import functions
from nongkrong.harmony import genesis

from nongkrong.algorithms.forms import lancaran


class LancaranTest(unittest.TestCase):
    def test_cadence_conversion(self):
        gen = genesis.Genesis(3, 5, 7, 9)
        mode = gen.mode("7+5+3")
        funcs = (functions.FUNCTIONS[f] for f in ("M", "w", "m", "o", "M"))
        melody = cadence.Cadence(funcs, time=(1, 1, 1, 1, 1))
        loopsize = 4
        m_structure = ((4, 4, 4), (3, 3, 3, 3), (3, 3, 3, 3), (4, 4, 4))
        meter = metre.define_metre_by_structure(m_structure)
        lnc = lancaran.Lancaran(mode, melody, meter, mode, loopsize)
        cadences = lnc.convert2cadences()
        print(meter.size)
        print(cadences[4][0].duration)

        assert meter.size == cadences[4][0].duration

        assert 3 is None

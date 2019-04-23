import unittest

from mu.sco import old
from mu.mel import ji
from mu.mel import mel

from nongkrong.metre import metre
from nongkrong.score import score


class TranslationTest(unittest.TestCase):
    def test_translation(self):
        u3 = metre.Unit(3)
        u2 = metre.Unit(2)
        com0 = metre.Compound(u3, u2, u2)
        com1 = metre.Compound(u3, u2)
        metre0 = metre.Metre(com0, com1)
        metre1 = metre.Metre(com0, com1, com1)
        timeflow = metre.TimeFlow(metre0, metre1)

        p0 = ji.JIHarmony([ji.r(1, 1)])
        p_empty = mel.TheEmptyPitch

        cadence0 = old.JICadence([old.Chord(p0, 1) for i in range(timeflow.size)])
        mdc0 = score.MDC(cadence0, timeflow, 0, False)
        self.assertEqual(mdc0[0][0][0], (p0,) * 3)
        self.assertEqual(mdc0[0][0][1], (p0,) * 2)

        cadence1 = old.JICadence([old.Chord(p0, 0.5) for i in range(timeflow.size * 2)])
        mdc1 = score.MDC(cadence1, timeflow, 0, False)
        self.assertEqual(mdc1[0][0][0], ((p0,) * 2,) * 3)

        cadence2 = cadence1.copy()
        cadence2.delay[0] = 0.25
        cadence2.dur[0] = 0.25
        cadence2.delay[1] = 0.75
        cadence2.dur[1] = 0.75
        mdc2A = score.MDC(cadence2, timeflow, 0, True)
        self.assertEqual(mdc2A[0][0][0], (((p0, p0), p0), (p0, p0), (p0, p0)))
        mdc2B = score.MDC(cadence2, timeflow, 0, False)
        self.assertEqual(mdc2B[0][0][0], (((p0, p0), p_empty), (p0, p0), (p0, p0)))

        cadence3 = cadence1.copy()
        cadence3.delay[0] = 0.75
        cadence3.dur[0] = 0.75
        cadence3.delay[1] = 0.25
        cadence3.dur[1] = 0.25
        mdc3A = score.MDC(cadence3, timeflow, 0, True)
        self.assertEqual(mdc3A[0][0][0], ((p0, (p0, p0)), (p0, p0), (p0, p0)))
        mdc3B = score.MDC(cadence3, timeflow, 0, False)
        self.assertEqual(mdc3B[0][0][0], ((p0, (p_empty, p0)), (p0, p0), (p0, p0)))

        cadence4 = old.JICadence(
            [old.Chord(p0, 1) for i in range(timeflow.unit_amount)]
        )
        mdc4 = score.MDC(cadence4, timeflow, 1, False)
        self.assertEqual(
            mdc4[0][0], ((p0, p_empty, p_empty), (p0, p_empty), (p0, p_empty))
        )

        cadence5 = old.JICadence(
            [old.Chord(p0, 1) for i in range(timeflow.compound_amount)]
        )
        mdc5 = score.MDC(cadence5, timeflow, 2, False)
        self.assertEqual(
            mdc5[0][0], ((p0, p_empty, p_empty), (p_empty, p_empty), (p_empty, p_empty))
        )

        cadence6 = old.JICadence(
            [old.Chord(p0, 1) for i in range(timeflow.unit_amount)]
        )
        mdc6 = score.MDC(cadence6, timeflow, 1, True)
        self.assertEqual(mdc6[0][0], ((p0, p0, p0), (p0, p0), (p0, p0)))

        cadence7 = old.JICadence(
            [old.Chord(p0, 1) for i in range(timeflow.compound_amount)]
        )
        mdc7 = score.MDC(cadence7, timeflow, 2, True)
        self.assertEqual(mdc7[0][0], ((p0, p0, p0), (p0, p0), (p0, p0)))

        cadence8 = old.JICadence(
            [old.Chord(p0, 1) for i in range(timeflow.metre_amount)]
        )
        mdc8 = score.MDC(cadence8, timeflow, 3, False)
        self.assertEqual(
            mdc8[0][0], ((p0, p_empty, p_empty), (p_empty, p_empty), (p_empty, p_empty))
        )

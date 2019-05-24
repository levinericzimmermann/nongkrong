from nongkrong.metre import metre
from nongkrong.delays import delays
from nongkrong.tempo import tempo
from nongkrong.harmony import shortwriting as sw


from mu.sco import old


def load_cadence(name: str, pitch=None, rhythm=None):
    if not pitch:
        pitch = sw.translate_from_file("sections/testSec/pitch/{0}".format(name))
    if not rhythm:
        with open("sections/testSec/rhythm/{0}".format(name), "r") as rhythm:
            rhythm = " ".join(rhythm.read().splitlines())
            rhythm = rhythm.split(" ")
            rhythm = tuple(float(n) for n in rhythm if n)
    return old.JICadence([old.Chord(p, r) for p, r in zip(pitch, rhythm)])


def main() -> tuple:
    names = (
        "gong",
        "siter_barung",
        "siter_panerus",
        "kecapi_plus",
        "kecapi_minus",
        "kendang",
        "tak",
    )
    cadences = list(load_cadence(name) for name in names)
    cadences[1] = (cadences[1], old.JICadence([]))
    cadences[2] = (cadences[2], old.JICadence([]))
    cadences[3] = (cadences[3], old.JICadence([]))
    cadences[4] = (cadences[4], old.JICadence([]))
    m_structure = ((5, 4, 4, 4), (5, 3, 3), (5, 2, 3))
    tf = metre.TimeFlow(metre.define_metre_by_structure(m_structure))
    de = list(None for i in range(tf.unit_amount))
    tl = tempo.TempoLine(
        (
            tempo.ANDANTE,
            tempo.ChangeTempo(1.3),
            tempo.ChangeTempo(1.4),
            tempo.ChangeTempo(1.5),
            tempo.LENTO,
        )
        + tuple(de[4:])
    )
    de[4] = delays.DELAY_LIGHT
    return tf, tuple(cadences), tl, tuple(de)


if __name__ == "__main__":
    print(main())

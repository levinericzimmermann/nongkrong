from mu.sco import old


from nongkrong.harmony import shortwriting as sw


def load_cadence(name: str, pitch=None, rhythm=None):
    if not pitch:
        pitch = sw.translate_from_file("pitch/{0}".format(name))
    if not rhythm:
        with open("rhythm/{0}".format(name), "r") as rhythm:
            rhythm = " ".join(rhythm.read().splitlines())
            rhythm = rhythm.split(" ")
            rhythm = tuple(float(n) for n in rhythm if n)
    return old.JICadence([old.Chord(p, r) for p, r in zip(pitch, rhythm)])

import functools
import operator

from mu.mel import ji


CONCERT_PITCH = 260
PRIMES = [3, 5, 7, 9]

GROUPS = []
for prime in PRIMES:
    p0 = ji.r(1, prime).normalize(2)
    p4 = p0 + ji.r(4, 1)
    rest = (ji.r(other, prime) for other in PRIMES if other != prime)
    rest = tuple(sorted(tuple(p.normalize(2) + ji.r(2, 1) for p in rest)))
    group = (p0,) + rest + (p4,)
    GROUPS.append(group)

PITCHES = functools.reduce(operator.add, GROUPS)

if __name__ == "__main__":
    import pyteqNew as pyteq

    for idx, pitches in enumerate(GROUPS + [PITCHES]):
        if idx < 4:
            name = "Group{0}".format(idx)
            delay = 0.5
            duration = 2
        else:
            name = "AllPitches"
            delay = 1
            duraton = 1

        melody = tuple(
            pyteq.MidiTone(ji.JIPitch(p, multiply=CONCERT_PITCH), delay, duration)
            for p in pitches
        )

        for p in melody:
            print(p.pitch.freq)

        unavailable_pitches = (
            30,
            32,
            34,
            42,
            44,
            46,
            73,
            75,
            78,
            80,
            82,
            85,
            87,
            90,
            92,
            94,
        )
        harp_range = tuple(n for n in range(20, 121) if n not in unavailable_pitches)
        f = pyteq.Pianoteq(melody, available_midi_notes=harp_range)
        f.export2wav(name, preset='"Concert Harp Recording"')

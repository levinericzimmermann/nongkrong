from mu.mel import ji


CONCERT_PITCH = 260
PRIMES = [2, 3, 5, 7, 9, 11]

PITCHES_POSITIVE = []
PITCHES_NEGATIVE = []
for prime in PRIMES:
    p0 = ji.r(prime, 1).normalize(2)
    p1 = ji.r(1, prime).normalize(2)
    if prime == 2:
        p0 += ji.r(2, 1)
        p1 += ji.r(2, 1)
    p2 = p1 + ji.r(4, 1)
    p3 = p0 + ji.r(4, 1)
    PITCHES_POSITIVE.append(p0)
    PITCHES_POSITIVE.append(p2)
    PITCHES_NEGATIVE.append(p1)
    PITCHES_NEGATIVE.append(p3)

if __name__ == "__main__":
    import pyteqNew as pyteq

    for idx, pitches in enumerate([PITCHES_POSITIVE, PITCHES_NEGATIVE]):
        if idx < 1:
            name = "Positive"
        else:
            name = "Negative"

        for p_idx, pitch in enumerate(sorted(pitches)):
            local_name = name + str(p_idx)
            melody = [pyteq.MidiTone(ji.JIPitch(pitch, multiply=CONCERT_PITCH), 4, 4, volume=1)]

            harp_range = tuple(
                n for n in range(20, 125)
            )
            f = pyteq.Pianoteq(melody, available_midi_notes=harp_range)
            f.export2wav(local_name, preset='"Erard Player"')

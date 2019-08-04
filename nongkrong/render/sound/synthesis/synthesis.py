import abc
import os
import sox

from mu.mel import ji
from mu.mel import mel
from mu.sco import old

from nongkrong.render.sound.synthesis import pyteq


class SoundEngine(abc.ABC):
    CONCERT_PITCH = 260

    @abc.abstractmethod
    def __call__(self, name: str, cadence: old.JICadence) -> None:
        raise NotImplementedError


class PyteqEngine(SoundEngine):
    def __init__(
        self, preset=None, fxp=None, available_midi_notes=tuple(range(128)), volume=0.7
    ):
        self.__volume = volume
        self.__available_midi_notes = available_midi_notes
        self.__preset = preset
        self.__fxp = fxp

    @property
    def volume(self) -> float:
        return self.__volume

    @property
    def preset(self) -> str:
        return self.__preset

    @property
    def fxp(self) -> str:
        return self.__fxp

    @property
    def available_midi_notes(self) -> tuple:
        return self.__available_midi_notes

    def __call__(self, name: str, cadence: old.JICadence) -> None:
        seq = []
        for chord in cadence:
            dur = float(chord.delay)
            if chord.pitch != mel.TheEmptyPitch and bool(chord.pitch):
                size = len(chord.pitch)
                for idx, pi in enumerate(chord.pitch):
                    if idx + 1 == size:
                        de = float(dur)
                    else:
                        de = 0
                    tone = pyteq.PyteqTone(
                        ji.JIPitch(pi, multiply=self.CONCERT_PITCH),
                        de,
                        dur,
                        volume=self.volume,
                    )
                    seq.append(tone)
            else:
                seq.append(old.Rest(dur))

        pt = pyteq.Pianoteq(tuple(seq), self.available_midi_notes)
        pt.export2wav(name, 1, self.preset, self.fxp)


class CsoundEngine(SoundEngine):
    @abc.abstractproperty
    def orc(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def mk_sco(self, cadence) -> str:
        raise NotImplementedError

    def __call__(self, name: str, cadence: old.JICadence) -> None:
        sfname = "{0}.wav".format(name)
        fname = "csoundsynth"
        orc_name = "{0}.orc".format(fname)
        sco_name = "{0}.sco".format(fname)
        sco = self.mk_sco(cadence)
        if sco:
            with open(orc_name, "w") as f:
                f.write(self.orc)
            with open(sco_name, "w") as f:
                f.write(sco)
            cmd0 = "csound --format=double -k 96000 -r 96000 -o {0} ".format(sfname)
            cmd1 = "{0} {1}".format(orc_name, sco_name)
            cmd = cmd0 + cmd1
            os.system(cmd)
            os.remove(orc_name)
            os.remove(sco_name)


class SampleEngine(CsoundEngine):
    """pitch2sample has to be a dict with the following structure:

        {pitch0: CYCLE((SAMPLE_NAME, PITCH_FACTOR), (SAMPLE_NAME, PITCH_FACTOR), ...),
         pitch1: CYCLE((SAMPLE_NAME, PITCH_FACTOR), ...),
         ...
         pitchN: CYCLE((SAMPLE_NAME, PITCH_FACTOR), ...)}
    """

    def __init__(self, pitch2sample: dict) -> None:
        self.__pitch2sample = pitch2sample

    @property
    def pitch2sample(self) -> dict:
        return self.__pitch2sample

    @property
    def orc(self) -> str:
        lines = (
            r"0dbfs=1",
            r"gaSend init 0",
            r"instr 1",
            r"asig diskin2 p4, p5, 0, 0, 6, 4",
            r"out asig * p6",
            r"gaSend = gaSend + (asig * 0.1)",
            r"endin",
            r"instr 2",
            r"kroomsize init 0.7",
            r"kHFDamp init 0.5",
            r"aRvbL, aRvbR freeverb gaSend, gaSend, kroomsize, kHFDamp",
            r"out (aRvbL + aRvbR) * 0.4",
            r"clear gaSend",
            r"endin",
        )
        return "\n".join(lines)

    def mk_sco(self, cadence) -> str:
        lines = []
        abs_start = cadence.delay.convert2absolute()
        for event, start in zip(cadence, abs_start):
            if event.pitch and event.pitch != mel.TheEmptyPitch:
                line = r"i1 {0}".format(start)
                for pi in event.pitch:
                    s_info = next(self.pitch2sample[pi])
                    sample_name, factor = s_info[0], s_info[1]
                    if len(s_info) == 3:
                        vol = s_info[2]
                    else:
                        vol = 1
                    duration = sox.file_info.duration(sample_name)
                    final_line = '{0} {1} "{2}" {3} {4}'.format(
                        line, duration, sample_name, factor, vol
                    )
                    lines.append(final_line)
        complete_duration = float(cadence.duration + 5)
        lines.append("i2 0 {0}".format(complete_duration))
        return "\n".join(lines)

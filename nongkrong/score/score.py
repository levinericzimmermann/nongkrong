import functools
import operator
import os
import itertools
import sys

from mu.mel import mel
from mu.mel import ji
from mu.sco import old

import nongkrong.instruments as instr

from nongkrong.metre import metre
from nongkrong.tempo import tempo
from nongkrong.render import notation
from nongkrong.render import sound


"""This module implements classes to organise compositions in hierarchical structures.

Those hierarchical structures are not meant to be changed by post processing. Once
initalised, they can't be altered anymore (immutable objects). Their main purpose is
to offer an interface between render engines of nongkrong and abstractions of musical
content in Python. The nongkrong library offers two different render engines:

    (1) Kepatihan notation via Latex (nongkrong.render.notation)
            -> render_score method
    (2) Soundfiles via Pianoteq and cSound (nongkrong.render.sound)
            -> render_sound method

The tree-like structure of nongkrong.score.score can be sketched down as:
    Score <- Section <- ((Instrument, MDC, Dynamics), TimeFlow, Tempo, ...)
meaning a Score contains one or several Section - objects,
while a Section contains one or several ((Instrument, MDC, ...), ...) objects.
"""


class Score(object):
    INSTRUMENTS = (
        instr.SITER_GONG,
        (instr.SITER_BARUNG, instr.SITER_BARUNG_PLUS, instr.SITER_BARUNG_MINUS),
        (instr.SITER_PANERUS, instr.SITER_PANERUS_PLUS, instr.SITER_PANERUS_MINUS),
        (instr.KECAPI_PLUS_PLU, instr.KECAPI_PLUS_PLU, instr.KECAPI_PLUS_MIN),
        (instr.KECAPI_MINUS_PLU, instr.KECAPI_MINUS_PLU, instr.KECAPI_MINUS_MIN),
        instr.KENDANG,
        instr.TAK,
    )

    SIMPLIFIED_INSTRUMENTS = (
        instr.SITER_GONG,
        instr.SITER_BARUNG,
        instr.SITER_PANERUS,
        instr.KECAPI_PLUS_PLU,
        instr.KECAPI_MINUS_PLU,
        instr.KENDANG,
        instr.TAK,
    )

    TIME_LV_PER_INSTRUMENT = (2, 1, 0, 0, 0, 0, 0)
    TEMPO_LINE_STYLE = notation.HorizontalLineStyle("normalsize", "", False, False)

    def __init__(self, name: str, path: str, *section_path: str) -> None:
        sys.path.insert(0, path)
        self.__name = name
        section_data = tuple(Score.get_data_of_section(path) for path in section_path)
        info = Score.convert2valid_sections(section_data)
        self.__sections, self.__mdc_gong, self.__mdc_tong = info
        self.__document_per_instrument = self.mk_document_for_each_instrument(
            self.__sections
        )
        self.__ssd_per_instr = self.mk_soundsynthdata_for_each_instrument(
            self.__sections
        )

    @staticmethod
    def get_data_of_section(section_path) -> tuple:
        return (section_path,) + __import__(section_path).main()

    @staticmethod
    def convert2valid_sections(data_per_section) -> tuple:
        def detect_if_full_or_not(cadences_per_section: tuple) -> tuple:
            return tuple(tuple(bool(c) for c in sec) for sec in cadences_per_section)

        def return_cadence_and_instrument_for_complex(
            idx, tf, time_lv, is_sutained, cadences, instruments, is_full_or_not_per_sec
        ):
            def detect_correct_instrument_for_empty_section(
                idx, is_full_or_not_per_sec
            ):
                for is_full_or_not in is_full_or_not_per_sec[idx + 1 :]:
                    if is_full_or_not[0]:
                        return instruments[1]
                    elif is_full_or_not[1]:
                        return instruments[2]
                for is_full_or_not in reversed(is_full_or_not_per_sec[:idx]):
                    if is_full_or_not[0]:
                        return instruments[1]
                    elif is_full_or_not[1]:
                        return instruments[2]
                return instruments[0]

            if all(is_full_or_not_per_sec[idx]):
                return cadences[0], instruments[0]
            elif all(tuple(not b for b in is_full_or_not_per_sec[idx])):
                i = detect_correct_instrument_for_empty_section(
                    idx, is_full_or_not_per_sec
                )
                return old.JICadence([old.Rest(tf.size)]), i
            else:
                if cadences[0]:
                    return cadences[0], instruments[1]
                else:
                    return cadences[1], instruments[2]

        def mk_mdc_gong_and_tong(cadence, timeflow) -> tuple:
            cadence_gong, cadence_tong = [], []
            for chord in cadence:
                hg, ht = [], []
                for p in chord.pitch:
                    if p < ji.r(1, 2):
                        hg.append(p)
                    else:
                        ht.append(p)
                cadence_gong.append(old.Chord(ji.JIHarmony(hg), chord.delay))
                cadence_tong.append(old.Chord(ji.JIHarmony(ht), chord.delay))
            cadences = tuple(
                old.JICadence(c).discard_rests() for c in (cadence_gong, cadence_tong)
            )
            return tuple(
                MDC.mk_mdc_by_cadence(
                    c, timeflow, Score.TIME_LV_PER_INSTRUMENT[0], False
                )
                for c in cadences
            )

        ig1 = operator.itemgetter(1)
        ig2 = operator.itemgetter(2)
        ig3 = operator.itemgetter(3)
        ig4 = operator.itemgetter(3)
        sb_full_or_not = detect_if_full_or_not(
            tuple(ig1(ig2(data)) for data in data_per_section)
        )
        sp_full_or_not = detect_if_full_or_not(
            tuple(ig2(ig2(data)) for data in data_per_section)
        )
        kec_p_full_or_not = detect_if_full_or_not(
            tuple(ig3(ig2(data)) for data in data_per_section)
        )
        kec_m_full_or_not = detect_if_full_or_not(
            tuple(ig4(ig2(data)) for data in data_per_section)
        )

        mdc_gong_ps, mdc_tong_ps = [], []
        valid_sec_data = []
        for sec_idx, data in enumerate(data_per_section):
            tf = data[1]
            tempo = data[3]
            tempo = (tempo.convert2latex_per_unit(tf), tempo.convert2tempo_per_unit(tf))
            cadences = list(data[2])
            instruments = list(Score.INSTRUMENTS)
            cad_sb, ins_sb = return_cadence_and_instrument_for_complex(
                sec_idx,
                tf,
                Score.TIME_LV_PER_INSTRUMENT[1],
                False,
                cadences[1],
                instruments[1],
                sb_full_or_not,
            )
            cad_sp, ins_sp = return_cadence_and_instrument_for_complex(
                sec_idx,
                tf,
                Score.TIME_LV_PER_INSTRUMENT[2],
                False,
                cadences[2],
                instruments[2],
                sp_full_or_not,
            )
            cad_kec_p, ins_kec_p = return_cadence_and_instrument_for_complex(
                sec_idx,
                tf,
                Score.TIME_LV_PER_INSTRUMENT[3],
                False,
                cadences[3],
                instruments[3],
                kec_p_full_or_not,
            )
            cad_kec_m, ins_kec_m = return_cadence_and_instrument_for_complex(
                sec_idx,
                tf,
                Score.TIME_LV_PER_INSTRUMENT[4],
                False,
                cadences[4],
                instruments[4],
                kec_m_full_or_not,
            )
            cadences[1], cadences[2] = cad_sb, cad_sp
            cadences[3], cadences[4] = cad_kec_p, cad_kec_m
            instruments[1], instruments[2] = ins_sb, ins_sp
            instruments[3], instruments[4] = ins_kec_p, ins_kec_m
            mdcs = tuple(
                MDC.mk_mdc_by_cadence(cad, tf, tl, False)
                for cad, tl in zip(cadences, Score.TIME_LV_PER_INSTRUMENT)
            )
            valid_sec_data.append((data[0], mdcs, tempo, data[4], tuple(instruments)))

            mdc_gong, mdc_tong = mk_mdc_gong_and_tong(cadences[0], tf)
            mdc_gong_ps.append(mdc_gong)
            mdc_tong_ps.append(mdc_tong)

        return tuple(tuple(it) for it in (valid_sec_data, mdc_gong_ps, mdc_tong_ps))

    @property
    def name(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return "Score: {0}".format(self.name)

    @property
    def mdc_gong_per_sec(self) -> tuple:
        return self.__mdc_gong

    @property
    def mdc_tong_per_sec(self) -> tuple:
        return self.__mdc_tong

    def mk_document_for_each_instrument(self, sections) -> tuple:
        sec_per_instrument = [[] for i in Score.INSTRUMENTS]
        for idx_sec, section in enumerate(sections):
            name = section[0]
            tempo_per_unit = section[2][0]  # second element is for sound synthesis
            delay_per_unit = section[3]
            for ins_idx, ins_mdc, ins in zip(
                range(len(Score.INSTRUMENTS)), section[1], section[4]
            ):
                print("NEW ISNTR")
                print(ins.name)
                print(ins_mdc)
                print("")
                not_sec = notation.Section(
                    name,
                    ins_mdc,
                    ins,
                    tempo_per_unit,
                    self.TEMPO_LINE_STYLE,
                    delay_per_unit,
                    self.mdc_gong_per_sec[idx_sec],
                    self.mdc_tong_per_sec[idx_sec],
                )
                sec_per_instrument[ins_idx].append(not_sec)
        return tuple(
            notation.Document("{0}_{1}".format(self.name, ins.name), *se)
            for se, ins in zip(sec_per_instrument, Score.SIMPLIFIED_INSTRUMENTS)
        )

    def mk_soundsynthdata_for_each_instrument(self, data_per_section) -> tuple:
        sec_per_instrument = [[] for i in Score.INSTRUMENTS]
        for idx_sec, section in enumerate(data_per_section):
            tempo_per_unit = section[2][1]  # first element is for notation
            delay_per_unit = section[3]
            for ins_idx, ins_mdc, ins in zip(
                range(len(Score.INSTRUMENTS)), section[1], section[4]
            ):
                divided_mdcs, sound_engines = ins_mdc.divide_by_sound_engine(ins)
                cadences = tuple(
                    dimdc.convert2cadence(tempo_per_unit, delay_per_unit)
                    for dimdc in divided_mdcs
                )
                sec_per_instrument[ins_idx].append((cadences, sound_engines, ins.name))
        cadences_and_soundengines_pairs_per_instrument = []
        ig0 = operator.itemgetter(0)
        for inst in sec_per_instrument:
            div_cadences = tuple(ig0(i) for i in inst)
            sound_engines = inst[0][1]
            ins_name = inst[0][2]
            zipped = zip(*div_cadences)
            cadences = tuple(functools.reduce(operator.add, c) for c in zipped)
            assert len(cadences) == len(sound_engines)
            cadence_sound_engine_pair = tuple(zip(cadences, sound_engines))
            cadences_and_soundengines_pairs_per_instrument.append(
                (ins_name, cadence_sound_engine_pair)
            )
        return tuple(cadences_and_soundengines_pairs_per_instrument)

    def render_notation(self) -> None:
        directory = "output/notation/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        for doc in self.__document_per_instrument:
            doc.render(directory)

    @property
    def mix_data(self) -> tuple:
        return (
            (1, 0.5, 0),
            (0.7, 0.3, 0.019),
            (0.6, 0.65, 0.003),
            (0.6, 0, 0.006),
            (0.6, 0.95, 0),
            (0.65, 0.6, 0),
            (0.98, 0.4, 0),
        )

    def render_sound(self) -> None:
        directory = "output/sound/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        files = []
        for ssd in self.__ssd_per_instr:
            instr_files = []
            name = ssd[0]
            directory_local = "{0}{1}/".format(directory, name)
            if not os.path.exists(directory_local):
                os.makedirs(directory_local)
            for idx, pair in enumerate(ssd[1]):
                file_name = "{0}{1}".format(directory_local, idx)
                cadence, se = pair
                se(file_name, cadence)
                instr_files.append(file_name)
            final_file = "{0}{1}".format(directory_local, name)
            sound.mix_mono(final_file, *tuple("{0}".format(ifn) for ifn in instr_files))
            files.append(final_file)
        res = "{0}{1}".format(directory, self.name)
        input_data = tuple((n,) + mixinfo for n, mixinfo in zip(files, self.mix_data))
        sound.mix_complex(res, *input_data)


class MDC(object):
    """"Metre-divided Cadence (MDC).

    MDC describes a cadence that is hierarchically divided by the structure of a
    nongkrong.metre.TimeFlow object. This structure can be sketched down as:
        TIMEFLOW <- METRE <- COMPOUND <- UNIT <- ELEMENT
    where the highest level (TIMEFLOW) contains one or several METRE, one
    METRE contains one or several COMPOUND, etc.

    One Element is the smallest unit. Every ELEMENT represents excatly one beat.

    One Element could be:
        1. A harmony -> for instance (ji.r(1, 1), ji.r(3, 2)) or (ji.r(7, 4),)
        2. A rest (represented by an empty harmony) -> ()
        3. A deeper rhythmical division where one beat gets further divided in
            smaller Elements. This is represented with a tuple that contains
            exactly two elements -> ((...), (...)). Each of those elements can
            be (1) A harmony, (2) A rest or (3) a deeper rhythmical division.
            The internal limit of how deep a beat can be divided is 4 divisions
            / 16 Elements per beat.

    To initalise a new MDC with the mk_mdc_by_cadence - method, you need an
    mu.sco.old.Cadence objects, its respective TimeFlow and the time_level,
    with which the Cadence shall be interpreted. The class will automatically
    divide the Cadence and generate through the division a new MDC object.
    The time level argument sets what a unit of 1 delay or 1 duration in
    Cadence.delay or Cadence.duration is supposed to mean.

    For
        ...time_lv == 0 -> 1 in cadence.delay equals one element in metre.Unit
        ...time_lv == 1 -> 1 in cadence.delay equals one metre.Unit
        ...time_lv == 2 -> 1 in cadence.delay equals one metre.Compound
        ...time_lv == 3 -> 1 in cadence.delay equals one metre.Metre

    Rhythmical values smaller than 1 are only allowed with time_lv == 0. Those
    values have to have the form
                        m * [1 / (2 ** x)].
    Therefore tuplets are not possible.

    Finally there is one last additional argument when initalising a MDC with
    the mk_mdc_by_cadence - method named is_pitch_sustained.
    It's of type bool (True or False) and changes the way how the translation
    function from cadence to Metre-divided-cadence works.
    For Instruments with a continous sustain (Flute, Bowed String, ...), the
    expected input is 'True', while Instruments with a disappearing tone (Drums,
    Xylophones, Plucked Strings) are expected to get the input 'False'.

    With input 'True' every event of the transforming cadence will only be set
    at the specific metrical starting point of a Chord or Tone while every other
    point will become transformed to a Rest (mel.TheEmptyPitch). In the translation
    method "convert2cadence" those rests will be deleted for a legato Interpretation.

    With input 'False' every event will become valid for its whole duration.
    Rests will stay rests: if there is a rest between two elements those
    two elements won't be played legato but with an interruption.
    """

    def __init__(self, structure: tuple, is_pitch_sustained: bool = False):
        self.__is_pitch_sustained = is_pitch_sustained
        self.__structure = structure

    @classmethod
    def mk_mdc_by_cadence(
        cls,
        cadence: old.Cadence,
        time_flow: metre.TimeFlow,
        time_lv: int = 0,
        is_pitch_sustained: bool = False,
    ):
        cadence = cadence.copy()
        # testing if input is valid
        MDC.is_valid_time_lv(time_lv)
        MDC.is_cadence_as_long_as_timeflow(cadence, time_flow, time_lv)
        MDC.are_delay_values_of_cadence_valid(cadence, time_lv)

        # building inner structure
        structure = cls.convert_input2structure(
            cadence, time_flow, time_lv, is_pitch_sustained
        )
        return cls(structure, is_pitch_sustained)

    @staticmethod
    def is_valid_time_lv(time_lv: int) -> None:
        try:
            assert time_lv in (0, 1, 2, 3)
        except AssertionError:
            msg = "time_lv has to be 0 (element), 1 (unit),  2 (compound) or 3 (metre)."
            raise ValueError(msg)

    @staticmethod
    def is_cadence_as_long_as_timeflow(
        cadence: old.Cadence, time_flow: metre.TimeFlow, time_lv: int
    ) -> None:
        try:
            real = sum(cadence.delay)
            if time_lv == 0:
                expected = time_flow.size
            elif time_lv == 1:
                expected = time_flow.unit_amount
            elif time_lv == 2:
                expected = time_flow.compound_amount
            elif time_lv == 3:
                expected = time_flow.metre_amount
            assert real == expected
        except AssertionError:
            msg = "Cadence has to be as long as its respective TimeFLow - object."
            msg += " Cadence duration: {0}. Expected duration {1}.".format(
                real, expected
            )
            raise ValueError(msg)

    @staticmethod
    def detect_division_depth_of_rhythmical_value(value: float) -> tuple:
        depth = tuple(1 / (2 ** (i + 1)) for i in range(4))
        for i in range(16):
            i += 1
            if value / i in depth:
                return depth, i

        msg = "Rhythmical Value {0} doesn't have the form (1 / 2**x) * m ".format(value)
        msg += "or is deeper than four divisions."
        raise ValueError(msg)

    @staticmethod
    def are_delay_values_of_cadence_valid(cadence: old.Cadence, time_lv: int) -> None:
        if time_lv > 0:
            for idx, delay in enumerate(cadence.delay):
                if int(delay) != float(delay):
                    msg = "For time_lv != 0 no rhythmical values containing steps < 1 "
                    msg += "are allowed. "
                    msg += "Delay {0} has forbidden value {1}.".format(idx, delay)
                    raise ValueError(msg)
        if time_lv == 0:
            for idx, delay in enumerate(cadence.delay):
                diff = float(delay) - int(delay)
                if diff:
                    MDC.detect_division_depth_of_rhythmical_value(diff)

    @staticmethod
    def divide_cadence_by_groups(
        cadence: old.Cadence, groups: tuple, is_pitch_sustained
    ) -> tuple:
        def divide_recursively(
            remaining_cadence, remaining_groups, divided_cadences: list = []
        ) -> list:
            if remaining_cadence:
                new_cadence = type(remaining_cadence)([])
                surplus_element = None
                group_size = remaining_groups[0]
                acc = 0
                for idx, item in enumerate(remaining_cadence):
                    size = float(item.delay)
                    acc += size
                    if acc == group_size:
                        new_cadence.append(item)
                        break
                    elif acc < group_size:
                        new_cadence.append(item)
                    elif acc > group_size:
                        diff = acc - group_size
                        item0 = item.copy()
                        item0.delay -= diff
                        item0.duration -= diff
                        item1 = item.copy()
                        item1.delay = diff
                        item1.duration = diff
                        if is_pitch_sustained is False:
                            item1.pitch = ji.JIHarmony([])
                        new_cadence.append(item0)
                        surplus_element = item1
                        break
                divided_cadences.append(new_cadence)
                remaining_cadence = remaining_cadence[idx + 1 :]
                if surplus_element is not None:
                    remaining_cadence.insert(0, surplus_element)
                return divide_recursively(
                    remaining_cadence, remaining_groups[1:], divided_cadences
                )
            else:
                return divided_cadences

        return tuple(divide_recursively(cadence, groups, []))

    @staticmethod
    def divide_unit_by_elements(cadence, is_pitch_sustained) -> tuple:
        def divide_recursively(cadence, size=1):
            duration = float(cadence.duration)
            beats = duration / size
            try:
                assert float(beats) == int(beats)
            except AssertionError:
                msg = "{0} beats for size {1} in cadence {2}.".format(
                    beats, size, cadence
                )
                msg += " Attribute 'beats' has to be an integer number."
                raise ValueError(msg)
            beats = int(beats)
            group = tuple(size for i in range(beats))
            divided = MDC.divide_cadence_by_groups(cadence, group, is_pitch_sustained)
            result = []
            for div in divided:
                if len(div) == 1:
                    p = ji.JIHarmony(div[0].pitch)
                    if len(p) == 0:
                        p = mel.TheEmptyPitch
                    result.append(p)
                else:
                    result.append(divide_recursively(div, size / 2))
            if size < 1:
                assert len(result) == 2
                if result[1] == mel.TheEmptyPitch and type(result[0]) != tuple:
                    return result[0]
            return tuple(result)

        return divide_recursively(cadence)

    @staticmethod
    def convert_input2structure(
        cadence: old.Cadence,
        time_flow: metre.TimeFlow,
        time_lv: int,
        is_pitch_sustained: bool,
    ) -> tuple:
        def recursive_divider(cadence, nested_structure, time_line) -> tuple:
            if nested_structure:
                structure = nested_structure[0]
                items = getattr(time_line, structure)
                sizes = getattr(time_line, "{0}_size".format(structure))
                divided_cadences = MDC.divide_cadence_by_groups(
                    cadence, sizes, is_pitch_sustained
                )
                return tuple(
                    recursive_divider(cadence, nested_structure[1:], tl)
                    for cadence, tl in zip(divided_cadences, items)
                )
            else:
                return MDC.divide_unit_by_elements(cadence, is_pitch_sustained)

        # in case time_lv != 0, convert the cadences time values
        # (delay / duration) to the basic elementar lv
        if time_lv > 0:
            if time_lv == 3:
                size_per_item = time_flow.metre_size
            elif time_lv == 2:
                size_per_item = time_flow.compound_size
            elif time_lv == 1:
                size_per_item = time_flow.unit_size
            else:
                raise ValueError("Invalid time_lv {0}".format(time_lv))
            delays = tuple(float(d) for d in cadence.delay)
            delays_acc = tuple(
                int(item) for item in itertools.accumulate((0,) + delays)
            )
            for idx, start, end in zip(range(len(cadence)), delays_acc, delays_acc[1:]):
                cadence.delay[idx] = sum(size_per_item[start:end])
                cadence.dur[idx] = cadence.delay[idx]

        return recursive_divider(cadence, time_flow.nested_structure, time_flow)

    def convert2cadence(
        self, tempo_factors_per_unit: tuple, delays: tuple
    ) -> old.JICadence:
        """
        """

        def return_item_and_sizes(element, lv=0) -> tuple:
            if type(element) == ji.JIHarmony or element == mel.TheEmptyPitch:
                return ((element, lv),)
            else:
                ret = tuple([])
                for tup in (return_item_and_sizes(it, lv + 1) for it in element):
                    ret += tup
                return ret

        divisions_per_elements = int(tempo.TempoLine.divisions_per_element)
        cadence = []
        unit_count = 0
        for meter in self.__structure:
            for compound in meter:
                for unit in compound:

                    delay = delays[unit_count]
                    if delay:
                        if cadence:
                            cadence[-1].delay += delay.duration
                            cadence[-1].duration += delay.duration
                        else:
                            cadence.append(old.Rest(delay.duration))

                    factors = tempo_factors_per_unit[unit_count]

                    abstract_delays = []
                    harmonies = []

                    for element in unit:
                        item_and_size_pairs = return_item_and_sizes(element)
                        for pair in item_and_size_pairs:
                            harmonies.append(pair[0])
                            de = int(divisions_per_elements * (1 / (2 ** pair[1])))
                            abstract_delays.append(de)

                    real_delays = tuple(itertools.accumulate([0] + abstract_delays))
                    real_delays = tuple(
                        sum(factors[idx0:idx1])
                        for idx0, idx1 in zip(real_delays, real_delays[1:])
                    )

                    for h, de in zip(harmonies, real_delays):
                        if h:
                            cadence.append(old.Chord(h, de))
                        else:
                            cadence.append(old.Rest(de))

                    unit_count += 1

        cadence = old.JICadence(cadence).discard_rests()
        return cadence

    @property
    def is_pitch_sustained(self) -> bool:
        return self.__is_pitch_sustained

    def __repr__(self) -> str:
        return str(self.__structure)

    def __getitem__(self, idx) -> tuple:
        return tuple(self.__structure[idx])

    def __iter__(self) -> iter:
        return iter(self.__structure)

    def divide_by_decomposition(self, decomposition: dict) -> tuple:
        """Decomposition is a dict with Pitch - objects as keys and tuple as values.

        Those tuple contain integers.
        The specific Pitches will be divided to new MDC according to their
        integer value. The integer values are expected to start with 0.
        """

        def distribute_harmony(harmony) -> tuple:
            harmonies_per_mdc = [[] for i in range(amount_mdc)]
            for pitch in harmony:
                if pitch != mel.TheEmptyPitch:
                    for instridx in decomposition[pitch]:
                        harmonies_per_mdc[instridx].append(pitch)
            container = []
            for idx, harmony in enumerate(harmonies_per_mdc):
                if harmony:
                    container.append(ji.JIHarmony(harmony))
                else:
                    container.append(mel.TheEmptyPitch)
            return tuple(container)

        def divide_unit(unit, lv=0) -> tuple:
            container = [[] for i in range(amount_mdc)]
            for element in unit:
                if element == mel.TheEmptyPitch:
                    for idx in range(amount_mdc):
                        container[idx].append(mel.TheEmptyPitch)
                elif type(element) == ji.JIHarmony:
                    for idx, el in enumerate(distribute_harmony(element)):
                        container[idx].append(el)
                else:
                    for idx, el in enumerate(divide_unit(element, 1)):
                        if el[1] == mel.TheEmptyPitch:
                            el2add = el[0]
                        else:
                            el2add = el
                        container[idx].append(el2add)
            return tuple(tuple(part) for part in container)

        def divide_recursively(item, lv=0) -> tuple:
            container = [[] for i in range(amount_mdc)]
            for subitem in item:
                if lv == 2:  # already unit
                    divided = divide_unit(subitem)
                else:  # still higher level (metre or compound)
                    divided = divide_recursively(subitem, lv + 1)
                for idx, div in enumerate(divided):
                    container[idx].append(div)
            return tuple(tuple(part) for part in container)

        amount_mdc = max(functools.reduce(operator.add, decomposition.values())) + 1
        mdcs = divide_recursively(tuple(self.__structure))
        return tuple(MDC(tuple(mdc), self.is_pitch_sustained) for mdc in mdcs)

    def divide_by_notation(self, instrument) -> tuple:
        ig0 = operator.itemgetter(0)
        decomposition = {
            key: tuple(ig0(i) for i in instrument.pitch2notation[key])
            for key in instrument.pitch2notation
        }
        return self.divide_by_decomposition(decomposition)

    def divide_by_sound_engine(self, instrument) -> tuple:
        decomposition = {}
        sound_engines = instrument.sound_engines
        uniqfied_sound_engines = tuple(set(sound_engines))
        for pitch in instrument.pitch2notation:
            se_numbers = []
            for instrument_data in instrument.pitch2notation[pitch]:
                instrument_number = instrument_data[0]
                se_number = uniqfied_sound_engines.index(
                    sound_engines[instrument_number]
                )
                se_numbers.append(se_number)
            decomposition.update({pitch: tuple(se_numbers)})
        return (self.divide_by_decomposition(decomposition), uniqfied_sound_engines)

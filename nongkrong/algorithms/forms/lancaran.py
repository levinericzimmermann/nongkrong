from nongkrong.harmony import abodefunctions
from nongkrong.harmony import interfunctions
from nongkrong.harmony import functions
from nongkrong.harmony import cadence
from nongkrong.harmony import modes
from nongkrong.metre import metre
from nongkrong.harmony import subfunctions

from nongkrong.algorithms.harmony import functions as f_ag
from nongkrong.algorithms.harmony import subfunctions as sf_ag

from nongkrong.algorithms.instruments import siter_barung as siterB_ag
from nongkrong.algorithms.instruments import siter_slenthem as siterS_ag
from nongkrong.algorithms.instruments import siter_panerus as siterP_ag
from nongkrong.algorithms.instruments import kecapi as kecapi_ag
from nongkrong.algorithms.instruments import kendang as kendang_ag
from nongkrong.algorithms.instruments import tak as tak_ag

from nongkrong.algorithms.forms import lancaran_inter2polation

from mu.mel import ji
from mu.sco import old

import functools
import math
import itertools
import operator


def detect_main_and_side_prime_per_subfunction(
    mode: modes.Mode,
    func0: functions.Function,
    func1: functions.Function,
    subfuncs: tuple,
) -> tuple:
    def detect_primes_for_interfunctions(subfuncs):
        if_primes = interfunctions.InterfuncLine.get_primes(mode, func0, func1)
        res_primes = []
        for ifunc in subfuncs:
            if ifunc.signified == subfunctions.SINGLE_SIGNS[0]:
                res_primes.append((if_primes[0], if_primes[1]))
            elif ifunc.signified == subfunctions.SINGLE_SIGNS[2]:
                res_primes.append((if_primes[2], if_primes[1]))
            elif all(
                (
                    ifunc.signified == subfunctions.SINGLE_SIGNS[1],
                    ifunc.nationality == 0,
                )
            ):
                res_primes.append((if_primes[1], if_primes[0]))
            elif all(
                (
                    ifunc.signified == subfunctions.SINGLE_SIGNS[1],
                    ifunc.nationality == 1,
                )
            ):
                res_primes.append((if_primes[1], if_primes[2]))
            else:
                msg = "UNKNOWN SIGNIFIED AND NATIONALITY COMBINATION "
                msg += "FOR SIGNIFIED {0} AND NATIONALITY {1}.".format(
                    ifunc.signified, ifunc.nationality
                )
                raise NotImplementedError(msg)

        return tuple(res_primes)

    def detect_primes_for_abodefunctions(subfuncs):
        af_primes = abodefunctions.AbodefuncLine.get_primes(mode, func0, func1)
        res_primes = []
        for af in subfuncs:
            if af.signified == subfunctions.SINGLE_SIGNS[0]:
                res_primes.append((af_primes[0], af_primes[1]))
            elif af.signified == subfunctions.SINGLE_SIGNS[1]:
                res_primes.append((af_primes[1], af_primes[0]))
            else:
                msg = "UNKNOWN ABODEFUNCTION {0} WITH SIGNIFIED {1}".format(
                    af, af.signified
                )
                raise NotImplementedError(msg)
        return tuple(res_primes)

    typ = type(subfuncs[0])
    if typ == interfunctions.InterFunction:
        return detect_primes_for_interfunctions(subfuncs)
    elif typ == abodefunctions.AbodeFunction:
        return detect_primes_for_abodefunctions(subfuncs)
    else:
        msg = "Unknown subfunction type {0}!".format(typ)
        raise NotImplementedError(msg)


def detect_main_and_side_prime_per_subfunction_for_all_functions(
    mode: modes.Mode, funcs: tuple, subfunctions_per_function: tuple
) -> tuple:
    primes_per_interpolation = []
    for func0, func1, subfuncs in zip(funcs, funcs[1:], subfunctions_per_function):
        primes_per_interpolation.append(
            detect_main_and_side_prime_per_subfunction(
                mode, func0, func1, subfuncs[:-1]
            )
        )
    return tuple(primes_per_interpolation)


class Lancaran(object):
    def __init__(
        self,
        mode: modes.Mode,
        melody: cadence.Cadence,
        meter: metre.Metre,
        next_mode: modes.Mode,
        loopsize: int,
    ) -> None:

        assert melody.time

        self.__stress_generator = lancaran_inter2polation.MultiStressesMaker(10)
        self.__compounds_per_function = melody.time[:-1]
        self.__melody_functions_meaning = melody.functions
        self.__melody_functions_real = self.convert_symbolic_functions2real_functions(
            mode, next_mode, melody.functions
        )
        self.__melody_pitches = tuple(func(mode) for func in melody.functions)
        self.__mode = mode
        self.__next_mode = next_mode
        self.__meter = meter
        self.__units_per_interpolation = Lancaran.detect_units_per_interpolation(
            self.__meter, self.__compounds_per_function
        )
        self.__amount_units_per_interpolation = tuple(
            len(u) for u in self.__units_per_interpolation
        )
        sfuncs = sf_ag.interpolate_between_every_function_pair_lancar_style(
            self.__mode,
            self.__next_mode,
            self.__melody_functions_meaning,
            self.__amount_units_per_interpolation,
        )
        self.__subfunctions_per_function = sfuncs
        ppi = detect_main_and_side_prime_per_subfunction_for_all_functions(
            self.__mode, self.__melody_functions_real, self.__subfunctions_per_function
        )
        self.__primes_per_interpolation = ppi

        # make cadence per instrument
        self.__siter_slenthem = siterS_ag.mk_simple_conversion(
            self.__mode, self.__compounds_per_function, self.__melody_functions_real
        )
        self.__siter_barung = siterB_ag.mk_simple_conversion(
            self.__mode, self.__melody_functions_real, self.__subfunctions_per_function
        )
        sp, kp, km, ken = self.mk_siter_panerus_kecapi_kendang_cadences()
        self.__siter_panerus = sp
        self.__kecapi_plus = kp
        self.__kecapi_minus = km
        self.__kendang = ken
        self.__tak = tak_ag.mk_loop_cadence_with_tuk(loopsize, meter)

        """
        print(self.__siter_slenthem.pitch)
        print("")
        print(self.__siter_barung.pitch)
        print("")
        print(self.__siter_panerus.pitch)
        print("")
        print(self.__kecapi_plus.pitch)
        print("")
        print(self.__kecapi_minus.pitch)
        print("")
        print(self.__kendang.pitch)
        print("")
        print(self.__tak.pitch)
        print("")
        """

    @staticmethod
    def convert_symbolic_functions2real_functions(mode, next_mode, functions) -> tuple:
        if mode == next_mode:
            return functions
        else:
            func = functions[-1]
            new_func = f_ag.convert_function_due_to_modulation(func, mode, next_mode)
            return functions[:-1] + (new_func,)

    @staticmethod
    def detect_units_per_interpolation(
        meter: metre.Metre, compound_per_interpolation: tuple
    ) -> tuple:
        def combine_compounds(com) -> tuple:
            return functools.reduce(operator.add, (tuple(c.unit) for c in com))

        acc = tuple(itertools.accumulate((0,) + compound_per_interpolation))
        compounds = tuple(meter.compound)
        return tuple(
            combine_compounds(compounds[start:stop])
            for start, stop in zip(acc, acc[1:])
        )

    def mk_siter_panerus_kecapi_kendang_cadences(self) -> tuple:
        all_primes_per_sf = functools.reduce(
            operator.add, self.__primes_per_interpolation
        )
        siter_panerus_pitches = siterP_ag.mk_simple_conversion2pitches(
            self.__mode, self.__melody_functions_real, self.__subfunctions_per_function
        )

        assert len(all_primes_per_sf) == len(siter_panerus_pitches)

        cadences = []
        sf_counter = 0
        for func0, func1, func1_symbolic, subfuncs, units in zip(
            self.__melody_functions_real,
            self.__melody_functions_real[1:],
            self.__melody_functions_meaning[1:],
            self.__subfunctions_per_function,
            self.__units_per_interpolation,
        ):
            amount_subfunctions = len(subfuncs)
            for idx, sub in enumerate(subfuncs[:-1]):
                # detect previous, current and next primes
                current_primes = all_primes_per_sf[sf_counter]
                if sf_counter > 0:
                    previous_primes = all_primes_per_sf[sf_counter - 1]
                else:
                    previous_primes = current_primes
                if sf_counter + 1 == len(all_primes_per_sf):
                    next_primes = current_primes
                else:
                    next_primes = all_primes_per_sf[sf_counter + 1]
                current_primes = all_primes_per_sf[sf_counter]

                # make cadences for particular subfunction
                lc = self.mk_siter_panerus_kecapi_kendang_for_one_subfunction(
                    self.__mode,
                    siter_panerus_pitches[sf_counter],
                    func0,
                    func1,
                    func1_symbolic,
                    subfuncs,
                    units,
                    idx,
                    amount_subfunctions,
                    previous_primes[0],
                    previous_primes[1],
                    current_primes[0],
                    current_primes[1],
                    next_primes[0],
                    next_primes[1],
                )

                cadences.append(lc)

                sf_counter += 1

        return tuple(functools.reduce(operator.add, c) for c in zip(*cadences))

    def mk_siter_panerus_kecapi_kendang_for_one_subfunction(
        self,
        mode: modes.Mode,
        siter_panerus_pitch: ji.JIPitch,
        func0_real: functions.Function,
        func1_real: functions.Function,
        func1_symbolic: functions.Function,
        subfuncs: tuple,
        units: tuple,
        position: int,
        amount_subfunctions: int,
        previous_main_prime: int,
        previous_side_prime: int,
        current_main_prime: int,
        current_side_prime: int,
        next_main_prime: int,
        next_side_prime: int,
    ) -> tuple:

        # make kecapi improvisation (positive or negative) to avoid
        # intervals between kecapi and siter
        kecapi_impro_conditions = (
            all((current_main_prime == 3, current_side_prime == 9)),
            all((current_main_prime == 9, current_side_prime == 3)),
        )
        if any(kecapi_impro_conditions):
            raise NotImplementedError()

        # make ordinary lancaran_inter2polation - pattern that
        # work with stressed and non-stressed parts
        else:
            return self.mk_siter_panerus_kecapi_kendang_for_one_subfunction_standard(
                siter_panerus_pitch,
                mode,
                func0_real,
                func1_real,
                func1_symbolic,
                subfuncs,
                units,
                position,
                amount_subfunctions,
                previous_main_prime,
                previous_side_prime,
                current_main_prime,
                current_side_prime,
                next_main_prime,
                next_side_prime,
            )

    def mk_siter_panerus_kecapi_kendang_for_one_subfunction_standard(
        self,
        siter_panerus_pitch: ji.JIPitch,
        mode: modes.Mode,
        func0: functions.Function,
        func1: functions.Function,
        func1_symbolic: functions.Function,
        subfuncs: tuple,
        units: tuple,
        position: int,
        amount_subfunctions: int,
        previous_main_prime: int,
        previous_side_prime: int,
        current_main_prime: int,
        current_side_prime: int,
        next_main_prime: int,
        next_side_prime: int,
    ) -> tuple:
        sf0, sf1 = subfuncs[position], subfuncs[position + 1]
        unitsize = units[position].size

        stresses_generator = self.__stress_generator
        siter_style = siterP_ag.StaticSiterStyle(True, True, True)
        # kecapi_plus_style = kecapi_ag.Plus_StaticLancaranStyle_Simple()
        # kecapi_minus_style = kecapi_ag.Minus_StaticLancaranStyle_Simple()
        kecapi_plus_style = kecapi_ag.Plus_StaticLancaranStyle_Full_WithHeader()
        kecapi_minus_style = kecapi_ag.Minus_StaticLancaranStyle_Full_WithHeader()
        kendang_style = kendang_ag.StaticLancaranStyle_OnlyStable()

        if type(sf0.signifier) == subfunctions.InterpolationSign:
            siter_style = siterP_ag.StaticSiterStyle(True, False, True)
            kendang_style = kendang_ag.StaticLancaranStyle_OnlyStable()
            kecapi_plus_style = kecapi_ag.Plus_StaticLancaranStyle_Full_WithoutHeader()
            kecapi_minus_style = (
                kecapi_ag.Minus_StaticLancaranStyle_Full_WithoutHeader()
            )

        if type(sf0.signifier) == subfunctions.SingleSign:
            siter_style = siterP_ag.StaticSiterStyle(True, False, False)

        if sf0.signified != sf1.signified:
            siter_style = siterP_ag.StaticSiterStyle(True, True, True)

        # make circle style
        circle_conditions = (
            current_main_prime == previous_main_prime,
            current_main_prime == next_main_prime,
            unitsize in kecapi_ag.Plus_CircleLancaranStyle().available_pattern_sizes,
            position + 2 != amount_subfunctions,
        )
        if all(circle_conditions):
            siter_style = siterP_ag.CircleSiterStyle()
            kecapi_plus_style = kecapi_ag.Plus_CircleLancaranStyle()
            kecapi_minus_style = kecapi_ag.Minus_CircleLancaranStyle()
            kendang_style = kendang_ag.SilentLancaranStyle()

        # make alternating style
        if position > 0:
            sf_before = subfuncs[position - 1]
            conditions_for_alternating_style = (
                type(sf0.signifier) == subfunctions.InterpolationSign,
                sf1.signified == sf0.signified,
                sf0.signified != sf_before.signified,
            )
            if all(conditions_for_alternating_style):
                if sf0.signifier.is_close:
                    siter_style = siterP_ag.AlternatingSiterStyle(True, True, False)
                    kecapi_plus_style = kecapi_ag.Plus_AlternatingLancaranStyle_Simple()
                    kecapi_minus_style = (
                        kecapi_ag.Minus_AlternatingLancaranStyle_Simple()
                    )
                    kendang_style = kendang_ag.AlternatingLancaranStyle_Stable()

        # make moveless style
        if sf0 == sf1:
            unit = units[position]
            log = math.log(unit.size, 2)
            if int(log) == log:
                siter_style = siterP_ag.EmptySiterStyle(True, True, False)
                kecapi_plus_style = kecapi_ag.Plus_MovelessLancaranStyle_Simple()
                kecapi_minus_style = kecapi_ag.SilentLancaranStyle()
                kendang_style = kendang_ag.MovelessLancaranStyle()
            elif unit.size % 7 == 0:
                siter_style = siterP_ag.StaticSiterStyle(True, True, False)
                kecapi_plus_style = kecapi_ag.Plus_LoopLancaranStyle7()
                kecapi_minus_style = kecapi_ag.Minus_LoopLancaranStyle7()
                kendang_style = kendang_ag.SilentLancaranStyle()
            elif unit.size % 6 == 0:
                siter_style = siterP_ag.StaticSiterStyle(True, True, False)
                kendang_style = kendang_ag.SilentLancaranStyle()
                kecapi_plus_style = kecapi_ag.Plus_LoopLancaranStyle6()
                kecapi_minus_style = kecapi_ag.Minus_LoopLancaranStyle6()
            elif unit.size % 5 == 0:
                siter_style = siterP_ag.StaticSiterStyle(True, True, False)
                kecapi_plus_style = kecapi_ag.Plus_LoopLancaranStyle5()
                kecapi_minus_style = kecapi_ag.Minus_LoopLancaranStyle5()
                kendang_style = kendang_ag.SilentLancaranStyle()
            elif unit.size % 3 == 0:
                siter_style = siterP_ag.StaticSiterStyle(True, True, False)
                kecapi_plus_style = kecapi_ag.Plus_LoopLancaranStyle3()
                kecapi_minus_style = kecapi_ag.Minus_LoopLancaranStyle3()
                kendang_style = kendang_ag.SilentLancaranStyle()
            else:
                siter_style = siterP_ag.EmptySiterStyle(True, True, False)
                kecapi_plus_style = kecapi_ag.SilentLancaranStyle()
                kecapi_minus_style = kecapi_ag.SilentLancaranStyle()
                kendang_style = kendang_ag.MovelessLancaranStyle()

        # make from-gong special gatra
        if func0.gong and position == 0:
            siter_style = siterP_ag.StaticSiterStyle(True, True, False)
            kecapi_plus_style = kecapi_ag.Plus_FromGongLancaranStyle()
            kecapi_minus_style = kecapi_ag.Minus_FromGongLancaranStyle()
            kendang_style = kendang_ag.SilentLancaranStyle()

        # make to-gong special gatra
        # also valide for m tong
        to_gong_conditions = (
            func1_symbolic in (functions.FUNCTIONS["m"], functions.FUNCTIONS["M"]),
            position + 2 == amount_subfunctions,
        )
        if all(to_gong_conditions):
            siter_style = siterP_ag.ToGongSiterStyle()
            kecapi_plus_style = kecapi_ag.Plus_ToGongLancaranStyle()
            kecapi_minus_style = kecapi_ag.Minus_ToGongLancaranStyle()
            kendang_style = kendang_ag.SilentLancaranStyle()

        lancaran_style = lancaran_inter2polation.LancaranStyle(
            stresses_generator,
            siter_style,
            kecapi_plus_style,
            kecapi_minus_style,
            kendang_style,
        )

        return lancaran_style.convert2cadences(
            unitsize,
            siter_panerus_pitch,
            mode.gender,
            previous_main_prime,
            previous_side_prime,
            current_main_prime,
            current_side_prime,
            next_main_prime,
            next_side_prime,
        )

    @property
    def siter_slenthem(self) -> old.JICadence:
        return self.__siter_slenthem

    @staticmethod
    def return_gender_dependent_instrument(cadence, mode) -> tuple:
        if mode.gender:
            return (cadence, old.JICadence([]))
        else:
            return (old.JICadence([]), cadence)

    @property
    def siter_barung(self) -> tuple:
        return self.return_gender_dependent_instrument(self.__siter_barung, self.__mode)

    @property
    def siter_panerus(self) -> tuple:
        return self.return_gender_dependent_instrument(
            self.__siter_panerus, self.__mode
        )

    @property
    def kecapi_plus(self) -> tuple:
        return self.return_gender_dependent_instrument(self.__kecapi_plus, self.__mode)

    @property
    def kecapi_minus(self) -> tuple:
        return self.return_gender_dependent_instrument(self.__kecapi_minus, self.__mode)

    @property
    def kendang(self) -> old.JICadence:
        return self.__kendang

    @property
    def tak(self) -> old.JICadence:
        return self.__tak

    def convert2cadences(self) -> tuple:
        return (
            self.siter_slenthem,
            self.siter_barung,
            self.siter_panerus,
            self.kecapi_plus,
            self.kecapi_minus,
            self.kendang,
            self.tak,
        )

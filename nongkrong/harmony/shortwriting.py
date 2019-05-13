import functools
import operator

from mu.mel import ji


def translate2pitch(info: str, standard=1, idx=None) -> ji.JIPitch:
    def change2pitch(current_num, current_exp):
        if current_num:
            number = int(current_num)
        else:
            msg = "NUMBER FORGOTTEN IN ELEMENT {0}".format(info)
            if idx:
                msg += " ({0} element)".format(idx)
            raise ValueError(msg)
        if current_exp:
            exp = sum(current_exp)
        else:
            exp = standard
        if exp > 0:
            ret = True
        else:
            ret = False
        return number ** abs(exp), ret

    splited_by_octave_remarks = info.split(".")
    octave = ji.r(1, 1)
    before = True
    pitch = None
    for item in splited_by_octave_remarks:
        if item:
            if pitch:
                msg = "UNEXPECTED FORM: '.' in between {0}".format(info)
                raise ValueError(msg)
            else:
                pitch = item
            before = False
        else:
            if before:
                octave += ji.r(1, 2)
            else:
                octave += ji.r(2, 1)
    numbers = tuple(str(i) for i in range(10))
    positive, negative = [[1], [1]]
    is_seperating = False
    current_num = ""
    current_exp = []
    for element in pitch:
        if element in numbers:
            if is_seperating:
                fac, pos = change2pitch(current_num, current_exp)
                if pos:
                    positive.append(fac)
                else:
                    negative.append(fac)
                current_num = element
                current_exp = []
                is_seperating = False
            else:
                current_num += element
        elif element == "+":
            is_seperating = True
            current_exp.append(1)
        elif element == "-":
            is_seperating = True
            current_exp.append(-1)
        else:
            msg = "UNKNOWN SIGN {0} IN {1}".format(element, info)
            if idx:
                msg += " ({0} element)".format(idx)
            raise ValueError(msg)

    fac, pos = change2pitch(current_num, current_exp)
    if pos:
        positive.append(fac)
    else:
        negative.append(fac)

    pitch = ji.r(
        *tuple(functools.reduce(operator.mul, n) for n in (positive, negative))
    )
    return pitch.normalize(2) + octave


def translate(information: str) -> tuple:
    divided = tuple(info for info in information.split(" ") if info)
    pitches = []
    standard = 1
    for idx, info in enumerate(divided):
        if info[0] == "!":
            if info[1] == "+":
                standard = 1
            elif info[1] == "-":
                standard = -1
            else:
                msg = "UNKNOWN SYMBOL {0} IN COMMAND {1} ({2}).".format(
                    info[1], info, idx
                )
                raise ValueError(msg)
        else:
            pitches.append(translate2pitch(info, standard, idx))
    return tuple(pitches)


def translate_from_file(path: str) -> tuple:
    with open(path, "r") as content:
        content = " ".join(content.read().splitlines())
        return translate(content)

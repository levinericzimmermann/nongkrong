import operator
import itertools
import pylatex


from mu.mel import mel


class Sign(object):
    def __init__(self, cmd: str, is_mathematical_symbol=False):
        self.__cmd = cmd
        self.__is_mathematical_symbol = is_mathematical_symbol

    def __repr__(self) -> str:
        return "S:{0}".format(self.__cmd)

    @property
    def is_mathematical_symbol(self) -> bool:
        return self.__is_mathematical_symbol

    def __str__(self) -> str:
        if self.is_mathematical_symbol:
            return r"${0}$".format(self.__cmd)
        else:
            return self.__cmd


SIGN_REST = Sign(r"\circ", True)
SIGN_NUMBERS = tuple(Sign(str(n + 1)) for n in range(20))


class SignAttractor(object):
    def __init__(self, cmd: str):
        self.__cmd = cmd

    def __repr__(self) -> str:
        return "ATT{0}".format(self.cmd)

    @property
    def cmd(self) -> str:
        return self.__cmd

    def wrap_signs(self, signs: tuple) -> str:
        wrapped = " ".join(tuple(str(sign) for sign in signs))
        return self.cmd + "{" + wrapped + "}"


SA_OVERLINE = SignAttractor(r"\textoverline")
SA_CIRCLED = SignAttractor(r"\circled")
SA_DOUBLE_CIRCLED = SignAttractor(r"\circledcircled")


class PitchNotationUnit(object):
    def __init__(self, content: tuple, wraps: tuple):
        self.__content = content
        self.__wraps = wraps

    @property
    def content(self) -> tuple:
        return self.__content

    @property
    def wraps(self) -> tuple:
        return self.__wraps

    def __str__(self) -> str:
        content = self.content
        for wrap in self.wraps:
            content = (wrap.wrap_signs(content),)
        return content[0]

    def __repr__(self) -> str:
        return "PNU {0}".format(repr(tuple(repr(item) for item in self.content)))


class HorizontalLineStyle(object):
    def __init__(
        self,
        size: str,
        label: str,
        add2table_if_empty: bool,
        mark_metrical_division: bool,
    ):
        available_sizes = ("Large", "large", "normalsize")
        assert size in available_sizes
        self.__size = size
        self.__mark_metrical_division = mark_metrical_division
        self.__label = label
        self.__add2table_if_empty = add2table_if_empty

    @property
    def size(self) -> str:
        return self.__size

    @property
    def label(self) -> str:
        return self.__label

    @property
    def add2table_if_empty(self) -> bool:
        return self.__add2table_if_empty

    @property
    def mark_metrical_division(self) -> bool:
        return self.__mark_metrical_division


class MelodicLineStyle(HorizontalLineStyle):
    def __init__(
        self,
        size,
        label: str,
        add2table_if_empty: bool,
        write_empty_unit: bool,
        mark_gong: bool,
    ):
        HorizontalLineStyle.__init__(self, size, label, add2table_if_empty, True)
        self.__mark_gong = mark_gong
        self.__write_empty_unit = write_empty_unit
        self.__label = label

    @property
    def mark_gong(self) -> bool:
        return self.__mark_gong

    @property
    def write_empty_unit(self) -> bool:
        return self.__write_empty_unit


class MultiColumn(object):
    def __init__(self, content: str, column_size: int):
        self.__content = content
        self.__column_size = column_size

    @property
    def content(self) -> str:
        return self.__content

    @property
    def column_size(self) -> int:
        return self.__column_size

    def convert2str(self, size, vl_before=None, vl_after=None, additional=None) -> str:
        content = r"\multicolumn{" + str(self.column_size) + r"}{"
        if vl_before:
            content += str(vl_before) + " "
        content += r"l"
        if vl_after:
            content += str(vl_after)
        content += r"}{"
        if additional:
            for add in additional:
                content += "{0} ".format(add)
        content += "{0} {1}".format(size, self.content)
        content += r"}"
        return content


class HorizontalLine(object):
    def __init__(
        self,
        content_per_unit: tuple,
        vertical_lines: tuple,
        horizontal_line_style: HorizontalLineStyle,
        has_label: True,
    ):
        self.__content = content_per_unit
        self.__vertical_lines = vertical_lines
        self.__horizontal_line_style = horizontal_line_style
        self.__has_label = has_label

    @property
    def content(self):
        return self.__content

    @property
    def has_label(self):
        return self.__has_label

    @property
    def vertical_lines(self):
        return self.__vertical_lines

    @property
    def horizontal_line_style(self):
        return self.__horizontal_line_style

    def __str__(self) -> str:
        def add_vl_before(data, vl):
            return r"\multicolumn{1}{" + str(vl) + "l}{" + data + "}"

        def add_vl_after(data, vl):
            return r"\multicolumn{1}{l" + str(vl) + "}{" + data + "}"

        def add_distance(data, distance):
            return "{0} {1}".format(distance, data)

        res = []
        size = r"\{0}".format(self.horizontal_line_style.size)
        distance = r"\distance" + self.horizontal_line_style.size
        if self.has_label:
            res.append(r"{0} {1}".format(size, self.horizontal_line_style.label))
        for idx, unit in enumerate(self.content):
            if type(unit) == MultiColumn:
                if self.horizontal_line_style.mark_metrical_division:
                    vl_before = self.vertical_lines[idx]
                    if idx + 1 == len(self.content):
                        vl_after = self.vertical_lines[idx]
                    else:
                        vl_after = None
                else:
                    vl_before = None
                    vl_after = None
                if idx == 0:
                    additional = (distance,)
                else:
                    additional = None
                res.append(unit.convert2str(size, vl_before, vl_after, additional))
            else:
                unit = list(r"{0} {1}".format(size, item) for item in unit)
                if idx == 0:
                    unit[0] = add_distance(unit[0], distance)
                if self.horizontal_line_style.mark_metrical_division:
                    if self.horizontal_line_style.mark_metrical_division:
                        unit[0] = add_vl_before(unit[0], self.vertical_lines[idx])
                    if idx + 1 == len(self.content):
                        if self.horizontal_line_style.mark_metrical_division:
                            unit[-1] = add_vl_after(unit[-1], self.vertical_lines[-1])
                res.extend(unit)
        return r" & ".join(res) + r" \\"


class VerticalLine(object):
    def __init__(self, thickness: float, color: str, amount: int):
        self.thickness = thickness
        self.color = color
        self.amount = amount

    def __str__(self) -> str:
        basic = r"!{"
        middle = r"\vline width "
        end = r"pt}"
        if self.color:
            basic += r"\color{" + self.color + r"} "
        res = basic + middle + str(self.thickness) + end
        if self.amount > 1:
            res = " ".join(tuple(res for i in range(self.amount)))
        return res


class VerticalLineStyle(object):
    def __init__(self, metre: VerticalLine, compound: VerticalLine, unit: VerticalLine):
        self.metre = metre
        self.compound = compound
        self.unit = unit


class Table(object):
    def __init__(self, melodic_lines, tempo_line, amount_elements, has_label: bool):
        self.melodic_lines = melodic_lines
        self.tempo_line = tempo_line
        self.amount_elements = amount_elements
        self.has_label = has_label

    def add2document(self, document) -> None:
        def add_hline(document):
            if self.has_label:
                cmd = r"\cline{" + "2-{0}".format(self.amount_elements + 1) + "}"
                document.append(pylatex.NoEscape(cmd))
            else:
                document.append(pylatex.Command("hline"))

        amount_columns = int(self.amount_elements) - 1
        if self.has_label:
            amount_columns += 1

        columns = r" ".join((r"l",) * amount_columns)
        table_start = r"\begin{tabular*}{\textwidth} {l @{\extracolsep{\fill}} "
        table_start += columns + r"}"
        document.append(pylatex.NoEscape(table_start))

        if self.tempo_line:
            document.append(pylatex.NoEscape(str(self.tempo_line)))

        for melodic_line in self.melodic_lines:
            add_hline(document)
            document.append(pylatex.NoEscape(str(melodic_line)))

        add_hline(document)

        document.append(pylatex.NoEscape(r"\end{tabular*}"))


class Section(object):
    MAX_SIGNS_PER_TABLE = 25
    VERTICAL_SPACE_BETWEEN_TABLE = 8

    def __init__(
        self,
        name: str,
        mdc,
        instrument,
        tempo_per_unit: tuple,
        tempo_line_style: HorizontalLineStyle,
        delays: tuple,
        mdc_gong,
        mdc_tong,
    ):

        self.__name = name
        mdc_per_instrument = mdc.divide_by_notation(instrument)

        # make vertical line for every unit
        vertical_lines = Section.mk_vertical_lines(mdc, delays, instrument)

        gong = Section.mk_is_gong(mdc_gong)
        tong = Section.mk_is_gong(mdc_tong)

        # make content per unit per mdc
        content_per_unit_per_instrument = tuple(
            Section.mk_content_per_unit(mdc_local, instrument, mstyle, gong, tong)
            for mdc_local, mstyle in zip(
                mdc_per_instrument, instrument.horizontal_line_styles
            )
        )

        self.__tables = Section.mk_tables(
            content_per_unit_per_instrument,
            vertical_lines,
            tempo_per_unit,
            instrument,
            tempo_line_style,
        )

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tables(self) -> tuple:
        return self.__tables

    @staticmethod
    def mk_vertical_lines(mdc, delays, instrument) -> tuple:
        vertical_lines = []
        unit_idx = 0
        for metre in mdc:
            for local_compound_idx, compound in enumerate(metre):
                for local_unit_idx, unit in enumerate(compound):
                    if local_unit_idx == 0:
                        if local_compound_idx == 0:
                            vertical_line = instrument.vertical_line_style.metre
                        else:
                            vertical_line = instrument.vertical_line_style.compound
                    else:
                        vertical_line = instrument.vertical_line_style.unit
                    delay = delays[unit_idx]
                    if delay:
                        vertical_line = delay.adapt_vertical_line(vertical_line)
                    vertical_lines.append(vertical_line)
                    unit_idx += 1

        vertical_lines.append(instrument.vertical_line_style.metre)
        return tuple(vertical_lines)

    @staticmethod
    def mk_is_gong(mdc) -> tuple:
        def detect(element) -> bool:
            if type(element) == tuple:
                return detect(element[0])
            elif element == mel.TheEmptyPitch:
                return False
            else:
                return True

        res = []
        for metre in mdc:
            m = []
            for compound in metre:
                c = [detect(unit[0]) for unit in compound]
                m.append(tuple(c))
            res.append(tuple(m))
        return tuple(res)

    @staticmethod
    def mk_content_per_unit(mdc, instrument, melodic_line_style, gong, tong) -> tuple:
        def transform2content(element, is_gong: bool, is_tong: bool) -> str:
            if type(element) == tuple:
                content = []
                amount_signs = 0
                for seidx, se in enumerate(element):
                    if seidx == 0:
                        trans, scounter = transform2content(se, is_gong, is_tong)
                    else:
                        trans, scounter = transform2content(se, False, False)
                    content.append(trans)
                    amount_signs += scounter
                return PitchNotationUnit(tuple(content), (SA_OVERLINE,)), amount_signs
            else:
                if element == mel.TheEmptyPitch:
                    sign = SIGN_REST
                    amount_signs = 1
                else:
                    amount_signs = len(element)
                    signs = tuple(
                        str(instrument.pitch2notation[pitch][0][1]) for pitch in element
                    )
                    if amount_signs == 1:
                        sign = signs[0]
                    elif amount_signs == 2:
                        sign = r"\mkinterval{" + signs[1] + "}{" + signs[0] + "}"
                    else:
                        raise ValueError(
                            "NO SOLUTION FOR MORE THAN TWO PITCHES FOUND YET"
                        )
                if is_gong:
                    res = PitchNotationUnit((sign,), (SA_CIRCLED, SA_DOUBLE_CIRCLED))
                elif is_tong:
                    res = PitchNotationUnit((sign,), (SA_CIRCLED,))
                else:
                    res = sign
                return res, amount_signs

        units = []
        for midx, metre in enumerate(mdc):
            for cidx, compound in enumerate(metre):
                for uidx, unit in enumerate(compound):
                    content = []
                    amount_signs = 0
                    for eidx, element in enumerate(unit):
                        if eidx == 0 and melodic_line_style.mark_gong is True:
                            is_gong = gong[midx][cidx][uidx]
                            is_tong = tong[midx][cidx][uidx]
                        else:
                            is_gong = False
                            is_tong = False
                        transformation, scounter = transform2content(
                            element, is_gong, is_tong
                        )
                        content.append(transformation)
                        amount_signs += scounter
                    has_content = True
                    if all(tuple(e == mel.TheEmptyPitch for e in unit)):
                        has_content = False
                        if melodic_line_style.write_empty_unit is False:
                            content = ("",) * len(unit)
                    units.append((tuple(content), amount_signs, has_content))
        return tuple(units)

    @staticmethod
    def mk_tables(
        content_per_unit_per_instrument,
        vertical_lines,
        tempo_per_unit,
        instrument,
        tempo_line_style,
    ) -> tuple:
        def detect_next_cut(amount_elements_per_unit):
            a = 0
            for counter, ae in enumerate(amount_elements_per_unit):
                assert ae <= Section.MAX_SIGNS_PER_TABLE
                a += ae
                if a > Section.MAX_SIGNS_PER_TABLE:
                    return counter
            return len(amount_elements_per_unit)

        def detect_amount_units_per_table(content_per_unit_per_instrument):
            amount_elements_per_unit_per_instrument = tuple(
                tuple(content[1] for content in instr)
                for instr in content_per_unit_per_instrument
            )
            amount_units = []
            while any(amount_elements_per_unit_per_instrument):
                next_cut_per_instr = tuple(
                    detect_next_cut(instr)
                    for instr in amount_elements_per_unit_per_instrument
                )
                next_cut = min(next_cut_per_instr)
                amount_units.append(next_cut)
                amount_elements_per_unit_per_instrument = tuple(
                    instr[next_cut:]
                    for instr in amount_elements_per_unit_per_instrument
                )
            return tuple(amount_units)

        def am_I_addable(has_content: bool, add_if_empty: bool) -> bool:
            if not add_if_empty:
                if not has_content:
                    return False
            return True

        def find_empty_line_if_no_melodic_line_fits(
            instrument_data,
            instrument_addable_per_table,
            idx,
            vl,
            instrument,
            has_label,
        ):
            def find_instr_idx(idx, instrument_addable_per_table):
                for addable_per_instr in instrument_addable_per_table[idx + 1 :]:
                    for instr_idx, is_addable in enumerate(addable_per_instr):
                        if is_addable:
                            return instr_idx
                for addable_per_instr in reversed(instrument_addable_per_table[:idx]):
                    for instr_idx, is_addable in enumerate(addable_per_instr):
                        if is_addable:
                            return instr_idx
                return 0

            def mk_melodic_lines(instr_idx, instrument_data, vl, instrument, has_label):
                return (
                    HorizontalLine(
                        instrument_data[instr_idx][0],
                        vl,
                        instrument.horizontal_line_styles[instr_idx],
                        has_label,
                    ),
                )

            instr_idx = find_instr_idx(idx, instrument_addable_per_table)
            return mk_melodic_lines(
                instr_idx, instrument_data, vl, instrument, has_label
            )

        amount_units_per_table = detect_amount_units_per_table(
            content_per_unit_per_instrument
        )
        unit_indices_per_table = tuple(
            itertools.accumulate((0,) + amount_units_per_table)
        )
        instrument_addable_per_table = []
        instr_data_per_table = []
        vl_per_table = []
        tempo_per_table = []
        for startidx, stopidx in zip(
            unit_indices_per_table, unit_indices_per_table[1:]
        ):
            instrument_data = tuple(
                content_per_unit[startidx:stopidx]
                for content_per_unit in content_per_unit_per_instrument
            )
            vl = vertical_lines[startidx : stopidx + 1]

            addable_or_not = tuple(
                any(am_I_addable(d[2], style.add2table_if_empty) for d in data)
                for data, style in zip(
                    instrument_data, instrument.horizontal_line_styles
                )
            )
            instrument_addable_per_table.append(addable_or_not)

            instr_data_per_table.append(instrument_data)
            vl_per_table.append(vl)
            tempo_per_table.append(tempo_per_unit[startidx:stopidx])

        tables = []
        has_label = any(
            tuple(style.label for style in instrument.horizontal_line_styles)
        )
        for idx, instrument_data, vl, tempo_data, is_addable_per_instr in zip(
            range(len(vl_per_table)),
            instr_data_per_table,
            vl_per_table,
            tempo_per_table,
            instrument_addable_per_table,
        ):
            ig0 = operator.itemgetter(0)
            melodic_lines = tuple(
                HorizontalLine(tuple(ig0(d) for d in data), vl, style, has_label)
                for data, style, is_addable in zip(
                    instrument_data,
                    instrument.horizontal_line_styles,
                    is_addable_per_instr,
                )
                if is_addable
            )
            if not melodic_lines:
                melodic_lines = find_empty_line_if_no_melodic_line_fits(
                    instrument_data,
                    instrument_addable_per_table,
                    idx,
                    vl,
                    instrument,
                    has_label,
                )

            if any(tuple(inf[2] for inf in tempo_data)):
                tempo_line = HorizontalLine(
                    tuple(ig0(inf) for inf in tempo_data),
                    vl,
                    tempo_line_style,
                    has_label,
                )
            else:
                tempo_line = None

            amount_elements = sum(len(ig0(d)) for d in instrument_data[0])
            tables.append(Table(melodic_lines, tempo_line, amount_elements, has_label))
        return tuple(tables)

    def add2document(self, doc) -> None:
        with doc.create(pylatex.Section(self.name)):
            for table in self.tables:
                table.add2document(doc)
                doc.append(pylatex.NoEscape(""))
                doc.append(pylatex.Command("newline"))
                doc.append(pylatex.NoEscape(""))
                doc.append(
                    pylatex.Command(
                        "vspace",
                        arguments="{0}mm".format(self.VERTICAL_SPACE_BETWEEN_TABLE),
                    )
                )
                doc.append(pylatex.NoEscape(""))
                doc.append(pylatex.Command("newline"))
                doc.append(pylatex.NoEscape(""))


class Document(object):
    def __init__(self, name: str, *section):
        self.name = name
        self.__sections = section

    @property
    def sections(self) -> tuple:
        return self.__sections

    @staticmethod
    def mk_basic_doc() -> pylatex.Document:
        doc = pylatex.Document()
        # doc.preamble.append(pylatex.NoEscape(r"\documentclass[a4paper]{article}"))
        # doc.preamble.append(
        #     pylatex.Command("usepackage", options="T1", arguments="fontenc")
        # )
        # doc.preamble.append(
        #     pylatex.Command("usepackage", options="utf8", arguments="inputenc")
        # )
        doc.preamble.append(pylatex.Command("usepackage", arguments="array"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="xcolor"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="tabu"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="tabularx"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="tikz"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="makecell"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="fancyhdr"))
        doc.preamble.append(pylatex.Command("usepackage", arguments="arydshln"))
        doc.preamble.append(
            pylatex.NoEscape(r"\newcommand\distanceLarge{\rule[-4.1mm]{0cm}{11mm}}")
        )
        doc.preamble.append(
            pylatex.NoEscape(r"\newcommand\distancelarge{\rule[-3.3mm]{0cm}{9.8mm}}")
        )
        doc.preamble.append(
            pylatex.NoEscape(r"\newcommand\distancenormalsize{\rule[-2.3mm]{0cm}{8mm}}")
        )
        doc.preamble.append(
            pylatex.NoEscape(r"\newcommand*\circled[1]{\tikz[baseline=(char.base)]{")
        )
        doc.preamble.append(
            pylatex.NoEscape(r"\node[shape=circle,draw,inner sep=1.2pt] (char) {#1};}}")
        )
        doc.preamble.append(
            pylatex.NoEscape(
                r"\newcommand*\circledcircled[1]{\tikz[baseline=(char.base)]{"
            )
        )
        doc.preamble.append(
            pylatex.NoEscape(r"\node[shape=circle,draw,inner sep=-1pt] (char) {#1};}}")
        )
        doc.preamble.append(pylatex.NoEscape(r"\makeatletter"))
        doc.preamble.append(
            pylatex.NoEscape(
                r"\newcommand*{\textoverline}[1]{$\overline{\hbox{#1}}\m@th$}"
            )
        )
        doc.preamble.append(pylatex.NoEscape(r"\makeatother"))
        doc.preamble.append(pylatex.NoEscape(r"\makeatletter"))
        doc.preamble.append(
            pylatex.NoEscape(r"\newcommand*{\mkinterval}[2]{$#1 \atop #2 \m@th$}")
        )
        doc.preamble.append(pylatex.NoEscape(r"\makeatother"))
        doc.preamble.append(pylatex.NoEscape(r"\newcolumntype{C}[1]{"))
        doc.preamble.append(
            pylatex.NoEscape(
                r">{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}"
            )
        )
        doc.preamble.append(pylatex.NoEscape(r"\setlength\parindent{0pt}"))
        doc.preamble.append(
            pylatex.NoEscape(r"\usepackage[a4paper,bindingoffset=0.2in,%")
        )
        doc.preamble.append(
            pylatex.NoEscape(r"left=0.5cm,right=1cm,top=1.5cm,bottom=1cm,%")
        )
        doc.preamble.append(pylatex.NoEscape(r"footskip=.25in]{geometry}"))
        doc.preamble.append(
            pylatex.NoEscape(r"\fancyhf{} % clear all header and footers")
        )
        doc.preamble.append(
            pylatex.NoEscape(
                r"\renewcommand{\headrulewidth}{0pt} % remove the header rule"
            )
        )
        doc.preamble.append(pylatex.NoEscape(r"\fancyhead[R]{\thepage}"))
        doc.preamble.append(pylatex.NoEscape(r"\setlength{\headsep}{0.25cm}"))
        doc.preamble.append(pylatex.NoEscape(r"\pagestyle{fancy}"))
        return doc

    def render(self, path: str) -> None:
        document = self.mk_basic_doc()
        for section in self.sections:
            section.add2document(document)
        document.generate_pdf(path + self.name, clean_tex=False)

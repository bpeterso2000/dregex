import math
from pprint import pformat

import colorama
from colorama import Fore, Style

import highlight
from highlight import Color, add_color, get_color

colorama.init()

# max num search string chars to display while debugging
DBUG_WINDOW_SIZE = 76
GROUP_ATTRS = ['group', 'start', 'end', 'span']
HORIZ_LINE = add_color('-' * 76, fg='yellow') + '\n'


class OpTracker:
    """Friendly debug reports."""

    def __init__(self):
        self.op_count = 0
        self.last_str_pos = None
        self.last_marks = []


def show_match(match):
    if match:
        result = HORIZ_LINE + add_color('Found Match.\n', bold=True)
        if not match.groups():
            hi = [Color(
                match.start(),
                match.end(),
                get_color('RED', bold=True)
            )]
            result += (
                HORIZ_LINE +
                highlight.apply_styles(match.string, hi) +
                '\n'
            )
    else:
        result = (
            HORIZ_LINE +
            add_color('Match Not Found!', fg='red', bold=True)
        )
        return result
    if match.groupdict():
        # regex uses group names
        result += '{hline}\nmatch.groupdict(): {value}'.format(
            hline=HORIZ_LINE,
            value=pformat(match.groupdict)
        )
    if match.groups():
        # regex uses groups
        result += HORIZ_LINE + 'match.groups(): {}\nmatch.regs: {}\n'.format(
            add_color(match.groups(), fg='green', bold=True),
            add_color(match.regs, fg='green', bold=True)
        )
        for group_num, group in enumerate(match.groups(), start=1):
            result += ''.join([
                'match.{match_attr}({match_num}): {value}\n'.format(
                    match_attr=add_color(i, fg='green', bold=True),
                    match_num=add_color(group_num, fg='yellow', bold=True),
                    value=add_color(
                        getattr(match, i)(group_num), fg='white', bold='True'
                    )
                ) for i in GROUP_ATTRS
            ])
            result += HORIZ_LINE + highlight.apply_styles(
                match.string, [Color(
                    match.start(group_num),
                    match.end(group_num),
                    get_color('magenta', bold=True)
                )]
            ) + '\n'
    else:
        result += HORIZ_LINE + ''.join([
            'match.{match_attr}(): {value}\n'.format(
                match_attr=add_color(i, fg='green', bold=True),
                value=add_color(
                    str(getattr(match, i)()), fg='white', bold='True'
                )
            ) for i in GROUP_ATTRS
        ])
    return result


def disp_str_pos(
    string, str_pos, marks=None, num_codes=0, window=DBUG_WINDOW_SIZE
):
    disp_str = string
    if marks is None:
        marks = []
    positions = {}
    for position in marks:
        positions[position] = (
            positions.get(position, '') +
            Fore.RED + Style.BRIGHT +
            '|' +
            Fore.RESET + Style.NORMAL
        )
    positions[str_pos] = (
        positions.get(str_pos, '') +
        Fore.GREEN + Style.BRIGHT +
        '>' +
        Fore.RESET + Style.NORMAL
    )
    offset = 0
    for position, markers in sorted(positions.items()):
        marker_pos = position + offset
        disp_str = disp_str[:marker_pos] + markers + disp_str[marker_pos:]
        offset += len(markers)
    padding = int(math.log(max(len(string), num_codes), 10)) + 2
    output = add_color(str(str_pos).rjust(padding) + ': ', fg='yellow')
    # return output + disp_str[max(position - int(window/2), 0):window]
    # need to fix so it doesn't cut off at partial escape code
    return output + disp_str

def disp_pattern_pos(
    opname, args, pattern, code_pos, str_len=0, window=DBUG_WINDOW_SIZE
):
    def segment(start=None, end=None, bold=False):
        sep = add_color(', ', fg='cyan')
        pattern_str = (
            add_color(repr(i), fg='cyan', bold=bold)
            for i in pattern[start:end]
        )
        if bold:
            pointer = (
                get_color(fg='yellow') + '>' + get_color(fg='cyan', bold=True)
            )
            pattern_str = (pointer + i for i in pattern_str)
        return sep.join(pattern_str)

    literals = [n + 1 for n, i in enumerate(pattern) if 'LITERAL' in str(i)]
    pattern = [chr(i) if n in literals else i for n, i in enumerate(pattern)]
    end_pos = code_pos + len(args[0]) + 1
    pointer = add_color('>', fg='yellow')
    highlighted = pointer + segment(code_pos, end_pos, bold=True)
    if code_pos:
        if end_pos < len(pattern):
            segments = (
                segment(end=code_pos),
                highlighted,
                segment(end_pos)
            )
        else:
            segments = (segment(end=code_pos), highlighted)
    else:
        segments = (highlighted, segment(end_pos))
    segments = ', '.join(segments)
    padding = int(math.log(max(len(pattern), str_len), 10)) + 2
    output = '{}: [{}]'.format(
        add_color(str(code_pos).rjust(padding), fg='cyan'),
        segments
    )
    #return output[max(code_pos - int(window/2), 0):window]
    # need to fix so it doesn't cut off at partial escape code
    return output


def op_logger(dispatcher, ctx, opname, *args):
        num_args = len(args[0])
        yield add_color(HORIZ_LINE, fg='yellow')
        last_str_pos = dispatcher._dbug.last_str_pos
        last_marks = dispatcher._dbug.last_marks
        # if 'LITERAL' in opname:
        #    char = add_color(chr(args[0][0]), fg='white', bold=True)
        #    arg_string = "'" + char + "'"
        # elif num_args == 0:
        #    arg_string = ''
        # elif num_args == 1:
        #    arg_string = str(args[0][0])
        # else:
        #    arg_string = ("%s " * len(args)) % args
        # yield '{}. {} {}'.format(
        #    dispatcher._dbug.op_count, opname, arg_string
        # )
        if (
            ctx.string_position != last_str_pos or
            ctx.state.marks != last_marks
        ):
            yield disp_str_pos(
                ctx.state.string,
                ctx.string_position,
                ctx.state.marks,
                num_codes=len(ctx.pattern_codes)
            )
        # yield add_color(
        #    '\n {:>2}: {}'.format(
        #        ctx.code_position, ctx.pattern_codes
        #    ), fg='cyan'
        # )
        yield disp_pattern_pos(
            opname,
            args,
            ctx.pattern_codes,
            ctx.code_position,
            str_len=len(ctx.state.string)
        )

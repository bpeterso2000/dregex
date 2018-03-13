from pprint import pformat

import colorama
from colorama import Fore, Style

import highlight
from highlight import Color, add_color, get_color

colorama.init()

# max num search string chars to display while debugging
DBUG_WINDOW_SIZE = 76
GROUP_ATTRS = ['group', 'start', 'end', 'span']
HORIZ_LINE = add_color('-' * 76, fg='yellow')


class OpTracker:
    """Friendly debug reports."""

    def __init__(self):
        self.op_count = 0
        self.last_str_pos = None
        self.last_marks = []


def show_match(match):
    result = HORIZ_LINE + '\n'
    if match:
        hi = [Color(match.start(), match.end(), get_color('RED', bold=True))]
        result += highlight.apply_styles(match.string, hi) + '\n'
    if match.groupdict():
        # regex uses group names
        result += '{hline}\nmatch.groupdict(): {value}'.format(
            hline=HORIZ_LINE,
            value=pformat(match.groupdict)
        )
    if match.groups():
        # regex uses groups
        for group_num, group in enumerate(match.groups()):
            result += HORIZ_LINE + '\n' + ''.join([
                'match.{match_attr}({match_num}): {value}\n'.format(
                    match_attr=add_color(i, fg='green', bold=True),
                    match_num=add_color(group_num, fg='yellow', bold=True),
                    value=add_color(
                        getattr(group, i)(group_num), fg='white', bold='True'
                    )
                ) for i in GROUP_ATTRS
            ])
            result += highlight.apply_styles(
                match.string, [group.span(group_num)]
            )
        result += 'match.groups(): {}\nmatch.regs(): {}'.format(
            add_color(match.groups(), fg='green', bold=True),
            add_color(match.regs(), fg='green', bold=True)
        )
    else:
        result += HORIZ_LINE + '\n' + ''.join([
            'match.{match_attr}(): {value}\n'.format(
                match_attr=add_color(i, fg='green', bold=True),
                value=add_color(
                    str(getattr(match, i)()), fg='white', bold='True'
                )
            ) for i in GROUP_ATTRS
        ])
    return result


def disp_str_pos(string, str_pos, marks=None, window=DBUG_WINDOW_SIZE):
    disp_str = string
    if marks is None:
        marks = []
    window_offset = int(window/2)
    positions = {}
    for position in marks:
        positions[position] = (
            positions.get(position, '') +
            Fore.RED + Style.BRIGHT + '|' +
            Fore.RESET + Style.NORMAL
        )
    positions[str_pos] = (
        positions.get(str_pos, '') +
        Fore.GREEN + Style.BRIGHT + '>' +
        Fore.RESET + Style.NORMAL
    )
    offset = 0
    for position, markers in sorted(positions.items()):
        marker_pos = position + offset
        disp_str = disp_str[:marker_pos] + markers + disp_str[marker_pos:]
        offset += len(markers)
    return disp_str[max(position - window_offset, 0):window]


def op_logger(dispatcher, ctx, opname, *args):
        last_str_pos = dispatcher._dbug.last_str_pos
        last_marks = dispatcher._dbug.last_marks
        if (
            ctx.string_position != last_str_pos or
            ctx.state.marks != last_marks
        ):
            yield disp_str_pos(
                ctx.state.string,
                ctx.string_position,
                ctx.state.marks
            )
            yield '-' * 76
        arg_string = ("%s " * len(args)) % args
        disp_op = '{}. {} {}'.format(
            dispatcher._dbug.op_count, opname, arg_string
        )
        yield disp_op

        # _log(context.pattern_codes)
        # print(vars(context))
        # print(vars(context.state))
        # print()
        # _log("|%s|%s|%s %s" % (context.mark_stack,
        #      context.string_position, opname, arg_string))

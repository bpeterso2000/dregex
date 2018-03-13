from collections import namedtuple

from colorama import init, Fore, Back, Style

init()

Color = namedtuple('Style', ['start', 'end', 'color'])


def get_color(fg=None, bg=None, bold=False):
    return (
        getattr(Fore, fg.upper() if fg else 'RESET') +
        getattr(Back, bg.upper() if bg else 'RESET') +
        getattr(Style, 'BRIGHT' if bold else 'NORMAL')
    )


RESET = get_color()


def add_color(s, fg=None, bg=None, bold=False):
    return get_color(fg=fg, bg=bg, bold=bold) + s + RESET


def restore_color(colors, end):
    previous_color_positions = [k for k in colors if k <= end]
    if previous_color_positions:
        previous_color = colors[max(previous_color_positions)]
        return previous_color


def get_style_strings(string, colors):
    if not colors:
        return string

    yield RESET
    last_pos = 0
    for pos, color in sorted(colors.items()):
        yield string[last_pos:pos] + color
        last_pos = pos
    yield string[last_pos:] + RESET


def reset_in_color_span(pos, start, end, color):
    return start <= pos <= end and Fore.RESET in color


def apply_styles(string, styles):
    colors = {}
    for start, end, color in sorted(
        styles, key=lambda x: x.end - x.start,
        reverse=True
    ):
        end = len(string) if end is None else end
        colors[end] = restore_color(colors, end) or RESET
        colors[start or 0] = color
        colors = {
            k: color if reset_in_color_span(k, start, end, color) else v
            for k, v in colors.items()
        }
    text = get_style_strings(string, colors)
    return ''.join(text)

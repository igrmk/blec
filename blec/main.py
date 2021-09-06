#!/usr/bin/python3

import sys
import re
import argparse
import math

__version__ = '1.1.3'

OPACITY = "(:\\d+(\\.\\d+)?|:\\.\\d+|:\\d+\\.)?"
HEX_SHORT_RE = re.compile(f'^[0-9A-Fa-f]{{3}}{OPACITY}$')
HEX_COMP3_RE = re.compile(f'^[0-9A-Fa-f]{{6}}{OPACITY}$')
HEX_COMP4_RE = re.compile('^[0-9A-Fa-f]{8}$')
DEC_COMP3_RE = re.compile(f'^\\[\\d+(,\\d+){{2}}\\]{OPACITY}$')
DEC_COMP4_RE = re.compile('^\\[\\d+(,\\d+){3}\\]$')

STD_COLORS = {
    'white': (1.0, 1.0, 1.0),
    'black': (0.0, 0.0, 0.0),
}

STD_COLORS_RE = re.compile('^' + '|'.join(STD_COLORS) + OPACITY + '$')


class PowerLaw:
    def __init__(self, gamma):
        self.gamma = gamma

    def to(self, x):
        return math.pow(x, self.gamma)

    def from_(self, x):
        return math.pow(x, 1 / self.gamma)


class Srgb:
    @staticmethod
    def to(x):
        if x <= 0.03928:
            return x / 12.92
        return math.pow((x + 0.055) / 1.055, 2.4)

    @staticmethod
    def from_(x):
        if x <= 0.00304:
            return 12.92 * x
        return 1.055 * math.pow(x, 1 / 2.4) - 0.055


def n_from_hex(number):
    return int(number, 16) / 255.0


def n_from_short_hex(number):
    return int(number, 16) * 17 / 255.0


def n_to_255(number):
    return int(round(number * 255))


def to_255(color):
    return tuple(map(n_to_255, color))


def to_argb_hex(color):
    return '{:02x}{:02x}{:02x}{:02x}'.format(color[3], *to_255(color[:3]))


def to_rgb_hex(color):
    return '{:02x}{:02x}{:02x}'.format(*to_255(color[:3]))


def to_rgba_hex(color):
    return '{:02x}{:02x}{:02x}{:02x}'.format(*to_255(color))


def from_rgb_hex(s):
    r, g, b = s[0:2], s[2:4], s[4:6]
    a = 1.0
    if len(s) > 6:
        s = s[7:]
        a = float(s)
    return tuple(map(n_from_hex, [r, g, b])) + (a,)


def from_std_color(s):
    parts = s.split(':')
    r, g, b = STD_COLORS[parts[0]]
    a = 1.0
    if len(parts) == 2:
        a = float(parts[1])
    return r, g, b, a


def from_rgb_short_hex(s):
    r, g, b = s[0], s[1], s[2]
    a = 1.0
    if len(s) > 3:
        s = s[4:]
        a = float(s)
    return tuple(map(n_from_short_hex, [r, g, b])) + (a,)


def from_argb_hex(s):
    a, r, g, b = s[0:2], s[2:4], s[4:6], s[6:8]
    return tuple(map(n_from_hex, [r, g, b, a]))


def from_rgba_hex(s):
    r, g, b, a = s[0:2], s[2:4], s[4:6], s[6:8]
    return tuple(map(n_from_hex, [r, g, b, a]))


def from_rgb_dec(s):
    end = s.find(']')
    r, g, b = s[1:end].split(',')
    a = 1.0
    if len(s) > end + 1:
        s = s[end + 2:]
        a = float(s)
    color = [int(x) / 255 for x in [r, g, b]]
    return tuple(color + [a])


def from_rgba_dec(s):
    s = s[1:-1]
    r, g, b, a = s.split(',')
    return tuple(int(x) / 255 for x in [r, g, b, a])


def from_argb_dec(s):
    s = s[1:-1]
    a, r, g, b = s.split(',')
    return tuple(int(x) / 255 for x in [r, g, b, a])


def blend_comp(trans, dst, src, dst_a, src_a, out_a):
    src = trans.to(src)
    dst = trans.to(dst)
    out = (src * src_a + dst * dst_a * (1.0 - src_a)) / out_a
    out = trans.from_(out)
    return out


def blend(trans, *colors):
    if not colors:
        return (0, 0, 0, 0)
    dst = colors[0]
    for src in colors[1:]:
        out_a = src[3] + dst[3] * (1.0 - src[3])
        if out_a == 0:
            dst = (0, 0, 0, 0)
        else:
            dst = tuple(
                blend_comp(trans, dst[i], src[i], dst[3], src[3], out_a)
                for i in range(3))
            dst += (out_a,)
    return dst


def parse_color(argb, str_):
    if STD_COLORS_RE.match(str_):
        return from_std_color(str_)
    if HEX_SHORT_RE.match(str_):
        return from_rgb_short_hex(str_)
    if HEX_COMP3_RE.match(str_):
        return from_rgb_hex(str_)
    if HEX_COMP4_RE.match(str_):
        if argb:
            return from_argb_hex(str_)
        return from_rgba_hex(str_)
    if DEC_COMP3_RE.match(str_):
        return from_rgb_dec(str_)
    if DEC_COMP4_RE.match(str_):
        if argb:
            return from_argb_dec(str_)
        return from_rgba_dec(str_)

    raise Exception('cannot parse color ' + str_)


def parse_and_check_color(argb, str_):
    color = parse_color(argb, str_)
    if any(comp > 1.0 for comp in color):
        raise Exception('color is out of range ' + str_)
    return color


def parse(colors, argb):
    return [parse_and_check_color(argb, str_) for str_ in colors]


def process(colors, argb, trans):
    parsed = parse(colors, argb)
    res = blend(trans, *parsed)
    if res[3] >= 254.5 / 255:
        return to_rgb_hex(res)
    if argb:
        return to_argb_hex(res)
    return to_rgba_hex(res)


def main():
    def formatter_class(prog):
        return argparse.RawTextHelpFormatter(
            prog,
            max_help_position=27,
            width=80)
    parser = argparse.ArgumentParser(
        formatter_class=formatter_class,
        description=(
            'Calculate a resulting color of the alpha blending process.\n'
            'Enumerate colors from the bottom to the top.'),
        epilog=(
            'examples — blend 75% black on pure white:\n'
            '    blec white black:0.75\n'
            '    blec fff 000000bf\n'
            '    blec ffffffff [0,0,0,191]\n'
            '    blec ffffff:1 [0,0,0]:0.75')
        )
    parser.add_argument(
        'colors',
        nargs='*',
        metavar='COLOR',
        help=(
            'color in following formats\n\n'
            'RGB\n'
            'RGB:opacity\n'
            'RRGGBB\n'
            'RRGGBB:opacity\n'
            'RRGGBBAA\n'
            '[r,g,b]\n'
            '[r,g,b]:opacity\n'
            '[r,g,b,a]\n'
            'white or black\n'
            'white:opacity or black:opacity\n\n'
            'where R, G, B, A — hexadecimal digits\n'
            '      0 ≤ opacity ≤ 1\n'
            '      0 ≤ r, g, b, a ≤ 255'))
    parser.add_argument(
        '--argb',
        action='store_true',
        help='use AARRGGBB and [a,r,g,b] instead of RRGGBBAA and [r,g,b,a]')
    parser.add_argument(
        '-g',
        '--gamma',
        metavar='GAMMA',
        help='floating number or "sRGB" (default) or "AdobeRGB"',
        default='sRGB',
        type=str)
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='print version and exit')
    parser.add_argument(
        '--parse',
        action='store_true',
        help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.version:
        print(__version__)
        sys.exit(0)
    try:
        if args.parse:
            parsed = parse(args.colors, args.argb)
            print(' '.join(str(p) for p in parsed))
            sys.exit(0)
        if args.gamma == 'sRGB':
            gamma = Srgb()
        elif args.gamma == 'AdobeRGB':
            gamma = PowerLaw(2.19921875)
        else:
            try:
                gamma = float(args.gamma)
            except ValueError:
                raise Exception('invalid gamma value')
            if gamma < 1:
                raise Exception('gamma shoud be higher or equal to 1')
            gamma = PowerLaw(gamma)
        print(process(args.colors, args.argb, gamma))
    except Exception as err:
        print("error: " + str(err), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

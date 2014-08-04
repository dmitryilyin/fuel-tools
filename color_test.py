#!/usr/bin/env python
import argparse
from color import Color
import sys


color = Color()
parser = argparse.ArgumentParser()
parser.add_argument('text', nargs='?', help='text string to show', default='Hello World!')
parser.add_argument("-f", "--foreground", help="foreground color", type=str, choices=sorted(color.color_table.keys()), default='off')
parser.add_argument("-b", "--background", help="background color", type=str, choices=sorted(color.color_table.keys()), default='off')
parser.add_argument("-a", "--attribute", help="text attribute", type=str, choices=sorted(color.attribute_table.keys()), default='normal')
parser.add_argument("-F", "--bright_foreground", help="set foreground to bright", action='store_true')
parser.add_argument("-B", "--bright_background", help="set background to bright", action='store_true')
parser.add_argument("-t", "--type", help="align type", type=str, choices=color.align_types, default='off')
parser.add_argument("-w", "--width", help="align width", type=int, default=0)
args = parser.parse_args()

color.set_foreground(args.foreground)
color.set_background(args.background)
color.set_attribute(args.attribute)
color.set_bright_foreground(args.bright_foreground)
color.set_bright_background(args.bright_background)
color.set_width(args.width)
color.set_align(args.type)

sys.stdout.write(color(args.text) + "\n")
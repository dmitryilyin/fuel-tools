#!/usr/bin/env python
from color import Color
import sys


democolor = Color()

colors = sorted(democolor.color_table.keys())
colors.insert(0, None)
attributes = sorted(democolor.attribute_table.keys())
brightness = [False, True]

for bg in colors:
    for fg in colors:
        for attr in attributes:
            for bright_background in brightness:
                for bright_foreground in brightness:
                    democolor.set_foreground(fg)
                    democolor.set_background(bg)
                    democolor.set_attribute(attr)
                    democolor.set_bright_foreground(bright_foreground)
                    democolor.set_bright_background(bright_background)
                    democolor.set_width(20)
                    democolor.set_align('center')
                    sys.stdout.write(democolor("Hello World!") + "\t" + repr(democolor) + "\n")

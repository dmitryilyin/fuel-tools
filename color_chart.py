#!/usr/bin/env python
from color import Color
import sys


democolor = Color()
for fg in [None] + list(range(0, 7)):
    for bg in [None] + list(range(0, 7)):
        for attr in sorted(democolor.attrtable.values()):
            democolor.setFG(fg)
            democolor.setBG(bg)
            democolor.setATTR(attr)
            democolor.brightfg = False
            democolor.brightbg = False
            sys.stdout.write(democolor("Hello World!") + "\t" + repr(democolor) + "\n")
            democolor.brightfg = True
            sys.stdout.write(democolor("Hello World!") + "\t" + repr(democolor) + "\n")
            democolor.brightbg = True
            sys.stdout.write(democolor("Hello World!") + "\t" + repr(democolor) + "\n")

class Color:
    """
    A custom fancy colors class
    """
    def __init__(self, fgcode=None, bgcode=None, attrcode=0, enabled=True, brightfg=False, brightbg=False):
        self.start = "\033["
        self.end = "m"
        self.reset = self.start + "0" + self.end

        if enabled:
            self.enabled = True
        else:
            self.enabled = False

        if brightfg:
            self.brightfg = True
        else:
            self.brightfg = False

        if brightbg:
            self.brightbg = True
        else:
            self.brightbg = False

        self.fgoffset = 30
        self.bgoffset = 40
        self.brightoffset = 60

        self.colortable = {
            'black': 0,
            'red': 1,
            'green': 2,
            'yellow': 3,
            'blue': 4,
            'magneta': 5,
            'cyan': 6,
            'white': 7,
            'off': None,
        }

        self.attrtable = {
            'normal': 0,
            'bold': 1,
            'faint': 2,
            #'italic':    3,
            'underline': 4,
            'blink': 5,
            #'rblink':    6,
            'negative': 7,
            'conceal': 8,
            #'crossed':   9,
            'off': 0,
        }

        self.setFG(fgcode)
        self.setBG(bgcode)
        self.setATTR(attrcode)

    def toggle_enabled(self):
        if self.enabled:
            self.enabled = False
        else:
            self.enabled = True

    def toggle_brightfg(self):
        if self.brightfg:
            self.brightfg = False
        else:
            self.brightfg = True

    def toggle_brightbg(self):
        if self.brightbg:
            self.brightbg = False
        else:
            self.brightbg = True

    def setFG(self, color):
        if type(color) == int:
            self.fgcode = color
            return True
        if color in self.colortable:
            self.fgcode = self.colortable[color]
            return True
        self.fgcode = None
        return False

    def setBG(self, color):
        if type(color) == int:
            self.bgcode = color
            return True
        if color in self.colortable:
            self.bgcode = self.colortable[color]
            return True
        self.bgcode = None
        return False

    def setATTR(self, color):
        if type(color) == int:
            self.attrcode = color
            return True
        if color in self.attrtable:
            self.attrcode = self.attrtable[color]
            return True
        self.attrcode = 0
        return False

    def escape(self):
        components = []
        attrcode = self.attrcode

        if self.fgcode is not None:
            fgcode = self.fgoffset + self.fgcode
            if self.brightfg:
                fgcode += self.brightoffset
        else:
            fgcode = None

        if self.bgcode is not None:
            bgcode = self.bgoffset + self.bgcode
            if self.brightbg:
                bgcode += self.brightoffset
        else:
            bgcode = None

        components.append(attrcode)
        if fgcode:
            components.append(fgcode)
        if bgcode:
            components.append(bgcode)

        escstr = self.start + ";".join(map(str, components)) + self.end
        return escstr

    def __str__(self):
        return self.escape()

    def __repr__(self):
        return "Color(fgcode=%s, bgcode=%s, attrcode=%s, enabled=%s, brightfg=%s, brightbg=%s)" % (
            self.fgcode,
            self.bgcode,
            self.attrcode,
            str(self.enabled),
            str(self.brightfg),
            str(self.brightbg),
        )

    def __call__(self, string):
        if self.enabled:
            return self.escape() + string + self.reset
        else:
            return string

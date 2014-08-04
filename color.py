import sys


class Color:
    """
    A custom fancy colors class
    """

    def __init__(
            self,
            foreground=None,
            background=None,
            attribute=0,
            enabled=True,
            bright_foreground=False,
            bright_background=False,
            align='off',
            width=0,
    ):
        self.start = "\033["
        self.end = "m"
        self.reset = self.start + "0" + self.end
        self.charset = 'utf-8'

        self.foreground_offset = 30
        self.background_offset = 40
        self.brightness_offset = 60

        self.color_table = {
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

        self.attribute_table = {
            'normal': 0,
            'bold': 1,
            'faint': 2,
            'italic': 3,
            'underline': 4,
            'blink': 5,
            'rblink': 6,
            'negative': 7,
            'conceal': 8,
            'crossed': 9,
            'off': 0,
        }

        self.align_types = ['left', 'right', 'center', 'off']

        self.invert_color_table = None
        self.invert_attribute_table = None

        self.set_foreground(foreground)
        self.set_background(background)
        self.set_attribute(attribute)
        self.set_width(width)
        self.set_align(align)
        self.set_enabled(enabled)
        self.set_bright_foreground(bright_foreground)
        self.set_bright_background(bright_background)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def set_bright_foreground(self, bright_foreground):
        self.bright_foreground = bool(bright_foreground)

    def set_bright_background(self, bright_background):
        self.bright_background = bool(bright_background)

    def toggle_enabled(self):
        if self.enabled:
            self.enabled = False
        else:
            self.enabled = True

    def toggle_bright_foreground(self):
        if self.bright_foreground:
            self.bright_foreground = False
        else:
            self.bright_foreground = True

    def toggle_bright_background(self):
        if self.bright_background:
            self.bright_background = False
        else:
            self.bright_background = True

    def set_align(self, align):
        if align in self.align_types:
            self.align = align
            return True
        else:
            return False

    def set_width(self, width):
        if type(width) != int:
            width = width.to_i
        self.width = abs(width)

    def align_string(self, string, width=None, align=None):
        if not width:
            width = self.width
        if not align:
            align = self.align

        if width == 0 or align == 'off':
            return string

        if sys.version_info < (3, 0):
            string = string.decode(self.charset)

        if align == 'right':
            string = string[0:width].rjust(width)
        elif align == 'center':
            string = string[0:width].center(width)
        elif align == 'left':
            string = string[0:width].ljust(width)

        if sys.version_info < (3, 0):
            string = string.encode(self.charset)

        return string

    def set_foreground(self, color):
        if type(color) == int:
            self.foreground_code = abs(color)
            return True
        if color in self.color_table:
            self.foreground_code = self.color_table[color]
            return True
        self.foreground_code = None
        return False

    def set_background(self, color):
        if type(color) == int:
            self.background_code = abs(color)
            return True
        if color in self.color_table:
            self.background_code = self.color_table[color]
            return True
        self.background_code = None
        return False

    def set_attribute(self, attribute):
        if type(attribute) == int:
            self.attribute_code = abs(attribute)
            return True
        if attribute in self.attribute_table:
            self.attribute_code = self.attribute_table[attribute]
            return True
        self.attribute_code = 0
        return False

    def color_string(self):
        components = []
        attribute_code = self.attribute_code

        if self.foreground_code is not None:
            forteground_code = self.foreground_offset + self.foreground_code
            if self.bright_foreground:
                forteground_code += self.brightness_offset
        else:
            forteground_code = None

        if self.background_code is not None:
            background_code = self.background_offset + self.background_code
            if self.bright_background:
                background_code += self.brightness_offset
        else:
            background_code = None

        components.append(attribute_code)
        if forteground_code:
            components.append(forteground_code)
        if background_code:
            components.append(background_code)

        return self.start + ";".join(map(str, components)) + self.end

    def show(self):
        if not self.invert_color_table:
            self.invert_color_table = dict((v, k) for k, v in self.color_table.iteritems())
        if not self.invert_attribute_table:
            self.invert_attribute_table = dict((v, k) for k, v in self.attribute_table.iteritems())
        return "Color(foreground='%s', background='%s', attribute='%s', bright_foreground=%s, bright_background=%s)" % (
            self.invert_color_table[self.foreground_code],
            self.invert_color_table[self.background_code],
            self.invert_attribute_table[self.attribute_code],
            str(self.bright_foreground),
            str(self.bright_background),
        )

    def process(self, string, width=None, align=None):
        if self.enabled:
            return self.color_string() + self.align_string(string, width, align) + self.reset
        else:
            return string

    def __call__(self, string, width=None, align=None):
        return self.process(string, width, align)

    def __str__(self):
        return self.color_string()

    def __repr__(self):
        return self.show()
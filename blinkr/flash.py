import random
from blinkr.animation import Animation

###############################################################################

RIGHT_BOTTOM_LEN = 40
RIGHT_BOTTOM_START = 0
RIGHT_BOTTOM_END = RIGHT_BOTTOM_START + RIGHT_BOTTOM_LEN

BOTTOM_LEN = 57
BOTTOM_START = RIGHT_BOTTOM_END + 1
BOTTOM_END = BOTTOM_START + BOTTOM_LEN

LEFT_LEN = 100
LEFT_START = BOTTOM_END + 1
LEFT_END = LEFT_START + LEFT_LEN

TOP_LEN = 58
TOP_START = LEFT_END + 1
TOP_END = TOP_START + TOP_LEN

RIGHT_TOP_LEN = 40
RIGHT_TOP_START = TOP_END + 1
RIGHT_TOP_END = RIGHT_TOP_START + RIGHT_TOP_LEN


RIGHT_BOTTOM = set(range(RIGHT_BOTTOM_START, RIGHT_BOTTOM_END))
BOTTOM = set(range(BOTTOM_START, BOTTOM_END))
LEFT = set(range(LEFT_START, LEFT_END))
TOP = set(range(TOP_START, TOP_END))
RIGHT_TOP = set(range(RIGHT_TOP_START, RIGHT_TOP_END))

NEXT_TO_QR = set(0, 1, 2, 338, 337, 336}

NEXT_TO_BUTTONS = set(range(10, 30)}

SECTIONS = {"RIGHT_BOTTOM":    RIGHT_BOTTOM,
            "BOTTOM":          BOTTOM,
            "LEFT":            LEFT,
            "TOP":             TOP,
            "RIGHT":           RIGHT,
            "RIGHT_TOP":       RIGHT_TOP,
            "NEXT_TO_QR":      NEXT_TO_QR,
            "NEXT_TO_BUTTONS": NEXT_TO_BUTTONS}

SECTION_LIST = list(SECTIONS.keys())

###############################################################################

OFF = (0, 0, 0)
ON = (255, 255, 255)

class Flash(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.idx = 0

    def exec_update(self):
        section = SECTION_LIST[self.idx]
        self.idx += 1
        self.idx = self.idx % len(SECTION_LIST)
        pixels_on = SECTIONS[section]
        rgbs = [(ON if p in pixels_on else OFF) for p in
                range(len(self.pixels))]
        pixels[:] = rgbs[:]
        pixels.write()
        return 1.0

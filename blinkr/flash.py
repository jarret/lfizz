import random
from animation import Animation

###############################################################################

RIGHT_BOTTOM_LEN = 80
RIGHT_BOTTOM_START = 0
RIGHT_BOTTOM_END = RIGHT_BOTTOM_START + RIGHT_BOTTOM_LEN

BOTTOM_LEN = 57
BOTTOM_START = RIGHT_BOTTOM_END
BOTTOM_END = BOTTOM_START + BOTTOM_LEN

LEFT_LEN = 112
LEFT_START = BOTTOM_END
LEFT_END = LEFT_START + LEFT_LEN

TOP_LEN = 58
TOP_START = LEFT_END
TOP_END = TOP_START + TOP_LEN

RIGHT_TOP_LEN = 40
RIGHT_TOP_START = TOP_END
RIGHT_TOP_END = RIGHT_TOP_START + RIGHT_TOP_LEN


RIGHT_BOTTOM = set(range(RIGHT_BOTTOM_START, RIGHT_BOTTOM_END))
BOTTOM = set(range(BOTTOM_START, BOTTOM_END))
LEFT = set(range(LEFT_START, LEFT_END))
TOP = set(range(TOP_START, TOP_END))
RIGHT_TOP = set(range(RIGHT_TOP_START, RIGHT_TOP_END))

NEXT_TO_QR = {0, 1, 2, 3, 4, 5, 338, 337, 336}

NEXT_TO_BUTTONS = set(range(15, 37))

SECTIONS = {"RIGHT_BOTTOM":    RIGHT_BOTTOM,
            "BOTTOM":          BOTTOM,
            "LEFT":            LEFT,
            "TOP":             TOP,
            "RIGHT_TOP":       RIGHT_TOP,
            "NEXT_TO_QR":      NEXT_TO_QR,
            "NEXT_TO_BUTTONS": NEXT_TO_BUTTONS}

SECTION_LIST = list(sorted(SECTIONS.keys()))

###############################################################################

OFF = (0, 0, 0)
ON = (255, 255, 255)

class Flash(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)

    def exec_update(self):
        section = random.choice(SECTION_LIST)
        #print("section: %s" % section)
        pixels_on = SECTIONS[section]
        rgbs = [(ON if p in pixels_on else OFF) for p in
                range(len(self.pixels))]
        self.pixels[:] = rgbs[:]
        self.pixels.write()
        return 0.1

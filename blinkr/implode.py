import time
import random
from animation import Animation

###############################################################################

ALL_PIXELS = set(range(0, 338))

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

RIGHT_TOP_LEN = 31
RIGHT_TOP_START = TOP_END
RIGHT_TOP_END = RIGHT_TOP_START + RIGHT_TOP_LEN


RIGHT_BOTTOM = set(range(RIGHT_BOTTOM_START, RIGHT_BOTTOM_END))
BOTTOM = set(range(BOTTOM_START, BOTTOM_END))
LEFT = set(range(LEFT_START, LEFT_END))
TOP = set(range(TOP_START, TOP_END))
RIGHT_TOP = set(range(RIGHT_TOP_START, RIGHT_TOP_END))

NEXT_TO_QR = {0, 1, 2, 3, 4, 5, 338, 337, 336}

NEXT_TO_BUTTONS = set(range(15, 37))
NOT_NEXT_TO_BUTTONS = ALL_PIXELS.difference(NEXT_TO_BUTTONS)


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

LERP_SECONDS = 1.5

class Implode(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.running = False
        self.not_next = list(NOT_NEXT_TO_BUTTONS)

    def setup(self):
        self.lerp_start_time = time.time()
        self.lerp_end_time = self.lerp_start_time + LERP_SECONDS
        self.lerps = []
        for p in NEXT_TO_BUTTONS:
            start_pixel = random.choice(self.not_next)
            if start_pixel > 169:
                end_pixel = p + 338
            else:
                end_pixel = p
            self.lerps.append({'start_pixel': start_pixel,
                               'end_pixel':   end_pixel})

    def exec_update(self):
        now = time.time()
        if now > self.lerp_end_time:
            pixels_on = NEXT_TO_BUTTONS
        else:
            progress = 1.0 - ((self.lerp_end_time - now) /
                        (self.lerp_end_time - self.lerp_start_time))
            pixels_on = set()
            for l in self.lerps:
                distance = l['end_pixel'] - l['start_pixel']
                on_pixel = self.modpixel(l['start_pixel'] +
                                         round(distance * progress))
                pixels_on.add(on_pixel)

        rgbs = [(ON if p in pixels_on else OFF) for p in
                range(len(self.pixels))]
        self.pixels[:] = rgbs[:]
        self.pixels.write()
        return 0.01


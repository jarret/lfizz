import time
import random

class Animation():
    def __init__(self, pixels):
        self.pixels = pixels

    def setup(self):
        pass

    def mod256(v):
        return v % 256

    def modpixel(self, v):
        return v % len(self.pixels)

    def wheel(pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    def wheelmod256(pos):
        pos = Animation.mod256(pos)
        return Animation.wheel(pos)

    def squeeze256(val, top):
        val = val % top
        factor = 256.0 / top
        #print("factor: %.04f" % factor)
        return round(factor * val)

    def opposite(pos):
        return Animation.mod256(pos + 128)

    def now():
        return int(time.time())

    def rand_past():
        return Animation.now() - random.randint(0, 3)

    def rand_future():
        return Animation.now() + random.randint(2, 8)

import random
from animation import Animation


class Error(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.even = True

    def exec_update(self):
        for i in range(len(self.pixels)):
            if (i % 2) == (0 if self.even else 1):
                self.pixels[i] = (255, 0, 0)
            else:
                self.pixels[i] = (0, 0, 0)
        self.even = not self.even
        self.pixels.write()
        return 2.0

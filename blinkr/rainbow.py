import math
import time
from animation import Animation


class Rainbow(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.state = {'positions': [p for p in range(len(pixels))]}

    def exec_update(self):
        a = round(((math.sin(5.0 * time.time()) + 1) / 2) * 15) + 5
        self.state['positions'] = [p + a for p in self.state['positions']]
        rgbs = [Animation.wheel(Animation.squeeze256(p, len(self.pixels)))
                for p in self.state['positions']]
        self.pixels[:] = rgbs[:]
        self.pixels.write()
        return 0.01

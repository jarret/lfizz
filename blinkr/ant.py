import random
from blinkr.animation import Animation


class Ant(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        rand_color_pos_0 = random.randint(0, 255)
        rand_pixel_0 = random.randint(0, len(self.pixels) - 1)
        self.state = {'base_color_pos': rand_color_pos_0,
                      'ant_pixel':      rand_pixel_0,
                      'counter':        0}

    def exec_update(self):
        body_color = Animation.wheel(self.state['base_color_pos'])
        rgbs = [body_color for _ in range(len(self.pixels))]

        px_start = self.state['ant_pixel']
        px_stop = self.state['ant_pixel'] + len(self.pixels)
        for p in range(px_start, px_stop, 4):
            ant_pixel = Animation.modpixel(p)
            ant_color_pos = Animation.opposite(self.state['base_color_pos'])
            rgbs[ant_pixel] = Animation.wheel(ant_color_pos)

        pixels[:] = rgbs[:]
        pixels.write()
        self.state['counter'] += 1
        if self.state['counter'] % 10 == 0:
            self.state['ant_pixel'] = Animation.modpixel(
                self.state['ant_pixel'] + 1)
        self.state['base_color_pos'] = Animation.mod256(
            self.state['base_color_pos'] + 1)
        return 0.005

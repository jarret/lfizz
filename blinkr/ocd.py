import time
import random
from animation import Animation


class Ocd(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        rand_color_pos_1 = random.randint(0, 255)
        rand_pixel_1 = random.randint(0, len(self.pixels))
        rand_pixel_2 = random.randint(0, len(self.pixels) - 1)
        self.state = {'base_color_pos':   rand_color_pos_1,
                      'lerp_start_pixel': rand_pixel_1,
                      'lerp_end_pixel':   rand_pixel_2,
                      'lerp_start_time':  Animation.rand_past(),
                      'lerp_end_time':    Animation.rand_future(),
                      'counter':          0}

    def new_ocd_lerp(self):
        self.state['lerp_start_pixel'] = self.state['lerp_end_pixel']
        self.state['lerp_end_pixel'] = random.randint(0, len(self.pixels) - 1)
        self.state['lerp_start_time'] = Animation.now()
        self.state['lerp_end_time'] = Animation.rand_future()

    def exec_update(self):
        body_color = Animation.wheel(self.state['base_color_pos'])
        rgbs = [body_color for _ in range(len(self.pixels))]

        now = time.time()
        if now > self.state['lerp_end_time']:
            self.new_ocd_lerp()
        progress = 1.0 - ((self.state['lerp_end_time'] - now) /
                    (self.state['lerp_end_time'] -
                     self.state['lerp_start_time']))

        distance = self.state['lerp_end_pixel'] - self.state['lerp_start_pixel']
        ant_pixel = self.state['lerp_start_pixel'] + round(distance * progress)

        ant_color_pos = Animation.opposite(self.state['base_color_pos'])
        rgbs[ant_pixel] = Animation.wheel(ant_color_pos)

        self.pixels[:] = rgbs[:]
        self.pixels.write()
        self.state['counter'] += 1
        return 0

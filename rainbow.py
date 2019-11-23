#!/usr/bin/env python3

import time
import random
import json

from queue import Queue

import board
from neopixel import NeoPixel

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

N_PIXELS = 150
BRIGHTNESS = 0.1
DATA_PIN = board.D18

MODES = {"RAINBOW", "ANT", "QUIT"}

class PixelStrip(object):
    def __init__(self):
        self.queue = Queue()
        self.last_mode = 'RAINBOW'

        lc = LoopingCall(self.flip_mode)
        lc.start(10.0)

    ###########################################################################

    def mod256(v):
        return v % 256

    def modpixel(v):
        return v % N_PIXELS

    def wheel(pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)


    def opposite(pos):
        return PixelStrip.mod256(pos + 128)

    def now():
        return int(time.time())

    def rand_past():
        return PixelStrip.now() - random.randint(0, 3)

    def rand_future():
        return PixelStrip.now() + random.randint(2, 8)

    ###########################################################################

    def flip_mode(self):
        if self.last_mode == 'RAINBOW':
            self.queue.put("ANT")
            self.last_mode = "ANT"
        elif self.last_mode == "ANT":
            self.queue.put("OCD")
            self.last_mode = "OCD"
        else:
            assert self.last_mode == "OCD"
            self.queue.put("RAINBOW")
            self.last_mode = "RAINBOW"

    ###########################################################################

    def rainbow_body(pixels, state):
        state['positions'] = [PixelStrip.mod256(p + 5) for p in
                              state['positions']]
        rgbs = [PixelStrip.wheel(p) for p in state['positions']]
        pixels[:] = rgbs[:]
        pixels.write()
        return 0.01

    def ant_body(pixels, state):
        body_color = PixelStrip.wheel(state['base_color_pos'])
        rgbs = [body_color for _ in range(N_PIXELS)]

        px_start = state['ant_pixel']
        px_stop = state['ant_pixel'] + N_PIXELS
        for p in range(px_start, px_stop, 4):
            ant_pixel = PixelStrip.modpixel(p)
            ant_color_pos = PixelStrip.opposite(state['base_color_pos'])
            rgbs[ant_pixel] = PixelStrip.wheel(ant_color_pos)

        pixels[:] = rgbs[:]
        pixels.write()
        state['counter'] += 1
        if state['counter'] % 10 == 0:
            state['ant_pixel'] = PixelStrip.modpixel(state['ant_pixel'] + 1)
        state['base_color_pos'] = PixelStrip.mod256(state['base_color_pos'] + 1)
        return 0.005

    def new_ocd_lerp(state):
        state['lerp_start_pixel'] = state['lerp_end_pixel']
        state['lerp_end_pixel'] = random.randint(0, N_PIXELS - 1)
        state['lerp_start_time'] = PixelStrip.now()
        state['lerp_end_time'] = PixelStrip.rand_future()

    def ocd_body(pixels, state):
        body_color = PixelStrip.wheel(state['base_color_pos'])
        rgbs = [body_color for _ in range(N_PIXELS)]

        now = time.time()
        if now > state['lerp_end_time']:
            PixelStrip.new_ocd_lerp(state)
            #print("new: %s" % state)
        progress = 1.0 - ((state['lerp_end_time'] - now) /
                    (state['lerp_end_time'] - state['lerp_start_time']))

        distance = state['lerp_end_pixel'] - state['lerp_start_pixel']
        ant_pixel = state['lerp_start_pixel'] + round(distance * progress)

        ant_color_pos = PixelStrip.opposite(state['base_color_pos'])
        rgbs[ant_pixel] = PixelStrip.wheel(ant_color_pos)

        pixels[:] = rgbs[:]
        pixels.write()
        state['counter'] += 1
        #if state['counter'] % 10 == 0:
        #    print(ant_pixel)

        #state['base_color_pos'] = PixelStrip.mod256(state['base_color_pos'] + 1)
        return 0

    def quit_body(pixels):
        rgbs = [(0, 0, 0) for _ in range(N_PIXELS)]
        pixels[:] = rgbs[:]
        pixels.write()

    ###########################################################################

    def thread_body(queue):
        pixels = NeoPixel(DATA_PIN, N_PIXELS, brightness=BRIGHTNESS,
                          auto_write=False)
        rainbow_init = {'positions': [p for p in range(N_PIXELS)]}
        rand_color_pos_0 = random.randint(0, 255)
        rand_pixel_0 = random.randint(0, N_PIXELS - 1)
        ant_init = {'base_color_pos': rand_color_pos_0,
                    'ant_pixel':      rand_pixel_0,
                    'counter':        0}
        rand_color_pos_1 = random.randint(0, 255)
        rand_pixel_1 = random.randint(0, N_PIXELS - 1)
        rand_pixel_2 = random.randint(0, N_PIXELS - 1)
        ocd_init = {'base_color_pos':   rand_color_pos_1,
                    'lerp_start_pixel': rand_pixel_1,
                    'lerp_end_pixel':   rand_pixel_2,
                    'lerp_start_time':  PixelStrip.rand_past(),
                    'lerp_end_time':    PixelStrip.rand_future(),
                    'counter':          0}

        state = {'rainbow': rainbow_init,
                 'ant':     ant_init,
                 'ocd':     ocd_init}

        mode = "OCD"
        while True:
            try:
                mode = queue.get_nowait()
                assert mode in MODES, "unknown mode %s" % mode
            except:
                pass
            if mode == "RAINBOW":
                sleep = PixelStrip.rainbow_body(pixels, state['rainbow'])
            elif mode == "ANT":
                sleep = PixelStrip.ant_body(pixels, state['ant'])
            elif mode == "OCD":
                sleep = PixelStrip.ocd_body(pixels, state['ocd'])
            else:
                assert mode == "QUIT"
                PixelStrip.quit_body(pixels)
                return
            time.sleep(sleep)

    def start_thread(self):
        reactor.callInThread(PixelStrip.thread_body, self.queue)

    def start(self):
        reactor.callLater(0.1, self.start_thread)

    def stop(self):
        self.queue.put("QUIT")

ps = PixelStrip()
ps.start()

reactor.addSystemEventTrigger("before", "shutdown", ps.stop)

reactor.run()

# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from third_party.waveshare.epd4in2 import EPD, EPD_WIDTH, EPD_HEIGHT
import time
import os
import datetime
import pytz

from twisted.internet import threads

from PIL import Image,ImageDraw,ImageFont
from qrdraw import QRDraw
from print import print_fancy_blue


WHITE = 0xff
BLACK = 0x00

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

FONT = "%s/third_party/Minecraftia.ttf" % SRC_PATH


class Eink(object):
    EPD = None

    def __init__(self, reactor):
        Eink.EPD.init()
        Eink.EPD.Clear(WHITE)
        Eink.EPD.wait_until_idle()
        self.draw_next = None
        self.drawing = False
        self.reactor = reactor

    def _display_image(image):
        Eink.EPD.wait_until_idle()
        start = time.time()
        #print("rotate")
        rotated = image.rotate(180)
        print("eink image rotated: %0.4f seconds" % (time.time() - start))

        start = time.time()
        b = Eink.EPD.getbuffer(rotated)
        print("eink get buffer: %0.4f" % (time.time() - start))
        start = time.time()
        Eink.EPD.display(b)
        print("eink display call: %0.4f" % (time.time() - start))

    ###########################################################################

    def queue_draw(self, func, *params):
        # stomp anything waiting with this.
        self.draw_next = {'func': func, 'params': params}

    def draw_from_queue(self):
        print_fancy_blue("check queue. Drawing: %s Next: %s" % (
            self.drawing, self.draw_next is None))

        if self.drawing:
            return
        if not self.draw_next:
            return
        self.drawing = True
        draw = self.draw_next
        d = threads.deferToThread(self.draw_and_delay, draw['func'],
                                  draw['params'])
        d.addCallback(self.finish_drawing)
        self.draw_next = None

    def draw_and_delay(self, func, args):
        print_fancy_blue("enter draw thread")
        func(*args)
        print_fancy_blue("leaving draw thread")

    def finish_drawing(self, result):
        print_fancy_blue("finish queue op")
        self.drawing = False
        self.draw_from_queue()

    ###########################################################################

    def _draw_qr_to_image(draw, bolt11):
        start = time.time()
        qd = QRDraw(bolt11)
        print("render QR: %0.4f" % (time.time() - start))
        start = time.time()
        x_offset, y_offset, scale = qd.place_inside_box(0, 0, EPD_HEIGHT)
        print("x: %d, y: %d, scale: %s" % (x_offset, y_offset, scale))
        for color, x1, y1, x2, y2 in qd.iter_draw_params(x_offset, y_offset,
                                                         scale):
            if color == BLACK:
                draw.rectangle((x1, y1, x2, y2), fill=BLACK)
        print("draw boxes: %0.4f" % (time.time() - start))

    def _draw_text_to_image(draw, line1, line2, line3):
        font = ImageFont.truetype(FONT, 16)
        font_big = ImageFont.truetype(FONT, 20)
        #print("1: %s 2: %s 3: %s" % (line1, line2, line3))
        line1 = str(line1) if line1 else "(none)"
        line2 = str(line2) if line2 else "(none)"
        line3 = str(line3) if line3 else "(none)"
        draw.text((3, 5), line1, font=font, fill=BLACK)
        draw.text((3, 40), line2, font=font_big, fill=BLACK)
        draw.text((3, 75), line3, font=font, fill=BLACK)

    def render_draw_qr(bolt11, satoshis, exchange_rate, exchange_rate_timestamp,
                       fiat_currency, fiat_price, timezone):
        #line1 = "Doesn't work, WIP - Jarret"
        line1 = "Babies are Dying."
        line2 = "$%.2f = %dsat" % (fiat_price, satoshis)
        dt = datetime.datetime.fromtimestamp(exchange_rate_timestamp,
                                             tz=pytz.timezone(timezone))
        time_str = dt.strftime('%H:%M:%S')
        #line3 =  "$%.2f BTC%s - %s" % (exchange_rate, fiat_currency, time_str)
        line3 = "Doesn't work, WIP - Jarret"

        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, line1, line2, line3)
        text_image = text_image.transpose(Image.ROTATE_90)

        qr_image = Image.new('1', (300, 300), WHITE)
        qr_draw = ImageDraw.Draw(qr_image)
        Eink._draw_qr_to_image(qr_draw, bolt11)

        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(qr_image, (0, 0))
        full_image.paste(text_image, (300, 0))

        Eink._display_image(full_image)

    def draw_qr(self, bolt11, satoshis, exchange_rate,
                exchange_rate_timestamp, fiat_currency, fiat_price,
                timezone):
        self.queue_draw(Eink.render_draw_qr, bolt11, satoshis, exchange_rate,
                        exchange_rate_timestamp, fiat_currency, fiat_price,
                        timezone)
        self.draw_from_queue()

    ###########################################################################

    def draw_three_lines(line1, line2, line3):
        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, line1, line2, line3)
        text_image = text_image.transpose(Image.ROTATE_90)
        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(text_image, (180, 0))
        Eink._display_image(full_image)

    def draw_random_1(self):
        self.queue_draw(Eink.draw_three_lines, "eat", "my", "shorts")
        self.draw_from_queue()

    def draw_random_2(self):
        self.queue_draw(Eink.draw_three_lines, "your beard", "is", "weird")
        self.draw_from_queue()

    def draw_random_3(self):
        self.queue_draw(Eink.draw_three_lines, "herp", "a", "derp")
        self.draw_from_queue()

    def draw_select_drink(self):
        self.queue_draw(Eink.draw_three_lines, "select", "yer", "drink")
        self.draw_from_queue()

    def draw_error(self):
        self.queue_draw(Eink.draw_three_lines, "WTF", "Problemo", "dudez")
        self.draw_from_queue()

    ###########################################################################

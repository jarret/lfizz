# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from third_party.waveshare.epd4in2 import EPD, EPD_WIDTH, EPD_HEIGHT
import time
import os

from PIL import Image,ImageDraw,ImageFont
from qrdraw import QRDraw

WHITE = 0xff
BLACK = 0x00

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

FONT = "%s/third_party/Minecraftia.ttf" % SRC_PATH


class Eink(object):
    def __init__(self):
        self.epd = EPD()
        self.epd.init()

    def clear(self):
        self.epd.Clear(WHITE)

    def _display_image(self, image):
        start = time.time()
        print("rotate")
        rotated = image.rotate(180)
        print("rotated: %0.4f seconds" % (time.time() - start))

        start = time.time()
        b = self.epd.getbuffer(rotated)
        print("get buffer: %0.4f" % (time.time() - start))
        start = time.time()
        self.epd.display(b)
        print("display call: %0.4f" % (time.time() - start))

    def _draw_qr_to_image(self, draw, bolt11):
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

    def _draw_text_to_image(self, draw, line1, line2, line3):
        font = ImageFont.truetype(FONT, 16)
        font_big = ImageFont.truetype(FONT, 20)
        draw.text((1, 5), line1, font=font, fill=BLACK)
        draw.text((1, 40), line2, font=font_big, fill=BLACK)
        draw.text((1, 80), line3, font=font, fill=BLACK)

    def draw_qr(self, bolt11, line1, line2, line3):

        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        self._draw_text_to_image(text_draw, line1, line2, line3)
        text_image = text_image.transpose(Image.ROTATE_90)

        qr_image = Image.new('1', (300, 300), WHITE)
        qr_draw = ImageDraw.Draw(qr_image)
        self._draw_qr_to_image(qr_draw, bolt11)

        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(qr_image, (0, 0))
        full_image.paste(text_image, (300, 0))

        self._display_image(full_image)


    def output_first_boot(self):
        pass

    def output_boot_up(self, ip):
        pass

    def output_qr(self, bolt11):
        pass

    def output_select_drink(self):
        pass

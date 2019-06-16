# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from third_party.waveshare.epd4in2 import EPD, EPD_WIDTH, EPD_HEIGHT
import time
import os

from twisted.internet import threads

from PIL import Image,ImageDraw,ImageFont
from qrdraw import QRDraw

WHITE = 0xff
BLACK = 0x00

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

FONT = "%s/third_party/Minecraftia.ttf" % SRC_PATH


class Eink(object):
    INTERFACE = None

    def __init__(self, reactor):
        self.reactor = reactor
        self.drawing = False

    def clear():
        Eink.INTERFACE.Clear(WHITE)

    def _display_image(image):
        start = time.time()
        print("rotate")
        rotated = image.rotate(180)
        print("rotated: %0.4f seconds" % (time.time() - start))

        start = time.time()
        b = Eink.INTERFACE.getbuffer(rotated)
        print("get buffer: %0.4f" % (time.time() - start))
        start = time.time()
        Eink.INTERFACE.display(b)
        print("display call: %0.4f" % (time.time() - start))


    def finished_drawing(self, result):
        self.drawing = False

    ###########################################################################

    def draw_first_boot():
        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, "first boot", "finding network",
                                 "hang on, Hoss")
        text_image = text_image.transpose(Image.ROTATE_90)
        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(text_image, (180, 0))
        Eink._display_image(full_image)

    def output_first_boot(self):
        if self.drawing:
            print("still drawing")
            self.reactor.callLater(1.0, self.output_first_boot)
            return
        self.drawing = True
        d = threads.deferToThread(self.draw_first_boot)
        d.addCallback(self.finish_drawing)

    ###########################################################################

    def draw_boot_up(ip, exchange_rate, invoice):
        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, ip, exchange_rate, invoice)
        text_image = text_image.transpose(Image.ROTATE_90)
        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(text_image, (180, 0))
        Eink._display_image(full_image)

    def output_boot_up(self, ip, exchange_rate, invoice):
        if self.drawing:
            print("still drawing")
            self.reactor.callLater(1.0, self.output_boot_up, ip, exchange_rate,
                                   invoice))
            return
        self.drawing = True
        d = threads.deferToThread(self.draw_boot_up)
        d.addCallback(self.finish_drawing)

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
        draw.text((1, 5), line1, font=font, fill=BLACK)
        draw.text((1, 40), line2, font=font_big, fill=BLACK)
        draw.text((1, 80), line3, font=font, fill=BLACK)

    def draw_qr(bolt11, satoshis, exchange_rate, exchange_rate_timestamp,
                fiat_currency, fiat_price, timezone):
        line1 = "Cures what ails ya!"
        line2 = "$%.2f / %dsat" % (fiat_price, satoshis)
        dt = datetime.datetime.fromtimestamp(exchange_rate_timestamp,
                                             tz=pytz.timezone(timezone))
        time_str = dt.strftime('%H:%M:%S')
        line3 =  "$%.2f BTC%s - %s" % (exchange_rate, fiat_currency, time_str)

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

    def output_qr(self, bolt11, satoshis, exchange_rate,
                  exchange_rate_timestamp, fiat_currency, fiat_price,
                  timezone):
        if self.drawing:
            print("still drawing")
            self.reactor.callLater(1.0, self.output_qr, bolt11, satoshis,
                                   exchange_rate, exchange_rate_timestamp,
                                   fiat_currency, fiat_price, timezone)
            return
        self.drawing = True
        d = threads.deferToThread(self.draw_qr, bolt11, bolt11, satoshis,
                                  exchange_rate, exchange_rate_timestamp,
                                  fiat_currency, fiat_price, timezone)
        d.addCallback(self.finish_drawing)

    ###########################################################################

    def draw_select_drink():
        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, "select", "yer", "drink")
        text_image = text_image.transpose(Image.ROTATE_90)
        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(text_image, (180, 0))
        Eink._display_image(full_image)

    def output_select_drink(self):
        if self.drawing:
            print("still drawing")
            self.reactor.callLater(1.0, self.output_select_drink)
            return
        self.drawing = True
        d = threads.deferToThread(self.draw_select_drink)
        d.addCallback(self.finish_drawing)

    ###########################################################################

    def draw_error():
        text_image = Image.new('1', (300, 100), WHITE)
        text_draw = ImageDraw.Draw(text_image)
        Eink._draw_text_to_image(text_draw, "WTF", "problemo", "dude")
        text_image = text_image.transpose(Image.ROTATE_90)
        full_image = Image.new('1', (400, 300), WHITE)
        full_image.paste(text_image, (180, 0))
        Eink._display_image(full_image)

    def output_error(self):
        if self.drawing:
            print("still drawing")
            self.reactor.callLater(1.0, self.output_error)
            return
        self.drawing = True
        d = threads.deferToThread(self.draw_error)
        d.addCallback(self.finish_drawing)


Eink.INTERFACE = EPD()
Eink.INTERFACE.init()

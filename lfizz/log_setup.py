# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import gzip
import logging
import logging.handlers

class GZipRotator(object):
    def __call__(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)

def setup_logging(filename, console_silent=False):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        os.makedirs(d)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                       datefmt='%m-%d %H:%M:%S')
    console_handler.setFormatter(console_format)

    #logfile_handler = logging.FileHandler(filename)
    #logfile_handler.setLevel(logging.DEBUG)
    logfile_handler = logging.handlers.TimedRotatingFileHandler(filename,
                                                                'midnight')
    logfile_handler.setLevel(logging.INFO)
    logfile_format = logging.Formatter(
        '%(asctime)s %(filename)s:%(lineno)d %(levelname)s: %(message)s')
    logfile_handler.setFormatter(logfile_format)
    logfile_handler.rotator = GZipRotator()

    handlers = ([logfile_handler] if console_silent else
                 [console_handler, logfile_handler])
    logging.basicConfig(handlers=handlers, level=logging.DEBUG)

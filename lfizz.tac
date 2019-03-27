# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys
import os

path = os.path.dirname(os.path.realpath(__file__))
print(path)
sys.path.insert(0, path)
from lfizz.lfizz import LFizz


lf = LFizz()
lf.run()

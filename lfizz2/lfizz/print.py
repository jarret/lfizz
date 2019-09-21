# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

###############################################################################
# print helpers
###############################################################################
CHILL_WHITE = '\x1b[0;37;40m'
CHILL_PURPLE = '\x1b[0;35;40m'
CHILL_LIGHT_BLUE = '\x1b[0;36;40m'
CHILL_BLUE = '\x1b[0;34;40m'

MEGA_WHITE = '\x1b[1;37;40m'
LIGHT_BLUE = '\x1b[1;36;40m'
BLUE = '\x1b[1;34;40m'
GREEN = '\x1b[1;32;40m'
CHILL_GREEN = '\x1b[0;32;40m'
RED = '\x1b[1;31;40m'
YELLOW = '\x1b[1;33;40m'
CHILL_YELLOW = '\x1b[0;33;40m'
FANCY_BLUE = '\x1b[1;37;44m'
ANNOYING =   '\x1b[5;31;44m'
ENDC = '\x1b[0m'

def print_red(string):
    print(RED + string + ENDC)

def print_green(string):
    print(GREEN + string + ENDC)

def print_chill_green(string):
    print(CHILL_GREEN + string + ENDC)

def print_light_blue(string):
    print(LIGHT_BLUE + string + ENDC)

def print_fancy_blue(string):
    print(FANCY_BLUE + string + ENDC)

def print_blue(string):
    print(BLUE + string + ENDC)

def print_yellow(string):
    print(YELLOW + string + ENDC)

def print_chill_yellow(string):
    print(CHILL_YELLOW + string + ENDC)

def print_chill_white(string):
    print(CHILL_WHITE + string + ENDC)

def print_chill_purple(string):
    print(CHILL_PURPLE + string + ENDC)

def print_chill_light_blue(string):
    print(CHILL_LIGHT_BLUE + string + ENDC)

def print_chill_blue(string):
    print(CHILL_BLUE + string + ENDC)

def print_mega_white(string):
    print(MEGA_WHITE + string + ENDC)

def print_annoying(string):
    print(ANNOYING + string + ENDC)

##################################################################

def red_str(string):
    return RED + string + ENDC

def chill_green_str(string):
    return CHILL_GREEN + string + ENDC

def chill_yellow_str(string):
    return CHILL_YELLOW + string + ENDC

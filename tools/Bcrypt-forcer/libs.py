#!/usr/bin/python3
# nu11secur1ty 2022
from colorama import init, Fore, Back, Style
init(convert=True)
import requests

def pingo(iteration,
          total,
          prefix='',
          suffix='',
          decimals=1,
          length=100,
          fill='█'):
    """
    Print
    """
    length = length - (len(prefix) + len(suffix) + 10)
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total)))
    fillLength = int(length * iteration // total)
    bar = fill * fillLength + '-' * (length - fillLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    if iteration == total:
        print()

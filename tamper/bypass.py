#!/usr/bin/env python

"""
Copyright (c) 2006-2023 nu11secur1ty (https://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""
import re
from lib.core.data import kb
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Injects bypass login

    Requirement:
        * MySQL

    >>> tamper('nu11secur1ty' or 1=1#')
    """

    retVal = payload

    if payload:
        retVal = re.sub('\\bAND\\b', '&&', retVal)
        retVal = re.sub('\\bOR\\b', '||', retVal)

    return retVal


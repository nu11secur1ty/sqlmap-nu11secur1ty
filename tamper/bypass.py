#!/usr/bin/env python

"""
Copyright (c) 2006-2023 nu11secur1ty (https://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

from lib.core.enums import PRIORITY
import re
__priority__ = PRIORITY.NORMAL
def dependencies():
    pass
def tamper(payload, **kwargs):
"""
Replace OR and AND keywords with || and &&
>>> tamper('nu11secur1ty' or 1=1#)
' || nu11secur1ty' or 1=1#
"""
    retVal = ""
    retVal = re.sub('\\bOR\\b', '||', payload)
    retVal = re.sub('\\bAND\\b', '&&', retVal)
    return retVal

#!/usr/bin/env python

"""
Copyright (c) 2006-2023 nu11secur1ty (https://sqlmap.org/, https://www.nu11secur1ty.com/)
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
>>> tamper(' or 1=1#)
' || or 1=1#
"""
    retVal = ""
    retVal = re.sub('\\bOR\\b', '||', payload)
    retVal = re.sub('\\bAND\\b', '&&', retVal)
    return retVal

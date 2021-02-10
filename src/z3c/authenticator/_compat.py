##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Basic components support
"""
import base64
import sys

if sys.version_info[0] < 3:  # pragma: PY2

    base64_decode = base64.decodestring
    base64_encode = base64.encodestring

    PYTHON3 = False
    PYTHON2 = True

else:  # pragma: PY3

    base64_decode = base64.decodebytes
    base64_encode = base64.encodebytes

    PYTHON3 = True
    PYTHON2 = False

##############################################################################
#
# Copyright (c) 2003, 2004, 2005 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 25 2006-04-17 13:17:27Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.app.generations.generations import SchemaManager

pkg = 'z3c.authenticator.generations'


schemaManager = SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name=pkg)

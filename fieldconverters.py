"""Zope-specific request field converters.

$Id: fieldconverters.py,v 1.1 2003/02/13 17:46:19 tseaver Exp $
"""
from datetime import datetime

from zope.publisher.browser import registerTypeConverter
from zope.app.datetimeutils import parse as parseDateTime

def field2date_via_datetimeutils(v):
    """Converter for request fields marshalled as ':date'.

    o XXX:  Uses the non-localized and non-tzinfo-aware 'parseDateTime'
            utility from zope.app.datetimeutils;  a better alternative
            would be more I18N / L10N aware, perhaps even adapting to
            the expressed preferences of the user.
    """
    if hasattr(v,'read'):
        v = v.read()
    else:
        v = str(v)

    # *Don't* force a timezone if not passed explicitly;  leave it as
    # "naive" datetime.
    year, month, day, hour, minute, second, tzname = parseDateTime(v, local=0)

    # TODO:  look up a real tzinfo object using 'tzname'
    #
    # Option 1:  Use 'timezones' module as global registry::
    #
    #   from zope.app.timezones import getTimezoneInfo
    #   tzinfo = getTimezoneInfo(tzname)
    #
    # Option 2:  Use a utility (or perhaps a view, for L10N).
    #
    #   tz_lookup = getUtility(None, ITimezoneLookup)
    #   tzinfo = tz_lookup(tzname)
    #
    return datetime(year, month, day, hour, minute, second,
                  # tzinfo=tzinfo
                   )

ZOPE_CONVERTERS = [('date', field2date_via_datetimeutils)]

def registerZopeConverters():

    for field_type, converter in ZOPE_CONVERTERS:
        registerTypeConverter(field_type, converter)

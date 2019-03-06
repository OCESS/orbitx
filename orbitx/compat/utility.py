"""A few helper functions for serverv-py.

Surprisingly, there aren't common functions to convert
from QBasic times to Python datetimes.
"""
from datetime import datetime, date
from collections import namedtuple


def qb_time_to_datetime(year, yday, hour, minute, doublesecond):
    """Convert a QB-format time to a datetime."""
    date_fromordinal = date.fromordinal(
        date(year, 1, 1).toordinal() + yday - 1)
    return datetime(
        year=year,
        month=date_fromordinal.month,
        day=date_fromordinal.day,
        hour=hour,
        minute=minute,
        second=int(doublesecond),
        microsecond=int(doublesecond % 1 * 1000000)
        # No tzinfo because this datetime is really beta-reality time.
    )


RGB = namedtuple('RGB', ['r', 'g', 'b'])


def colour_code_to_rgb(code):
    """Convert a QB colour code to an RGB tuple."""
    # These specific RGB values are actually xterm defaults for RGB mappings
    # from ANSI colour codes. They should be pretty close.
    if code == 0:  # Black
        # Foreground colours
        return RGB(0, 0, 0)
    elif code == 1:  # Blue
        return RGB(0, 0, 0xff)
    elif code == 2:  # Green
        return RGB(0, 0xff, 0)
    elif code == 3:  # Cyan
        return RGB(0, 0xff, 0xff)
    elif code == 4:  # Red
        return RGB(0xff, 0, 0)
    elif code == 5:  # Purple
        return RGB(0xff, 0, 0xff)
    elif code == 6:  # Brown/Orange
        return RGB(0xff, 0xff, 0)
    elif code == 7:  # Light Gray (White)
        return RGB(0xff, 0xff, 0xff)
    elif code == 8:  # Dark Gray (Light Black)
        # Background colours
        return RGB(0x4d, 0x4d, 0x4d)
    elif code == 9:  # Light Blue
        return RGB(0, 0, 0xcd)
    elif code == 10:  # Light Green
        return RGB(0, 0xcd, 0)
    elif code == 11:  # Light Cyan
        return RGB(0, 0xcd, 0xcd)
    elif code == 12:  # Light Red
        return RGB(0xcd, 0, 0)
    elif code == 13:  # Light Purple
        return RGB(0xcd, 0, 0xcd)
    elif code == 14:  # Yellow (Light Orange)
        return RGB(0xcd, 0xcd, 0)
    elif code == 15:  # White (Light White)
        return RGB(0xe5, 0xe5, 0xe5)
    raise ValueError('Read invalid QB colour code from STARSr file!')

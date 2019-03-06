"""Functions that copy file io functionality of serverv.bas.

As a recap, this entire program tries to keep communication consistent
between legacy (i.e. file-based IPC between QBasic programs written by Dr.
Magwood) and Ivan's new node.js-based project.

This module is the legacy file-based IPC functionality.
"""
from os import SEEK_SET
import struct  # Reading floats from bytearrays
from datetime import timedelta
import time

from orbitx.compat import utility


def _mki(integer):
    return integer.to_bytes(2, byteorder='little')


def _cvi(twobytes):
    return int.from_bytes(twobytes, byteorder='little')


def _mks(single):
    return struct.pack("<f", single)


def _cvs(fourbytes):
    return struct.unpack("<f", fourbytes)[0]


def _mkd(double):
    return struct.pack("<d", double)


def _cvd(eightbytes):
    return struct.unpack("<d", eightbytes)[0]


def simulator_orb5res_parse(src, file_vars):
    """Block 300."""
    if file_vars.setdefault('RCload', 0) != 0:
        src.seek(255, SEEK_SET)
        file_vars['Rt'] = _cvi(src.read(2)) + int(file_vars['RCload'] * 4)


def simulator_orb5res_transform(file_contents, file_vars):
    """Block 320."""
    if file_vars.setdefault('RCload', 0) != 0:
        file_contents[255:257] = _mki(file_vars.setdefault('Rt', 0))
    if file_vars.setdefault('FCenable', 0) == 0:
        file_contents[293:295] = _mki(3)


def HABeecom_gastelemetry_parse(src, file_vars):
    """Block 400."""
    src.seek(323, SEEK_SET)
    file_vars['PROBEflag'] = _cvs(src.read(4))
    src.seek(251, SEEK_SET)
    file_vars['RCload'] = _cvs(src.read(4))
    src.seek(399, SEEK_SET)
    file_vars['O2a1'] = _cvs(src.read(4))
    file_vars['O2a2'] = _cvs(src.read(4))
    src.seek(415, SEEK_SET)
    file_vars['O2b1'] = _cvs(src.read(4))
    file_vars['O2b2'] = _cvs(src.read(4))
    # Note we're doing float/int equality. I dunno man, I just copy serverv.bas
    if file_vars['O2a1'] > 0 and file_vars['O2a2'] == 1:
        file_vars['FCenable'] = 1
    if file_vars['O2b1'] > 0 and file_vars['O2b2'] == 1:
        file_vars['FCenable'] = 1


def HABeecom_gastelemetry_transform(file_contents, file_vars):
    """Block 420."""
    pass


def MCeecom_gasmc_parse(src, file_vars):
    """Block 500."""
    pass


def MCeecom_gasmc_transform(file_contents, file_vars):
    """Block 510 - 520."""
    pass


def SIMeecom_gassim_parse(src, file_vars):
    """Block 600."""
    pass


def SIMeecom_gassim_transform(file_contents, file_vars):
    """Block 610."""
    pass


def SIMeecom_doorsim_parse(src, file_vars):
    """Block 700."""
    pass


def SIMeecom_doorsim_transform(file_contents, file_vars):
    """Block 710."""
    file_contents[267:269] = _mki(file_vars.setdefault('PACKblock', 0))
    file_contents[269:271] = _mki(file_vars.setdefault('RCblock', 0))
    file_contents[271:275] = _mks(file_vars.setdefault('IS2', 0.0))


def HABeng_orbitsse_parse(src, file_vars):
    """Block 810."""
    src.seek(230, SEEK_SET)
    file_vars['EL6'] = _cvs(src.read(4))
    src.seek(278, SEEK_SET)
    file_vars['switch1'] = _cvi(src.read(2))
    src.seek(210, SEEK_SET)
    file_vars['EL1'] = _cvs(src.read(4))
    file_vars['IS2'] = _cvs(src.read(4))
    src.seek(688, SEEK_SET)
    file_vars['PBflag'] = _cvs(src.read(4))
    file_vars['RCblock'] = 1
    if (file_vars['EL6'] > 9000 and
        file_vars['switch1'] == 1 and
            file_vars['EL1'] > 10):
        file_vars['RCblock'] = 0
    file_vars['PACKblock'] = 1
    if file_vars['PBflag'] == 9:
        file_vars['PACKblock'] = 0


def HABeng_orbitsse_transform(file_contents, file_vars):
    """Also Block 810. No reset logic here."""
    if file_vars.setdefault('probe', 0) == 0:
        file_contents[129:137] = _mkd(0)
    if file_vars['probe'] == 1:
        file_contents[129:137] = _mkd(1)
        file_contents[137:145] = _mkd(28)
    if file_vars['probe'] == 2:
        file_contents[129:137] = _mkd(2)


def display_mst_parse(src, file_vars):
    """Block 900."""
    pass


def display_mst_transform(file_contents, file_vars):
    """Until Block 940."""
    pass


def MCeecom_time_parse(src, file_vars):
    """Block 930. Also a bit of time logic."""
    if file_vars.setdefault('use_file_time', True):
        src.seek(1, SEEK_SET)
        file_vars['timestamp'] = utility.qb_time_to_datetime(
            _cvi(src.read(2)), _cvi(src.read(2)), _cvi(src.read(2)),
            _cvi(src.read(2)), _cvd(src.read(8)))
    else:
        file_vars['last_time_update'] = time.perf_counter()
        file_vars['timestamp'] = (
            file_vars['timestamp'] +
            timedelta(seconds=time.perf_counter() -
                      file_vars['last_time_update'])
        )


def MCeecom_time_transform(file_contents, file_vars):
    """Also block 930."""
    file_vars['chkBYTE'] = file_vars.setdefault('chkBYTE', 0) + 1
    if file_vars['chkBYTE'] > 58:
        file_vars['chkBYTE'] = 1
    dt = file_vars['timestamp']
    file_contents[0:1] = [file_vars['chkBYTE']]
    file_contents[1:3] = _mki(dt.year)
    file_contents[3:5] = _mki(dt.timetuple().tm_yday)
    file_contents[5:7] = _mki(dt.hour)
    file_contents[7:9] = _mki(dt.minute)
    file_contents[9:17] = _mkd(dt.second + dt.microsecond / 1000000)
    file_contents[17:25] = b' ' * 8
    file_contents[25:26] = [file_vars['chkBYTE']]


# TODO: implement OSbackup.RND
# TODO: implement XXXXXXX reset

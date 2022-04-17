"""Sets up the Python logging subsytem, accessible by logging.getLogger().

When OrbitX first launches and this module is initialized, there will be two
handlers.
 - print_handler will print WARNING and higher log messages to stderr
 - startup_handler will write all log messages to logs/debug-startup.log

If you want to print all log messages to stderr, instead of just WARNING and
higher, call enable_verbose_logging().

Once you know which OrbitX program is running (lead, mirror, compat, etc.),
call make_program_logfile(program_name). This will stop the logger writing to
logs/debug-startup.log, make logs/debug-{program_name}.log, and mirror all
messages in debug-startup.log into the new logfile.

This is done because we assume there can be at most one copy of each OrbitX
program running on the same machine, but two different OrbitX programs running
on the same machine. So if 'lead' and 'mirror' are both running, they should
have unique logfiles.
"""

import logging
from pathlib import Path
from typing import List

# This should be updated whenever the on-disk file we're logging to changes.
logfile_name: str = ''

LOGDIR = Path('logs')

debug_formatter = logging.Formatter(
    '{asctime} {levelname}\t{module}.{funcName}: {message}',
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)

print_formatter = logging.Formatter(
    '{levelname} {module}.{funcName}:\t{message}',
    datefmt='%X',  # The timestamp is just the time of day
    style='{'
)


class LogdirFileHandler(logging.FileHandler):
    """Puts a FileHandler in the logging directory."""

    def __init__(self, program_name: str,
                 mode='w', encoding=None, delay=False):
        """Just takes the name of a program, e.g. 'mirror'."""
        # Thanks to https://stackoverflow.com/a/20667049.
        LOGDIR.mkdir(exist_ok=True)
        logging.FileHandler.__init__(
            self, str(LOGDIR / f'debug-{program_name}.log'),
            mode, encoding, delay)


class StartupHandler(LogdirFileHandler):
    """The same as a LogdirFileHandler, but also saves LogRecords so that we
    can mirror them into a future logfile once we haev a unique logfile name.
    """

    def __init__(self):
        self.record_buffer: List[logging.LogRecord] = []
        LogdirFileHandler.__init__(self, 'startup')

    def handle(self, record):
        self.record_buffer.append(record)
        LogdirFileHandler.handle(self, record)


# Set up the logger.
# Log WARNING and higher to stderr.
# Log INFO and higher to the logfile (initially the startup logfile).
logging.getLogger('orbitx').setLevel(logging.DEBUG)
logging.captureWarnings(True)

print_handler = logging.StreamHandler()
print_handler.setLevel(logging.WARNING)
print_handler.setFormatter(print_formatter)

startup_handler = StartupHandler()
startup_handler.setLevel(logging.DEBUG)
startup_handler.setFormatter(debug_formatter)
logfile_name = startup_handler.baseFilename

logging.getLogger('orbitx').handlers = []
logging.getLogger('orbitx').addHandler(print_handler)
logging.getLogger('orbitx').addHandler(startup_handler)


def make_program_logfile(program_name: str):
    """Starts logging INFO messages to program-specific logfile."""
    # mode='w' implies that we discard any pre-existing contents of this file.
    global logfile_name
    logfile_handler = LogdirFileHandler(program_name, delay=True)
    logfile_handler.setLevel(logging.INFO)
    logfile_handler.setFormatter(debug_formatter)

    logging.getLogger('orbitx').info(
        f'Switching logfiles to {logfile_handler.baseFilename}.')
    logging.getLogger('orbitx').addHandler(logfile_handler)
    for record in startup_handler.record_buffer:
        logfile_handler.emit(record)
    logfile_name = logfile_handler.baseFilename
    logging.getLogger('orbitx').info('Startup complete.')

    # startup_handler will now no longer be used by the logging subsystem.
    startup_handler.close()


def enable_verbose_logging():
    """Enables logging of all messages to stdout, from INFO upwards"""
    print_handler.setLevel(logging.DEBUG)  # We'll print any debug messages and higher.
    logging.getLogger().setLevel(logging.DEBUG)

"""Common code and class interfaces."""
import os.path

DEFAULT_CNC_ADDRESS = 'localhost'
DEFAULT_PORT = 28430

def savefile(name):
    return os.path.join(SAVE_DIRECTORY, name)
SAVE_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'data', 'saves')
AUTOSAVE_SAVEFILE = savefile('autosave.json')
SOLAR_SYSTEM_SAVEFILE = savefile('OCESS.json')

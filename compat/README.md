note, this orbitx/compat directory is basically a copy-paste of
https://github.com/OCESS/serverv-py
If this message is still in this README.md, this code hasn't been fully
changed to match the new orbitx structure. Read the rest of this file with this
in mind.

# What is this?

This project is a rewrite of OCESS' server program in the
kind-of distributed client-server model that is Spacesim's
collective QuickBasic infrastructure. To maintain some
backwards compatibility, but not restrict ourselves to
old software, this Python server will be able to mediate
the existing legacy communication and also use modern
communication e.g. communication with a `node.js` server.

Since the legacy logic of this server has been mostly cloned
from the legacy server (`serverv.bas`), there will be a bit
of code smell so be aware. It should mostly be contained.

For the legacy server, see the `notes` directory. My chicken
scratchings of understanding the legacy code are also in there.

### Setup:

    git clone https://github.com/OCESS/serverv-py
    # After installing pip (use the Python installer on Windows)
    pip3 install virtualenv
    virutalenv -p python3 serverv-py
    cd serverv-py
    source bin/activate # On Linux
    Scripts\activate # On Windows
    pip install -r requirements.txt

### Usage:

    # source bin/activate if you haven't done so in the current session
    # flags optional, default values are shown as an example
    ./serverv-py/server.py --sevpath orbit-files/sevpath.RND --piloting 127.0.0.1:31415

### Testing:

    # Will run server.py for a few seconds, then exit.
    # Also checks that no .RND files were changed after running,
    # and spins up a very basic server to receive network messages.
    ./test.bash

If you're on Windows I don't have a testing script yet. To make sure everything works, just
run `test_scripts/super_basic_echo.py` and then `serverv-py/server.py`.

### Source files:

There are a few sources in `serverv-py/serverv-py`. The most important is
`server.py`, which contains the main event loop and calls other modules.

- `server.py`: Actually runs everything asynchronously.
- `filetransforms.py`: Generalized helper logic for copying files between legacy
  QB clients.
- `qb_communication.py`: Actually does the copying of files between
  legacy QB clients
- `piloting_state.py`: Reads and keeps track of the piloting state, i.e.
  `STARSr` data file.
- `utility.py`: A few common helper functions used by different modules.

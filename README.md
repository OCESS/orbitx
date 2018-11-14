# OrbitX

This project re-implements the central server and astronaut flight software for
Dr. Magwood's
['Orbit' suite of software](http://www.wiki.spacesim.org/index.php/Orbit)
written for OCESS.

This project is maintained by
- Ye Qin
- Sean
- Patrick

As part of CS493 and CS494, a final year project course at Waterloo.

## Project Setup

It's recommended you develop and run in a virtualenv. Setup is as follows:

```
git clone https://github.com/OCESS/orbitx
cd orbitx
python3 -m venv venv # or however you can create a python3 virtualenv
source ven/bin/activate
pip install --upgrade pip # not required, but a good idea
cd src
make install # installs packages in requirements.txt, make sure you've activated your venv!
```

If you're on windows, replace `source venv/bin/activate` with
`Scripts\Activate.bat` on `cmd`, or `Scripts\Activate.ps1` if you know you're
running powershell.

And when you want to restart development, just do:

```
cd orbitx
source venv/bin/activate
```

## Building

This project is mostly python, which does not require you to build a new binary
after making changes to `.py` files. However, making changes to the
`orbitx.proto` file requires building your changes. The file `src/Makefile` will
let you do the following commands in `src/`:

```
make build    # run this when you make a change to orbitx.proto
make install  # run this once, to set up this project
make format   # run this to automatically format code
```

## Running

`src/flight.py` Is an executable python scripts. Run `src/flight.py --help` for
help on running the program. The sparknotes version is, run:

```
src/flight.py --flight-gui
``` 

If you get errors, make sure you have the pip packages in `requirements.txt`
installed. If you followed the setup instructions, this is as easy as running
`source bin/activate`.

## Contributing!!

Hey spacesim member, or other GitHub user!! Thank you for even considering this
section!

If you're a simmer, and you want to make a code change, feel free to get in
touch with me (Patrick) by emailing me/messaging me somehow. I can help you
design or test your code change. If you have a code change ready to go, feel
free to make a pull request to this repo and I'll look over it and merge it.

The goals of this project are:
- Being readable and maintainable, making contributing as easy as possible,
- To be scientifically accurate, so that we can really just simulate space,
- To have feature parity with Dr. Magwood's legacy orbit, but until then,
- To be able to operate side-by-side with Dr. Magwood's legacy orbit!

So if you have some code that roughly fits this, feel free to drop me a line!

## Project Structure

```
src/: All python source files. Most of these are self-contained modules.
src/flight.py: Flight server or mirroring client. Run with ./flight.py
src/orbitx-demo.ipynb: Jupyter notebook that can be run and viewed remotely

doc/: Any documentation for this project
doc/orbitsource: Source code for relevant components of legacy Orbit
doc/\*-prototypes/: Prototypes for various components

data/: Data that does not fit in src/, e.g. save files
data/saves/tests/: Save files for testing, used by src/test.py
```

## Controls

Simulation Controls:
```
'p' : pause and continue the simulation
'l' : show and hide the labels of the planets
```

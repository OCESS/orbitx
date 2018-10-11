# cs493 [title WIP]

This project re-implements the central server and astronaut flight software for
Dr. Magwood's
['Orbit' suite of software](http://www.wiki.spacesim.org/index.php/Orbit)
written for OCESS.

This project is maintained by
- Ye Qin
- Sean
- Patrick

As part of CS493 and CS494, a final year project course at Waterloo.

## Building

It's recommended you develop and run in a virtualenv. Setup is as follows:

```
git clone https://github.com/OCESS/cs493
python3 -m venv cs493
cd cs493
source bin/activate
pip install -r requirements.txt
```

and when you want to restart development:

```
cd cs493
source bin/activate
```

This project is mostly python, so no building required. However, there is a
Makefile in `src/` to generate python code from the protobuf file. Run `make`
in the `src/` directory to generate these definitions.

## Running

Both `src/cnc.py` and `src/flight.py` are executable python scripts. Invoke them
with `--help` for usage.

Make sure you have the pip packages in `requirements.txt` installed. If you
followed the setup instructions, this is as easy as running
`source bin/activate`.

## Project Structure [WIP]

```
src/: All python source files
src/cnc.py: Main CnC server. Run with ./cnc.py
src/flight.py: Flight client. Run with ./flight.py

doc/: Any documentation for this project
doc/orbitsource: Source code for relevant components of legacy Orbit
doc/network-prototypes/: Prototype networking experiments

data/: Data that does not fit in src/, e.g. save files

test/: Unit and integration tests
```

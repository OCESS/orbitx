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

## Project Structure [WIP]

```
src/
src/common: Common functionality and libraries
src/cnc: The "Command and Control" server (it's just a fun name that's not "server")
src/flight: The GUI by which astronauts pilot the habitat. Networked to the cnc server

doc/: Any documentation for this project
doc/orbitsource: Source code for relevant components of legacy Orbit

data/: Data that does not fit in src/, e.g. save files

test/: Unit and integration tests
```

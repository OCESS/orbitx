# OrbitX

![The Jupiter system, showing Io, Europa, Ganymede, and Callisto orbiting Jupiter](https://user-images.githubusercontent.com/1498589/49043539-60230c00-f199-11e8-90d4-4e9553c6c14f.png)

This project re-implements the central server and astronaut flight software for
Dr. Magwood's
['Orbit' suite of software](http://www.wiki.spacesim.org/index.php/Orbit)
written for OCESS.

For a guide on if and how you should contribute, read `CONTRIBUTING.md`  
For a guide on how to set up your text editor to edit code, read `DEVELOPING.md`  
For a guide on how the actual OrbitX codebase is structured, read `ARCHITECTURE.md`

This project is maintained by
- Patrick
- Stefan De Young

As part of CS493 and CS494, a final year project course at Waterloo.

Furthermore, OCESS and UWaterloo CS494 members have contribued:
- Ye Qin
- Sean
- Stefano DeYoung
- Cesare Corazza
- Jamie Tait
- Jonah Hamer-Wilson
- Calum Wheaton

## First Time Contributors

If you're a first-time contributor to OrbitX, take a look at `CONTRIBUTING.md`,
especially if you don't recognize the `git clone` command in the Project Setup
section. The `CONTRIBUTING.md` has helpful tips for first-time contributors.

## Project Setup

If you run into any issues during setup, feel free to email me,
patrick.melanstone on gmail. For step-by-step explanations of these
instructions, read `CONTRIBUTING.md`.

It's recommended you develop and run in a virtualenv. Setup is as follows:

First, fork your own copy of `orbitx` on GitHub (you'll need a GitHub account
for this). See below for windows-specific changes. Then,
```
git clone https://github.com/your-github-username/orbitx
cd orbitx
python3 -m venv venv # or however you can create a python3 virtualenv
source venv/bin/activate
pip install --upgrade pip # not required, but a good idea
cd orbitx
make install # installs packages in requirements.txt, make sure you've activated your venv!
```

If you're on windows, replace `source venv/bin/activate` with
`Scripts\Activate.bat` on `cmd`, or `Scripts\Activate.ps1` if you know you're
running powershell. Also you'll have to just run the make commands manually, by running `cat Makefile` and copying the command you want.

If you get an error referencing "Microsoft Visual C++ Build Tools", especially when
installing `yappi`, install [the build tools](https://www.scivision.dev/python-windows-visual-c-14-required/)
(choose Windows 10 SDK and C++ x64/x86 build tools in the installer).

And when you want to restart development, just do:

```
cd orbitx
source venv/bin/activate
```

## Building

This project is mostly python, which does not require you to build a new binary
after making changes to `.py` files. However, making changes to the
`orbitx.proto` file requires building your changes. The file `orbitx/Makefile` will
let you do the following commands in `orbitx/`:

```
make build    # run this when you make a change to orbitx.proto
make install  # run this once, to set up this project
make format   # run this to automatically format code
```

## Running

`orbitx.py` Is an executable python script. Run `python orbitx.py --help` for
the CLI args, or just run `python orbitx.py` for a graphical launcher.

If you get errors, make sure you have the pip packages in `requirements.txt`
installed. If the setup instructions completed without errors, this is as easy
as running `source bin/activate`.

## Project Structure

Read `ARCHITECTURE.md` for a description of OrbitX's architecture.

## Screens

![The most recent iteration of the OrbitX GUI](https://user-images.githubusercontent.com/1498589/58850124-1d1b8700-865b-11e9-8be6-4f0013b11a2a.png)

![The entire solar system, with circle segments showing the paths of planets](https://user-images.githubusercontent.com/1498589/48948260-e1f90800-ef01-11e8-9835-f5f472604720.PNG)

![The Jupiter system, with sinusoidal paths of Jovian moons around Jupiter](https://user-images.githubusercontent.com/1498589/48948270-ea514300-ef01-11e8-8f23-4010e6fb7bd3.PNG)

![The Jupiter system, showing Io, Europa, Ganymede, and Callisto orbiting Jupiter](https://user-images.githubusercontent.com/1498589/49043539-60230c00-f199-11e8-90d4-4e9553c6c14f.png)

![A representation of the new habitat design](https://user-images.githubusercontent.com/1498589/51934439-96674c80-23d1-11e9-98a0-9a0213eef2ea.png)

# Contributing to OrbitX

Read this guide if you're interested in becoming a contributor to OrbitX!

For a guide on how to install and run OrbitX, read `README.md`  
For a guide on how to set up your text editor to edit code, read `DEVELOPING.md`  
For a guide on how the actual OrbitX codebase is structured, read `ARCHITECTURE.md`

## Can I Contribute To OrbitX?

If you're reading this, then thank you! New contributors to OrbitX,
especially Spacesim members, are essential to the health of OrbitX.

The code for OrbitX has specifically been written to be easy for you, yes you,
to modify! Whether you're a grade 12 in ICS, an alumn who is bored, or a
grade 9 who is never going to take an ICS class! _You_ can modify the very code
that OrbitX runs on.

However, if this is your first coding project that you're considering working
on, you'll probably learn more if you have someone who has some more experience
programming, especially when making changes larger than dozens of lines. Ask
one of the Commanders, they should be happy to find someone to help you! And
if there's nobody available, you can always find me (Patrick Melanson) on
gmail (patrick.melanstone) or on FB or on pretty much any form of messaging.
I always love to talk about OrbitX with spacesimmers!

## Setting Up Your Environment

This section will guide you through making a small change, just so you can see
what the process is like. If this is one of your first times contributing, it's
expected that the instructions in this section will take some time. These steps
are very similar for contributing to many open-source projects, especially the
steps relating to `git`, so you're learning very commonly-used commands here.

Don't worry if it's overwhelming at first! Feel free to ask someone to work on
this with you.

### Setting Up Git

Second, we'll fork a copy of the `orbitx` repository and clone it. To learn how
to do this and what this means, feel free to read
[this excellent workshop on `git`](https://github.com/fboxwala/intro-git-py-workshop/wiki).

To guide you through that workshop,

- read
[Part 1: Intro to Git](https://github.com/fboxwala/intro-git-py-workshop/wiki/Part-1%3A-Intro-to-Git)
if you want to find out what this 'Git' thing is, and how it relates to GitHub.

- read the installation instructions for your platform (Windows, Mac, or Linux)
to be able to run `git` commands.

- read
[Part 2: Setup your Repository](https://github.com/fboxwala/intro-git-py-workshop/wiki/Part-2:-Setup-your-Repository)
to fork your own personal copy of the `orbitx` repository. Except when that
page says "click the *Fork* button in the top right hand corner of this page," you
should instead click the *Fork* button in the top right hand corner of the
[OrbitX](https://github.com/OCESS/orbitx) repository page. Also, replace any
URLs that end with '`/intro-git-py-workshop.git`' with '`/orbitx.git`', and
replace '`/fboxwala/intro-git-py-workshop.git`' with '`/OCESS/orbitx.git`'.

Congratulations! You've forked and cloned your own copy of `orbitx`.

### Setting Up Your Editor

Feel free to skip this if you already have a working Python development
environment, but you may want to read `DEVELOPING.md` if you skip this.

First, install [Python 3](https://www.python.org/downloads/), adding it to your
PATH variable if it asks.

Then, install the Community edition of
[PyCharm](https://www.jetbrains.com/pycharm/download/), which is a good
text editor/IDE for first-time contributors. It is good at editing Python code
and automatically gives some basic feedback on your code. Since OrbitX is
almost entirely Python code, this will be your main text editor.

Once PyCharm is installed, open it up, find the `orbitx` folder you cloned
in the last section, and open that folder up as a project in PyCharm. Then,
add a virtual environment to contain your install Python packages by doing the
following:

1. Open File > Settings > Project: orbitx > Project Interpreter

2. Next to the "Project Interpreter" dropdown, click the gear icon > click Add

3. Select Virtualenv environment > New environment, and click OK

4. When PyCharm prompts you to Install requirements, install them.

You can achieve the same thing via command line, but it's more finnicky.

### Generating Protobuf Files

One final step: generate protobuf files. This step has to be done once when
setting up your project, and every time you edit `orbitx.proto` (which won't
be often).

In PyCharm, click "Terminal" at the bottom of the PyCharm window and make sure the
text "`(venv)`" appears at the beginning of the command line that pops up (if
not, something went wrong in the previous virtual environment step).

Then, run the following command (copy-pasted from `orbitx/Makefile`):

```
cd orbitx
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. orbitx.proto
```

### You're done!

At this point, you can change whatever you want in OrbitX! If you want your
changes to be accepted into OrbitX, you should read the next section to make
your first change. But if you don't care, feel free to just start editing!

To run OrbitX, use the Run menu in PyCharm's top bar.

### Making Your First Change

Remember that Git workshop a few sections ago? Read
[Part 3: Development](https://github.com/fboxwala/intro-git-py-workshop/wiki/Part-3:-Development)
to find out how to make a branch, make edits on it, and push your code.

When it asks you to look at an issue, take a look at
[issue #71](https://github.com/OCESS/orbitx/issues/71) in OrbitX, and reference
that issue.

Once you're done, congratulations! You've pushed real code! You've learnt all
you can from this guide, and now you know how to contribute to this project
and also most other open-source projects in the world.

## Getting Your Changed Merged

Now that you know how to send changes to be merged into OrbitX, it's time to
make one of these changes!

If you're considering a small change, totally feel free to push code and I'll
probably merge it as-is.

If it's a larger change, try to get in touch with me before you make your
change! I might have some ideas on how to make your code easier to write, or
it might fit into some work that I'm doing that I haven't pushed yet.

But overall, your changes will get merged in some form if you push them. OrbitX
is always looking for new contributors!

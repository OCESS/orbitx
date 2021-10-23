# OrbitX Development Environment Guide

Read this guide for recommendations on how to set up a development environment
for OrbitX. As long as you can edit the .py files and OrbitX runs, that's
ultimately the only thing that matters. This guide will hopefully make editing
the source code easier for you.

Feel free to ignore any and all of these recommendations!

For a guide on if and how you should contribute, read `CONTRIBUTING.md`  
For a guide on how to install and run OrbitX, read `README.md`  
For a guide on how the actual OrbitX codebase is structured, read `ARCHITECTURE.md`

## Quickstart

If you don't want to put much thought into setting up your environment and just
want to start writing code, use [PyCharm](https://www.jetbrains.com/pycharm/)!
It will do everything mentioned in this guide, (formatting your code, doing
type-checking) automatically!

*Recommendation*: use PyCharm, and you don't need to do any more setup!

That's it! If you're using PyCharm, feel free to stop reading this guide. Just
listen to PyCharm when it says your code is formatted weird, and start
tinkering with OrbitX!

---

If you already have a preferred editor that you're more comfortable with, this
guide continues with recommendations for how to set up your editor and workflow
to make your life easier.

*Advanced Recommendation*: if you already have a preferred editor, keep reading

## Text Editor

There are plenty of ways to edit code out there! As long as you can edit a text
file, you can edit OrbitX's codebase! Even Windows Notepad will work, but that
is painful to use.

In general, your editing workflow will go like this:

1. Edit a `.py` file somehow
2. (Optional) use the tools described in this guide to check your code
3. Run `python orbitx.py` and see if your changes worked
4. (Optional) Run `python test.py` and see if everything still works

Importantly, use whatever text editor you feel comfortable with for step 1!

I've been using Sublime and have had good experiences with it, especially by
installing plugins (e.g. autopep8, pretty json). But use whatever!

## Code Style

The standard coding style for Python is
[PEP 8](https://www.python.org/dev/peps/pep-0008/). It has a lot of good style
recommendations, essentially this will make your code look professional,
especially because OrbitX's codebase is in PEP 8.

But you don't have to read the entire document, since lots of people have made
programs to automatically format your code according to PEP 8. Specific
examples are are autopep8, pylint, Anaconda's autoformatter, maybe even yapf.
But if you're using a text editor or IDE that has a convenient plugin, use
that.

*Recommendation*: use an automatic python PEP 8 formatter.

You can use the `format` target in the `Makefile` to format the code. If you
don't have Makefiles set up, you can just copy-paste the `python -m autopep8`
command in `Makefile` and get the same effect.

## Type Annotations

Usually, in Python you don't have to say what the type of a function parameter
is. For example, you can write:

    def altitude(entityA, entityB)

but it's not clear how to call this. Should you pass in two strings, and expect
a number? Or pass in two Entity objects? Who knows! But Python 3 allows:

    def altitude(entityA: Entity, entityB: Entity) -> float:

Now we know that `altitude` expects two `Entity` objects, and returns a number
like `3.6`. Even better, there are tools that will automatically warn you if
you try to pass in something of a different type. Just like a statically-typed
language, like the C you learn in ICS class!

When working on the OrbitX codebase, using type-checkers will help catch bugs!
Adding these type annotations to new code will also make the codebase easier
to maintain.

*Recommendation*: Use `mypy` to type-check your code

*Recommendation*: Add type annotations to new code you write

`mypy` is the standard type-checker for Python. If you have an IDE with
Python support, it will likely have a `mypy` plugin (Sublime Text and PyCharm
both have one). `mypy` also comes as a command-line tool.

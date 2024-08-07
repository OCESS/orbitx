Powergrid background
====================

Hello! You may be here looking for how to edit the powergrid background.

You may notice there's a .drawio file and a .drawio.png in here. They're
both generated by the same tool, draw.io. Here's how to edit it!

1. Open up your old web browser and point it to https://app.diagrams.net
1. Select the GitHub storage option, and hit Open Existing Diagram
1. Browse on over to OCESS/orbitx/[your branch name]/data/engineering/orbitx-powergrid.drawio
1. Make edits! (Make sure that any component names match up with component
names in strings.py, that's how the tkinter GUI code knows where to place
component widgets)

And here's how to save your changes (you basically make a commit):

1. Once you're done editing, click the save changes button
1. It'll pop up a "Commit Message" box, fill in an appropriate commit message.
You've now saved the .drawio file! This is what orbitx will use to correctly
place tkinter widgets. Next, we'll save the .drawio.png file, which is what
orbitx will use to render the actual background!
1. Click File > Export > PNG, and save it to
OCESS/orbitx/[your branch name]/data/engineering/orbitx-powergrid.drawio.png
1. Add a commit message, e.g. "updating png to [do the same thing you wrote
about in your .drawio commit message]"
1. Done!
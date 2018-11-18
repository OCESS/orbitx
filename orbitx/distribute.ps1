$ErrorActionPreference = "Stop"

$VPY_DIR_SCRIPT=@'
# I'm sorry this script is necessary. Can be its own file if cleaner.
import importlib
import os

vpython_spec = importlib.util.find_spec('vpython')
assert vpython_spec.has_location
print(os.path.dirname(vpython_spec.origin))
'@

# Have to make sure the orbitx_pb2_grpc.py patch is applied.
python __init__.py

# Workaround for vpython/vpython_libraries/glow.min.js not being included:
$VPY_DIR = python -c "$VPY_DIR_SCRIPT"

# Use pyinstaller to make an executable in dist/
pyinstaller `
	--noconfirm `
	../flight.py `
	-n orbitx `
	'--add-data' '../data;data' `
	'--add-data' "$VPY_DIR;vpython" `
	'--add-data' "$VPY_DIR/vpython_data;vpython/vpython_data"

# Fix up some pyinstaller hijinks
cd dist\orbitx\vpython
cmd /c mklink /d vpython_librariesc vpython_libraries
cmd /c mklink /d vpython_datac vpython_data
cd vpython_libraries
cmd /c mklink glow.min.jsc glow.min.js
cmd /c mklink glowcomm.htmlc glowcomm.html

# Package it into a zip file
cd ..\..\..
Compress-Archive -Force -Path orbitx -DestinationPath orbitx

cd ..
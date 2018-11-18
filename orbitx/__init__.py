"""Patch up orbitx_pb2_grpc.py import errors.

See https://github.com/protocolbuffers/protobuf/issues/1491
for some background. But basically if you're trying to run
`import orbitx.orbitx_pb2_grpc`
orbitx_pb2_grpc.py will try to effectively import `orbitx.orbitx.orbitx_pb2`.
Replacing `import orbitx_pb2` with `from . import orbitx_pb2` fixes this.

This is very hacky and black-magic, sorry.
"""

import sys
from pathlib import Path

target_file = Path(__file__).resolve().parent / 'orbitx_pb2_grpc.py'

if not hasattr(sys, 'frozen'):
    # Made sure we're not in a frozen binary, like a distributed .exe file.
    # If this file doesn't exist, we must be running as orbitx.exe.
    assert target_file.is_file()
    with open(target_file, 'r') as grpc_py:
        replaced_file = grpc_py.read().replace(
            '\nimport orbitx_pb2', '\nfrom . import orbitx_pb2')

    with open(target_file, 'w') as grpc_py:
        grpc_py.write(replaced_file)

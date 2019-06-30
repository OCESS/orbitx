"""
This modules in this subpackage implement the different OrbitX programs.
Each submodule implements a common.Program.

- programs.compat implements a compatibility server with OrbitV,
    reading OrbitV binary files and sending network updates to OrbitX
- programs.lead implements the lead server, which simulates the physical flight
    state and sends out updates to anyone who cares
- programs.mirror implements the mirror server, which by default follows a lead
    server in a read-only mode. It can stop getting network updates and
    continue physical simulation by itself.
"""

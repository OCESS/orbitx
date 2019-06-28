"""
This modules in this subpackage implement the different OrbitX variants.
Each submodule contains:
- a main(args) function that will run a while-True loop and block.
- an argument_parser with any variant-specific CLI arguments.

- variants.compat implements a compatibility server with OrbitV,
    reading OrbitV binary files and sending network updates to OrbitX
- variants.lead implements the lead server, which simulates the physical flight
    state and sends out updates to anyone who cares
- variants.mirror implements the mirror server, which by default follows a lead
    server in a read-only mode. It can stop getting network updates and
    continue physical simulation by itself.
"""

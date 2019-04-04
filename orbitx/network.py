"""Network-related classes."""

import logging
import threading
import queue
from typing import List, Union

import grpc

from orbitx import orbitx_pb2 as protos
from orbitx import orbitx_pb2_grpc as grpc_stubs

log = logging.getLogger()


# This Request class is just an alias of the Command protobuf message. We
# provide this so that nobody has to directly import orbitx_pb2, and so that
# we can this wrapper class in the future.
Request = protos.Command


class StateServer(grpc_stubs.StateServerServicer):
    """
    Service for sending state to clients.

    Usage: A client will call "get_physical_state", which will fire off a
    request to this server. The self.get_physical_state method will return a
    value and that value will be sent over the network to the client, and
    the client's call of "get_physical_state" will return whatever value we
    produce here.

    Make sure to call self.notify_state_change when there's a physical state
    change, e.g. when a physics step is simulated.

    Magic!
    """

    def __init__(self):
        self._class_used_properly = False
        self._internal_state_lock = threading.Lock()
        self._commands = queue.Queue()

    def notify_state_change(self, physical_state_copy: protos.PhysicalState):
        # This flag is to make sure this class is set up and being used
        # properly. When changing this code, consider that multithreading is
        # hard. This StateServer will be in a different thread than the main
        # thread of whatever is using this GRPC server.
        # So REMEMBER: the argument should not be modified by the main thread!
        # an easy way to ensure this is by passing in a copy.deepcopy.
        with self._internal_state_lock:
            self._internal_state_copy = physical_state_copy
            self._class_used_properly = True

    def get_physical_state(
            self, request: protos.Command, context) -> protos.PhysicalState:
        """Server-side implementation of this remote procedure call (RPC).

        This is called by GRPC, and the name of the function is special (it's
        referenced in orbitx.proto, under service StateServer)"""
        if request.ident != protos.Command.NOOP:
            self._commands.put(request)
        with self._internal_state_lock:
            assert self._class_used_properly
            return self._internal_state_copy

    def pop_commands(self) -> List[protos.Command]:
        """Returns all commands that have been sent to this server.

        Calling this method again immediately will likely return nothing."""
        commands: List[protos.Command] = []
        try:
            while True:
                commands.append(self._commands.get_nowait())
        except queue.Empty:
            pass
        return commands


class StateClient:
    """
    Context manager for networking.

    Should return a function that evaluates to the state of the entities.
    This will let us change the implementation of this class without changing
    calling code.

    Usage:
        with StateClient('localhost', 28430) as physical_state_getter:
            while True:
                physical_state = physical_state_getter()
    """

    def __init__(self, cnc_address, cnc_port):
        self.cnc_location = f'{cnc_address}:{cnc_port}'

    def _get_physical_state(
            self, command: protos.Command = None) -> protos.PhysicalState:
        if command is None:
            command = protos.Command(ident=protos.Command.NOOP)
        return self.stub.get_physical_state(command)

    def __enter__(self):
        self.channel = grpc.insecure_channel(self.cnc_location)
        self.stub = grpc_stubs.StateServerStub(self.channel)
        return self._get_physical_state

    def __exit__(self, *args):
        self.channel.close()

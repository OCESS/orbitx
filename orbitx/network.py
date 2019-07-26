"""Network-related classes."""

import logging
import threading
import queue
from typing import List, Iterable

import grpc

from orbitx import common
from orbitx import state
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
        with self._internal_state_lock:
            self._internal_state_copy = physical_state_copy
            self._class_used_properly = True

    def get_physical_state(
        self, request_iterator: Iterable[protos.Command], context) \
            -> protos.PhysicalState:
        """Server-side implementation of this remote procedure call (RPC).

        This is called by GRPC, and the name of the function is special (it's
        referenced in orbitx.proto, under service StateServer)"""
        for request in request_iterator:
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
    Allows clients to easily communicate to the Physics Server.

    Usage:
        connection = StateClient('localhost')
        while True:
            physics_state = connection.get_state()
    """

    def __init__(self, hostname: str):
        self.channel = grpc.insecure_channel(
            f'{hostname}:{common.DEFAULT_PORT}')
        self.stub = grpc_stubs.StateServerStub(self.channel)

    def get_state(self, commands: List[Request] = None) \
            -> state.PhysicsState:
        if commands is None:
            commands_iter = iter([Request(ident=protos.Command.NOOP)])
        else:
            commands_iter = iter(commands)
        return state.PhysicsState(None,
                                  self.stub.get_physical_state(commands_iter))

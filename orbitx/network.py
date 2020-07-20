"""Network-related classes."""

import logging
import threading
import time
import queue
from types import SimpleNamespace
from typing import Dict, List, Optional, Iterable

import grpc

from orbitx import common
from orbitx import physics
from orbitx import orbitx_pb2 as protos
from orbitx import orbitx_pb2_grpc as grpc_stubs
from orbitx.data_structures import PhysicsState, Request

log = logging.getLogger()

DEFAULT_PORT = 28430


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

    # Keep this in sync with the ClientType definition in orbitx.proto.
    CLIENT_TYPE_TO_STR = [
        'Invalid client',
        'MC Flight',
        'Habitat Flight',
        'OrbitV Compatibility Server',
        'MIST',
        'Hab Engineering'
    ]

    def __init__(self):
        self._class_used_properly = False
        self._internal_state_lock = threading.Lock()
        self._commands = queue.Queue()
        self.addr_to_connected_clients: Dict[str, SimpleNamespace] = {}

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
        client_type: Optional[protos.Command.ClientType] = None
        for request in request_iterator:
            if client_type is None:
                client_type = request.client
            else:
                assert client_type == request.client

            if request.ident != protos.Command.NOOP:
                self._commands.put(request)
        assert client_type is not None

        if context.peer() not in self.addr_to_connected_clients:
            self.addr_to_connected_clients[context.peer()] = \
                SimpleNamespace(
                    client_type=self.CLIENT_TYPE_TO_STR[client_type],
                    client_addr=context.peer()
                )

        self.addr_to_connected_clients[context.peer()].last_contact = \
            time.monotonic()

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

    def refresh_client_list(self):
        self.addr_to_connected_clients.clear()


class NetworkedStateClient:
    """
    Allows clients to easily communicate to the Physics Server.

    Usage:
        connection = NetworkedStateClient('localhost')
        while True:
            physics_state = connection.get_state()
    """

    def __init__(self, client: protos.Command.ClientType, hostname: str):
        self.channel = grpc.insecure_channel(
            f'{hostname}:{DEFAULT_PORT}')
        self.stub = grpc_stubs.StateServerStub(self.channel)
        self.client_type = client

        initial_state = PhysicsState(None, self.stub.get_physical_state(iter([
                Request(ident=Request.NOOP, client=self.client_type)])))

        self._caching_physics_engine = physics.PhysicsEngine(initial_state)
        self._time_of_next_network_update = 0.0

    def get_state(self, commands: List[Request] = None) \
            -> PhysicsState:

        current_time = time.monotonic()
        commands_to_send = False

        if commands is None or len(commands) == 0:
            commands_iter = iter([
                Request(ident=Request.NOOP, client=self.client_type)])
        else:
            for command in commands:
                command.client = self.client_type
            commands_iter = iter(commands)
            commands_to_send = True

        returned_state: PhysicsState

        if commands_to_send or current_time > self._time_of_next_network_update:
            # We need to make a network request.
            # TODO: what if this fails? Do anything smarter than an exception?
            returned_state = PhysicsState(
                None, self.stub.get_physical_state(commands_iter))
            self._caching_physics_engine.set_state(returned_state)

            if commands_to_send:
                # If we sent a user command, still ask for an update soon so
                # the user input can be reflected in hab flight's GUI as soon
                # as possible.
                # Magic number alert! The constant we add should be enough that
                # the physics server has had enough time to simulate the effect
                # of our input, but we should minimize the constant to minimize
                # input lag.
                self._time_of_next_network_update = current_time + 0.15
            else:
                self._time_of_next_network_update = (
                        current_time + common.TIME_BETWEEN_NETWORK_UPDATES
                )

        else:
            returned_state = self._caching_physics_engine.get_state()

        return returned_state

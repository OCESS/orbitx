"""Network-related classes."""

import logging
import threading

import grpc

import orbitx_pb2 as protos
import orbitx_pb2_grpc as grpc_stubs

log = logging.getLogger()


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

    def notify_state_change(self, physical_state_copy):
        # This flag is to make sure this class is set up and being used
        # properly. When changing this code, consider that multithreading is
        # hard. This StateServer will be in a different thread than the main
        # thread of whatever is using this GRPC server.
        # So REMEMBER: the argument should not be modified by the main thread!
        # an easy way to ensure this is by passing in a copy.deepcopy.
        with self._internal_state_lock:
            self._internal_state_copy = physical_state_copy
            self._class_used_properly = True

    def get_physical_state(self, request, context):
        """Server-side implementation of this remote procedure call (RPC)."""
        with self._internal_state_lock:
            assert self._class_used_properly
            return self._internal_state_copy


class StateClient:
    """
    Context manager for networking.

    Should return a function that evaluates to the state of the entities.
    This will let us change the implementation of this class without changing
    calling code.

    Usage:
        with Networking('localhost', 28430) as physical_state_getter:
            while True:
                sleep(1)
                physical_state = physical_state_getter()
    """

    def __init__(self, cnc_address, cnc_port):
        self.cnc_location = f'{cnc_address}:{cnc_port}'

    def _get_physical_state(self):
        return self.stub.get_physical_state(
            protos.ClientId(ident=protos.ClientId.MIRRORING_CLIENT))

    def __enter__(self):
        self.channel = grpc.insecure_channel(self.cnc_location)
        self.stub = grpc_stubs.StateServerStub(self.channel)
        return self._get_physical_state

    def __exit__(self, *args):
        self.channel.close()

"""Provides PhysicsState, a wrapping class for a PhysicalState and y-vector."""

from typing import List, Dict, Optional, Union

import numpy as np

from . import orbitx_pb2 as protos
from . import common
from .physics_entity import PhysicsEntity


class PhysicsState:
    """The physical state of the system for use in solve_ivp and elsewhere.

    Example usage:
    y = PhysicsState(physical_state, y_1d)

    entity = y[0]
    y['Habitat'] = habitat
    scipy.solve_ivp(y.y0())

    See help(PhysicsState.__init__) for how to initialize. Basically, the `y`
    param should be None at the very start of the program, but for the program
    to have good performance, PhysicsState.__init__ should have both parameters
    filled if it's being called more than once a second while OrbitX is running
    normally.
    """

    # For if an entity is not attached to anything
    NO_INDEX: int = -1

    # Number of different kinds of variables in the internal y vector. The
    # internal y vector has length N_COMPONENTS * len(proto_state.entities).
    # For example, if the y-vector contained just x, y, vx, and vy, then
    # N_COMPONENTS would be 4.
    N_COMPONENTS: int = 10

    # Datatype of internal y-vector
    DTYPE = np.longdouble

    def __init__(self,
                 y: Optional[np.ndarray],
                 proto_state: protos.PhysicalState):
        """Collects data from proto_state and y, when y is not None.

        There are two kinds of values we care about:
        1) values that change during simulation (like position, velocity, etc)
        2) values that do not change (like mass, radius, name, etc)

        If both proto_state and y are given, 1) is taken from y and
        2) is taken from proto_state. This is a very quick operation.

        If y is None, both 1) and 2) are taken from proto_state, and a new
        y vector is generated. This is a somewhat expensive operation."""
        assert isinstance(proto_state, protos.PhysicalState)
        assert isinstance(y, np.ndarray) or y is None

        # self._proto_state will have positions, velocities, etc for all
        # entities. DO NOT USE THESE they will be stale. Use the accessors of
        # this class instead!
        self._proto_state = proto_state
        self._n = len(proto_state.entities)

        if y is None:
            # PROTO: if you're changing protobufs remember to change here
            X = np.array([entity.x for entity in proto_state.entities])
            Y = np.array([entity.y for entity in proto_state.entities])
            VX = np.array([entity.vx for entity in proto_state.entities])
            VY = np.array([entity.vy for entity in proto_state.entities])
            Heading = np.array([
                entity.heading for entity in proto_state.entities])
            Spin = np.array([entity.spin for entity in proto_state.entities])
            Fuel = np.array([entity.fuel for entity in proto_state.entities])
            Throttle = np.array([
                entity.throttle for entity in proto_state.entities])
            np.clip(Throttle, common.MIN_THROTTLE, common.MAX_THROTTLE,
                    out=Throttle)

            # Internally translate string names to indices, otherwise
            # our entire y vector will turn into a string vector oh no.
            # Note this will be converted to floats, not integer indices.
            AttachedTo = np.array([
                self._name_to_index(entity.attached_to)
                for entity in proto_state.entities
            ])

            Broken = np.array([
                entity.broken for entity in proto_state.entities
            ])

            self._y0: np.ndarray = np.concatenate((
                X, Y, VX, VY, Heading, Spin,
                Fuel, Throttle, AttachedTo, Broken
            ), axis=0).astype(self.DTYPE)
        else:
            self._y0: np.ndarray = y.astype(self.DTYPE)

        assert len(self._y0.shape) == 1, f'y is not 1D: {self._y0.shape()}'
        assert self._y0.size % self.N_COMPONENTS == 0
        assert self._y0.size // self.N_COMPONENTS == \
            len(proto_state.entities), \
            f'{self._y0.size} != {len(proto_state.entities)}'
        self._n = len(self._y0) // self.N_COMPONENTS

    def _y_entities(self) -> np.ndarray:
        """Internal, returns an array for every entity, each with an element
        for each component."""
        return np.transpose(self._y_components())

    def _y_components(self) -> np.ndarray:
        """Internal, returns N_COMPONENT number of arrays, each with an element
        for each entity."""
        return self._y0.reshape(self.N_COMPONENTS, -1)

    def _entity_names(self) -> List[str]:
        """Returns list of names of every entity."""
        return [entity.name for entity in self._proto_state.entities]

    def _index_to_name(self, index: int) -> str:
        """Translates an index into the entity list to the right name."""
        i = int(index)
        return self._entity_names()[i] if i != self.NO_INDEX else ''

    def _name_to_index(self, name: str) -> int:
        """Finds the index of the entity with the given name."""
        return self._entity_names().index(name) if name != '' \
            else self.NO_INDEX

    def y0(self):
        """Returns a y-vector suitable as input for scipy.solve_ivp."""
        # Ensure that heading is within [0, 2pi).
        self._y_components()[4] %= (2 * np.pi)
        return self._y0

    def as_proto(self, t: float) -> protos.PhysicalState:
        """Creates a protos.PhysicalState view into internal data at time t

        Expensive. Consider one of the other accessors, which are faster."""
        self._proto_state.timestamp = t

        for entity_data, entity in zip(
                self._y_entities(),
                self._proto_state.entities):

            entity.x, entity.y, entity.vx, entity.vy, entity.heading, \
                entity.spin, entity.fuel, entity.throttle, \
                attached_index, broken = entity_data

            entity.attached_to = self._index_to_name(attached_index)
            entity.broken = bool(broken)
        return self._proto_state

    def __getitem__(self, index: Union[str, int]) -> PhysicsEntity:
        """Returns a PhysicsEntity view at a given name or index.

        Allows the following:
        physics_entity = PhysicsState[2]
        physics_entity = PhysicsState['Habitat']
        """
        if isinstance(index, str):
            # Turn a name-based index into an integer
            index = self._entity_names().index(index)
        i = int(index)

        entity = self._proto_state.entities[i]

        entity.x, entity.y, entity.vx, entity.vy, entity.heading, \
            entity.spin, entity.fuel, entity.throttle, \
            attached_index, broken = \
            self._y_entities()[i]

        entity.attached_to = self._index_to_name(attached_index)
        entity.broken = bool(broken)
        return PhysicsEntity(entity)

    def __setitem__(self, index: Union[str, int], val: PhysicsEntity):
        """Puts a PhysicsEntity at a given name or index in the state.

        Allows the following:
        PhysicsState[2] = physics_entity
        PhysicsState['Habitat'] = physics_entity
        """
        if isinstance(index, str):
            # Turn a name-based index into an integer
            index = self._entity_names().index(index)
        i = int(index)

        # Bound throttle
        val.throttle = max(common.MIN_THROTTLE, val.throttle)
        val.throttle = min(common.MAX_THROTTLE, val.throttle)

        self._proto_state.entities[i].CopyFrom(val.proto)

        attached_index = self._name_to_index(val.attached_to)

        self._y_entities()[i] = np.array([
            val.x, val.y, val.vx, val.vy, val.heading, val.spin, val.fuel,
            val.throttle, attached_index, val.broken
        ]).astype(self.DTYPE)

    @property
    def X(self):
        return self._y_components()[0]

    @property
    def Y(self):
        return self._y_components()[1]

    @property
    def VX(self):
        return self._y_components()[2]

    @property
    def VY(self):
        return self._y_components()[3]

    @property
    def Heading(self):
        return self._y_components()[4]

    @property
    def Spin(self):
        return self._y_components()[5]

    @property
    def Fuel(self):
        return self._y_components()[6]

    @property
    def Throttle(self):
        return self._y_components()[7]

    @property
    def AttachedTo(self) -> Dict[int, int]:
        """Returns a mapping from index to index of entity attachments.

        If the 0th entity is attached to the 2nd entity, 0 -> 2 will be mapped.
        """
        attach_map = {}
        for attached, attachee in enumerate(
                self._y_components()[8]):
            if int(attachee) != self.NO_INDEX:
                attach_map[attached] = int(attachee)
        return attach_map

    @property
    def Broken(self):
        return self._y_components()[9]

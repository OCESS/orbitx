"""
The main thing in this file is PhysicsState, which pretty much represents the
entire state of OrbitX. It creates Entities, it owns the EngineeringState, and
it makes your eggs and coffee too.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union

import numpy as np

from orbitx import orbitx_pb2 as protos
from orbitx import strings

from orbitx.data_structures import DTYPE
from orbitx.data_structures.engineering import EngineeringState
from orbitx.data_structures.entity import (
    Entity, _EntityView,
    _NO_INDEX, _LANDED_ON, _PER_ENTITY_MUTABLE_FIELDS, _ENTITY_FIELD_ORDER
)


log = logging.getLogger('orbitx')

# Make sure this is in sync with the corresponding enum in orbitx.proto!
Navmode = Enum('Navmode', zip([  # type: ignore
    'Manual', 'CCW Prograde', 'CW Retrograde', 'Depart Reference',
    'Approach Target', 'Pro Targ Velocity', 'Anti Targ Velocity'
], protos.Navmode.values()))


class PhysicsState:
    """The physical state of the system for use in solve_ivp and elsewhere.

    The following operations are supported:

    # Construction without a y-vector, taking all data from a PhysicalState
    PhysicsState(None, protos.PhysicalState)

    # Faster Construction from a y-vector and protos.PhysicalState
    PhysicsState(ivp_solution.y, protos.PhysicalState)

    # Access of a single Entity in the PhysicsState, by index or Entity name
    my_entity: Entity = PhysicsState[0]
    my_entity: Entity = PhysicsState['Earth']

    # Iteration over all Entitys in the PhysicsState
    for entity in my_physics_state:
        print(entity.name, entity.pos)

    # Convert back to a protos.PhysicalState (this almost never happens)
    my_physics_state.as_proto()

    Example usage:
    y = PhysicsState(y_1d, physical_state)

    entity = y[0]
    y[HABITAT] = habitat
    scipy.solve_ivp(y.y0())

    See help(PhysicsState.__init__) for how to initialize. Basically, the first
    `y` instantiated in the lifetime of the program will be created by a call to
    PhysicsState.__init__. But for the program to have good performance,
    PhysicsState.__init__ should have both parameters filled if it's being
    called more than once a second while OrbitX is running normally.
    """

    class NoEntityError(ValueError):
        """Raised when an entity is not found."""
        pass

    # The number of single-element values at the end of the y-vector.
    # Currently just SRB_TIME and TIME_ACC are appended to the end. If there
    # are more values appended to the end, increment this and follow the same
    # code for .srb_time and .time_acc
    N_SINGULAR_ELEMENTS = 2

    ENTITY_START_INDEX = 0
    ENGINEERING_START_INDEX = -(EngineeringState.N_ENGINEERING_FIELDS)
    SRB_TIME_INDEX = ENGINEERING_START_INDEX - 2
    TIME_ACC_INDEX = SRB_TIME_INDEX + 1

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
        self._proto_state = protos.PhysicalState()
        self._proto_state.CopyFrom(proto_state)
        self._n = len(proto_state.entities)

        self._entity_names = \
            [entity.name for entity in self._proto_state.entities]
        self._array_rep: np.ndarray

        if y is None:
            # We rely on having an internal array representation we can refer
            # to, so we have to build up this array representation.
            # If you modify how self._array_rep is built, change every instance
            # of how a y-vector is accessed. Search for #Y_VECTOR_CHANGESITE.
            self._array_rep = np.empty(
                len(proto_state.entities) * len(_PER_ENTITY_MUTABLE_FIELDS)
                + self.N_SINGULAR_ELEMENTS
                + EngineeringState.N_ENGINEERING_FIELDS, dtype=DTYPE)

            for field_name, field_n in _ENTITY_FIELD_ORDER.items():
                for entity_index, entity in enumerate(proto_state.entities):
                    proto_value = getattr(entity, field_name)
                    # Internally translate string names to indices, otherwise
                    # our entire y vector will turn into a string vector oh no.
                    # Note this will convert to floats, not integer indices.
                    if field_name == _LANDED_ON:
                        proto_value = self._name_to_index(proto_value)

                    self._array_rep[self._n * field_n + entity_index] = proto_value

            self._array_rep[self.SRB_TIME_INDEX] = proto_state.srb_time
            self._array_rep[self.TIME_ACC_INDEX] = proto_state.time_acc

            # It's IMPORTANT that we pass in self._array_rep, because otherwise the numpy
            # array will be copied and EngineeringState won't be modifying our numpy array.
            self.engineering = EngineeringState(
                self._array_rep[self.ENGINEERING_START_INDEX:],
                self._proto_state.engineering,
                parent_state=self,
                populate_array=True
            )
        else:
            self._array_rep = y.astype(DTYPE)
            self._proto_state.srb_time = y[self.SRB_TIME_INDEX]
            self._proto_state.time_acc = y[self.TIME_ACC_INDEX]
            self.engineering = EngineeringState(
                self._array_rep[self.ENGINEERING_START_INDEX:],
                self._proto_state.engineering,
                parent_state=self,
                populate_array=False)

        assert len(self._array_rep.shape) == 1, \
            f'y is not 1D: {self._array_rep.shape}'
        n_entities = len(proto_state.entities)
        assert self._array_rep.size == (
            n_entities * len(_PER_ENTITY_MUTABLE_FIELDS)
            + self.N_SINGULAR_ELEMENTS
            + EngineeringState.N_ENGINEERING_FIELDS
        )

        np.mod(self.Heading, 2 * np.pi, out=self.Heading)

        self._entities_with_atmospheres: Optional[List[int]] = None

    def _y_component(self, field_name: str) -> np.ndarray:
        """Returns an n-array with the value of a component for each entity."""
        return self._array_rep[
            _ENTITY_FIELD_ORDER[field_name] * self._n:
            (_ENTITY_FIELD_ORDER[field_name] + 1) * self._n
        ]

    def _index_to_name(self, index: int) -> str:
        """Translates an index into the entity list to the right name."""
        i = int(index)
        return self._entity_names[i] if i != _NO_INDEX else ''

    def _name_to_index(self, name: Optional[str]) -> int:
        """Finds the index of the entity with the given name."""
        try:
            assert name is not None
            return self._entity_names.index(name) if name != '' \
                else _NO_INDEX
        except ValueError:
            raise self.NoEntityError(f'{name} not in entity list')

    def y0(self):
        """Returns a y-vector suitable as input for scipy.solve_ivp."""
        return self._array_rep

    def as_proto(self) -> protos.PhysicalState:
        """Creates a protos.PhysicalState view into all internal data.

        Expensive. Consider one of the other accessors, which are faster.
        For example, if you want to iterate over all elements, use __iter__
        by doing:
        for entity in my_physics_state: print(entity.name)"""
        constructed_protobuf = protos.PhysicalState()
        constructed_protobuf.CopyFrom(self._proto_state)
        for entity_data, entity in zip(self, constructed_protobuf.entities):
            (
                entity.x, entity.y, entity.vx, entity.vy,
                entity.heading, entity.spin, entity.fuel,
                entity.throttle, entity.landed_on,
                entity.broken
            ) = (
                entity_data.x, entity_data.y, entity_data.vx, entity_data.vy,
                entity_data.heading, entity_data.spin, entity_data.fuel,
                entity_data.throttle, entity_data.landed_on,
                entity_data.broken
            )

        constructed_protobuf.engineering.CopyFrom(self.engineering.as_proto())

        return constructed_protobuf

    def __len__(self):
        """Implements `len(physics_state)`."""
        return self._n

    def __iter__(self):
        """Implements `for entity in physics_state:` loops."""
        for i in range(0, self._n):
            yield self.__getitem__(i)

    def __getitem__(self, index: Union[str, int]) -> Entity:
        """Returns a Entity view at a given name or index.

        Allows the following:
        entity = physics_state[2]
        entity = physics_state[HABITAT]
        entity.x = 5  # Propagates to physics_state.
        """
        if isinstance(index, str):
            # Turn a name-based index into an integer
            index = self._entity_names.index(index)
        i = int(index)

        return _EntityView(self, i)

    def __setitem__(self, index: Union[str, int], val: Entity):
        """Puts a Entity at a given name or index in the state.

        Allows the following:
        PhysicsState[2] = physics_entity
        PhysicsState[HABITAT] = physics_entity
        """
        if isinstance(val, _EntityView) and val._creator == self:
            # The _EntityView is a view into our own data, so we already have
            # the data.
            return
        if isinstance(index, str):
            # Turn a name-based index into an integer
            index = self._entity_names.index(index)
        i = int(index)

        entity = self[i]

        (
            entity.x, entity.y, entity.vx, entity.vy, entity.heading,
            entity.spin, entity.fuel, entity.throttle, entity.landed_on,
            entity.broken
        ) = (
            val.x, val.y, val.vx, val.vy, val.heading,
            val.spin, val.fuel, val.throttle, val.landed_on,
            val.broken
        )

    def __repr__(self):
        return self.as_proto().__repr__()

    def __str__(self):
        return self.as_proto().__str__()

    @property
    def timestamp(self) -> float:
        return self._proto_state.timestamp

    @timestamp.setter
    def timestamp(self, t: float):
        self._proto_state.timestamp = t

    @property
    def srb_time(self) -> float:
        return self._proto_state.srb_time

    @srb_time.setter
    def srb_time(self, val: float):
        self._proto_state.srb_time = val
        self._array_rep[self.SRB_TIME_INDEX] = val

    @property
    def parachute_deployed(self) -> bool:
        return self._proto_state.parachute_deployed

    @parachute_deployed.setter
    def parachute_deployed(self, val: bool):
        self._proto_state.parachute_deployed = val

    @property
    def X(self):
        return self._y_component('x')

    @property
    def Y(self):
        return self._y_component('y')

    @property
    def VX(self):
        return self._y_component('vx')

    @property
    def VY(self):
        return self._y_component('vy')

    @property
    def Heading(self):
        return self._y_component('heading')

    @property
    def Spin(self):
        return self._y_component('spin')

    @property
    def Fuel(self):
        return self._y_component('fuel')

    @property
    def Throttle(self):
        return self._y_component('throttle')

    @property
    def LandedOn(self) -> Dict[int, int]:
        """Returns a mapping from index to index of entity landings.

        If the 0th entity is landed on the 2nd entity, 0 -> 2 will be mapped.
        """
        landed_map = {}
        for landed, landee in enumerate(
                self._y_component('landed_on')):
            if int(landee) != _NO_INDEX:
                landed_map[landed] = int(landee)
        return landed_map

    @property
    def Broken(self):
        return self._y_component('broken')

    @property
    def Atmospheres(self) -> List[int]:
        """Returns a list of indexes of entities that have an atmosphere."""
        if self._entities_with_atmospheres is None:
            self._entities_with_atmospheres = []
            for index, entity in enumerate(self._proto_state.entities):
                if entity.atmosphere_scaling != 0 and \
                        entity.atmosphere_thickness != 0:
                    self._entities_with_atmospheres.append(index)
        return self._entities_with_atmospheres

    @property
    def time_acc(self) -> float:
        """Returns the time acceleration, e.g. 1x or 50x."""
        return self._proto_state.time_acc

    @time_acc.setter
    def time_acc(self, new_acc: float):
        self._proto_state.time_acc = new_acc
        self._array_rep[self.TIME_ACC_INDEX] = new_acc

    def craft_entity(self):
        """Convenience function, a full Entity representing the craft."""
        return self[self.craft]

    @property
    def craft(self) -> Optional[str]:
        """Returns the currently-controlled craft.
        Not actually backed by any stored field, just a calculation."""
        if strings.HABITAT not in self._entity_names and \
                strings.AYSE not in self._entity_names:
            return None
        if strings.AYSE not in self._entity_names:
            return strings.HABITAT

        hab_index = self._name_to_index(strings.HABITAT)
        ayse_index = self._name_to_index(strings.AYSE)
        if self._y_component('landed_on')[hab_index] == ayse_index:
            # Habitat is docked with AYSE, AYSE is active craft
            return strings.AYSE
        else:
            return strings.HABITAT

    def reference_entity(self):
        """Convenience function, a full Entity representing the reference."""
        return self[self._proto_state.reference]

    @property
    def reference(self) -> str:
        """Returns current reference of the physics system, shown in GUI."""
        return self._proto_state.reference

    @reference.setter
    def reference(self, name: str):
        self._proto_state.reference = name

    def target_entity(self):
        """Convenience function, a full Entity representing the target."""
        return self[self._proto_state.target]

    @property
    def target(self) -> str:
        """Returns landing/docking target, shown in GUI."""
        return self._proto_state.target

    @target.setter
    def target(self, name: str):
        self._proto_state.target = name

    @property
    def navmode(self) -> Navmode:
        return Navmode(self._proto_state.navmode)

    @navmode.setter
    def navmode(self, navmode: Navmode):
        self._proto_state.navmode = navmode.value

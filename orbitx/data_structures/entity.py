"""
A wrapper around the Entity protobuf, which represents any physical object
floating around in space.

These are usually instantiated and owned by PhysicsState (see
data_structures.space)
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import vpython

from orbitx import orbitx_pb2 as protos
from orbitx import strings
from orbitx.data_structures import DTYPE

log = logging.getLogger('orbitx')


class Entity:
    """A wrapper around protos.Entity.

    Example usage:
    assert Entity(protos.Entity(x=5)).x == 5
    assert Entity(protos.Entity(x=1, y=2)).pos == [1, 2]

    To add fields, or see what fields exists, please see orbitx.proto,
    specifically the "message Entity" declaration.
    """

    def __init__(self, entity: protos.Entity):
        self.proto = entity

    def __repr__(self):
        return self.proto.__repr__()

    def __str__(self):
        return self.proto.__str__()

    # These are filled in just below this class definition. These stubs are for
    # static type analysis with mypy.
    name: str
    x: float
    y: float
    vx: float
    vy: float
    r: float
    mass: float
    heading: float
    spin: float
    fuel: float
    throttle: float
    landed_on: str
    broken: bool
    artificial: bool
    atmosphere_thickness: float
    atmosphere_scaling: float

    def screen_pos(self, origin: 'Entity') -> vpython.vector:
        """The on-screen position of this entity, relative to the origin."""
        return vpython.vector(self.x - origin.x, self.y - origin.y, 0)

    @property
    def pos(self):
        return np.array((self.x, self.y), dtype=DTYPE, copy=True)

    @pos.setter
    def pos(self, coord):
        self.x = coord[0]
        self.y = coord[1]

    @property
    def v(self):
        return np.asarray([self.vx, self.vy])

    @v.setter
    def v(self, coord):
        self.vx = coord[0]
        self.vy = coord[1]

    @property
    def dockable(self):
        return self.name == strings.AYSE

    def landed(self) -> bool:
        """Convenient and more elegant check to see if the entity is landed."""
        return self.landed_on != ''


class _EntityView(Entity):
    """A view into a PhysicsState, very fast to create and use.
    Setting fields will update the parent PhysicsState appropriately."""

    def __init__(self, creator: PhysicsState, index: int):
        self._creator = creator
        self._index = index

    def __repr__(self):
        # This is actually a bit hacky. This line implies that orbitx_pb2
        # protobuf generated code can't tell the difference between an
        # orbitx_pb2.Entity and an _EntityView. Turns out, it can't! But
        # hopefully this assumption always holds.
        return repr(Entity(self))

    def __str__(self):
        return str(Entity(self))


# The landed_on protobuf field is special and we reference it a couple times.
# Here, we hardcode it into a python symbol, so that we don't have to type out
# the "landed_on" string literal a bunch of times and possibly make a typo.
_LANDED_ON = "landed_on"
assert _LANDED_ON in [field.name for field in protos.Entity.DESCRIPTOR.fields]

# Represents an entity that is not landed on anything.
_NO_INDEX = -1

# These entity fields do not change during simulation. Thus, we don't have to
# store them in a big 1D numpy array for use in scipy.solve_ivp.
_PER_ENTITY_UNCHANGING_FIELDS = [
    'name', 'mass', 'r', 'artificial', 'atmosphere_thickness',
    'atmosphere_scaling'
]

_PER_ENTITY_MUTABLE_FIELDS = [field.name for
                              field in protos.Entity.DESCRIPTOR.fields if
                              field.name not in _PER_ENTITY_UNCHANGING_FIELDS]
_ENTITY_FIELD_ORDER = {name: index for index, name in
                       enumerate(_PER_ENTITY_MUTABLE_FIELDS)}


# I feel like I should apologize before things get too crazy. Once you read
# the following module-level loop and ask "why _EntityView a janky subclass of
# Entity, and is implemented using janky array indexing into data owned by a
# PhysicsState?".
# My excuse is that I wanted a way to index into PhysicsState and get an Entity
# for ease of use and code. I found this to be a useful API that made physics
# code cleaner, but it was _too_ useful! The PhysicsState.__getitem__ method
# that implemented this indexing was so expensive and called so often that it
# was _half_ the runtime of OrbitX at high time accelerations! My solution to
# this performance issue was to optimize PhysicsState.__getitem__ by return
# an Entity (specifically, an _EntityView) that was very fast to instantiate
# and very fast to access.
# Hence: janky array-indexing accessors is my super-optimization! 2x speedup!
for field in protos.Entity.DESCRIPTOR.fields:
    # For every field in the underlying protobuf entity, make a
    # convenient equivalent property to allow code like the following:
    # Entity(entity).heading = 5

    def entity_fget(self, name=field.name):
        return getattr(self.proto, name)

    def entity_fset(self, val, name=field.name):
        return setattr(self.proto, name, val)

    def entity_fdel(self, name=field.name):
        return delattr(self.proto, name)

    setattr(Entity, field.name, property(
        fget=entity_fget, fset=entity_fset, fdel=entity_fdel,
        doc=f"Entity proxy of the underlying field, self.proto.{field.name}"))

    def entity_view_unchanging_fget(self, name=field.name):
        return getattr(self._creator._proto_state.entities[self._index], name)

    def entity_view_unchanging_fset(self, val, name=field.name):
        return setattr(
            self._creator._proto_state.entities[self._index], name, val)

    field_n: Optional[int]
    if field.name in _PER_ENTITY_MUTABLE_FIELDS:
        field_n = _ENTITY_FIELD_ORDER[field.name]
    else:
        field_n = None

    if field.type in [field.TYPE_FLOAT, field.TYPE_DOUBLE]:
        def entity_view_mutable_fget(self, field_n=field_n):
            return self._creator._array_rep[
                self._creator._n * field_n + self._index]

        def entity_view_mutable_fset(self, val, field_n=field_n):
            self._creator._array_rep[
                self._creator._n * field_n + self._index] = val
    elif field.type == field.TYPE_BOOL:
        # Same as if it's a float, but we have to convert float -> bool.
        def entity_view_mutable_fget(self, field_n=field_n):
            return bool(
                self._creator._array_rep[
                    self._creator._n * field_n + self._index])

        def entity_view_mutable_fset(self, val, field_n=field_n):
            self._creator._array_rep[
                self._creator._n * field_n + self._index] = val
    elif field.name == _LANDED_ON:
        # Special case, we store the index of the entity we're landed on as a
        # float, but we have to convert this to an int then the name of the
        # entity.
        def entity_view_mutable_fget(self, field_n=field_n):
            entity_index = int(
                self._creator._array_rep[
                    self._creator._n * field_n + self._index])
            if entity_index == _NO_INDEX:
                return ''
            return self._creator._entity_names[entity_index]

        def entity_view_mutable_fset(self, val, field_n=field_n):
            assert isinstance(val, str)
            self._creator._array_rep[
                self._creator._n * field_n + self._index] = \
                self._creator._name_to_index(val)
    elif field.type == field.TYPE_STRING:
        assert field.name in _PER_ENTITY_UNCHANGING_FIELDS
    else:
        raise NotImplementedError(
            "Encountered a field in the protobuf definition of Entity that "
            f"is of a type we haven't handled: {field.type}.")

    if field.name in _PER_ENTITY_UNCHANGING_FIELDS:
        # Note there is no fdel defined. The data is owned by the PhysicalState
        # so the PhysicalState should delete data on its own time.
        setattr(_EntityView, field.name, property(
            fget=entity_view_unchanging_fget,
            fset=entity_view_unchanging_fset,
            doc=f"_EntityView proxy of unchanging field {field.name}"
        ))

    else:
        assert field.name in _PER_ENTITY_MUTABLE_FIELDS
        setattr(_EntityView, field.name, property(
            fget=entity_view_mutable_fget,
            fset=entity_view_mutable_fset,
            doc=f"_EntityView proxy of mutable field {field.name}"
        ))

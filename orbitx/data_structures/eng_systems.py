"""
Contains convenience wrappers for various smaller parts of Engineering, such as
components, coolants, radiators.

See data_structures.engineering for the EngineeringState definition, which puts
all these smaller parts together.

See data_structures.__init__ for other documentation.
"""

import logging
from typing import List, NamedTuple, Optional, Union

import numpy as np

from orbitx import orbitx_pb2 as protos
from orbitx import strings

log = logging.getLogger('orbitx')

N_COMPONENTS = len(strings.COMPONENT_NAMES)
N_COOLANT_LOOPS = len(strings.COOLANT_LOOP_NAMES)
N_RADIATORS = len(strings.RADIATOR_NAMES)

_N_COMPONENT_FIELDS = len(protos.EngineeringState.Component.DESCRIPTOR.fields)
_N_COOLANT_FIELDS = len(protos.EngineeringState.CoolantLoop.DESCRIPTOR.fields)
_N_RADIATOR_FIELDS = len(protos.EngineeringState.Radiator.DESCRIPTOR.fields)


class PowerSource(NamedTuple):
    """Represents a reactor, fuel cell, or battery."""
    name: str
    internal_resistance: float


class PowerBus(NamedTuple):
    """
    Represents one of the power buses, to which components and power sources
    are connected.
    """
    nominal_voltage: float
    primary_power_source: PowerSource
    secondary_power_source: Optional[PowerSource]


class CoolantView:
    """Represents a single Coolant Loop.

    Should not be instantiated outside of EngineeringState."""

    def __init__(self, array_rep: np.ndarray, coolant_n: int):
        """Called by an EngineeringState factory.

        array_rep: an array that, starting at 0, contains all data for all coolant loops in the form
                   [temp1, temp2, temp3, primary1, primary2, primary3, secondary1, secondary2, secondary3]
        coolant_n: an index specifying which coolant loop, starting at 0.
        """
        self._array = array_rep
        self._n = coolant_n

    def name(self):
        return strings.COOLANT_LOOP_NAMES[self._n]

    @property
    def coolant_temp(self) -> float:
        return self._array[N_COOLANT_LOOPS * 0 + self._n]

    @coolant_temp.setter
    def coolant_temp(self, val: float):
        self._array[N_COOLANT_LOOPS * 0 + self._n] = val

    @property
    def primary_pump_on(self) -> bool:
        return bool(self._array[N_COOLANT_LOOPS * 1 + self._n])

    @primary_pump_on.setter
    def primary_pump_on(self, val: bool):
        self._array[N_COOLANT_LOOPS * 1 + self._n] = val

    @property
    def secondary_pump_on(self) -> bool:
        return bool(self._array[N_COOLANT_LOOPS * 2 + self._n])

    @secondary_pump_on.setter
    def secondary_pump_on(self, val: bool):
        self._array[N_COOLANT_LOOPS * 2 + self._n] = val


class ComponentView:
    """Represents a single Component.

    Should not be instantiated outside of EngineeringState."""

    def __init__(self, parent: 'EngineeringState', array_rep: np.ndarray, component_n: int):
        """Called by an EngineeringState factory.

        array_rep: an array that, starting at 0, contains all data for all components in the form
                   [connected1, connected2, ..., temp1, temp2, ... ..., coolant_ayse_n]
        component_n: an index specifying which component, starting at 0.
        """
        self._parent = parent
        self._array = array_rep
        self._n = component_n

    def name(self):
        return strings.COMPONENT_NAMES[self._n]

    @property
    def connected(self) -> bool:
        return bool(self._array[N_COMPONENTS * 0 + self._n])

    @connected.setter
    def connected(self, val: bool):
        self._array[N_COMPONENTS * 0 + self._n] = float(val)

    @property
    def capacity(self):
        return float(self._array[N_COMPONENTS * 1 + self._n])

    @capacity.setter
    def capacity(self, val: float):
        self._array[N_COMPONENTS * 1 + self._n] = float(val)

    @property
    def temperature(self) -> float:
        return self._array[N_COMPONENTS * 2 + self._n]

    @temperature.setter
    def temperature(self, val: float):
        self._array[N_COMPONENTS * 2 + self._n] = val

    @property
    def resistance(self) -> float:
        raise NotImplementedError(
            "implement this when we know where it will be used"
        )

    @property
    def voltage(self) -> float:
        raise NotImplementedError(
            "implement this when we know where it will be used"
        )

    @property
    def current(self) -> float:
        raise NotImplementedError(
            "implement this when we know where it will be used"
        )

    @property
    def coolant_hab_one(self) -> bool:
        return bool(self._array[N_COMPONENTS * 3 + self._n])

    @coolant_hab_one.setter
    def coolant_hab_one(self, val: bool):
        self._array[N_COMPONENTS * 3 + self._n] = float(val)

    @property
    def coolant_hab_two(self) -> bool:
        return bool(self._array[N_COMPONENTS * 4 + self._n])

    @coolant_hab_two.setter
    def coolant_hab_two(self, val: bool):
        self._array[N_COMPONENTS * 4 + self._n] = float(val)

    @property
    def coolant_ayse(self) -> bool:
        return bool(self._array[N_COMPONENTS * 5 + self._n])

    @coolant_ayse.setter
    def coolant_ayse(self, val: bool):
        self._array[N_COMPONENTS * 5 + self._n] = float(val)

    def connected_coolant_loops(self) -> List[CoolantView]:
        connected_loops: List[CoolantView] = []
        if self.coolant_hab_one:
            connected_loops.append(self._parent.coolant_loops[0])
        elif self.coolant_hab_two:
            connected_loops.append(self._parent.coolant_loops[1])
        elif self.coolant_ayse:
            connected_loops.append(self._parent.coolant_loops[2])
        return connected_loops


class RadiatorView:
    """Represents a single Radiator.

    Should not be instantiated outside of EngineeringState.
    """

    def __init__(self, parent: 'EngineeringState', array_rep: np.ndarray, radiator_n: int):
        """Called by an EngineeringState factory.

        parent: an EngineeringState that this RadiatorView will use to get the associated coolant loop.
        array_rep: an array that, starting at 0, contains all data for all radiators.
        radiator_n: an index specifying which component, starting at 0.
        """
        self._parent = parent
        self._array = array_rep
        self._n = radiator_n

    def name(self):
        return strings.RADIATOR_NAMES[self._n]

    def get_coolant_loop(self) -> CoolantView:
        return self._parent.coolant_loops[self.attached_to_coolant_loop - 1]

    @property
    def attached_to_coolant_loop(self) -> int:
        return int(self._array[N_RADIATORS * 0 + self._n])

    @attached_to_coolant_loop.setter
    def attached_to_coolant_loop(self, val: int):
        self._array[N_RADIATORS * 0 + self._n] = val

    @property
    def functioning(self) -> bool:
        return bool(self._array[N_RADIATORS * 1 + self._n])

    @functioning.setter
    def functioning(self, val: bool):
        self._array[N_RADIATORS * 1 + self._n] = val


class ComponentList:
    """
    Wraps the underlying component data array into something like a list.

    Accessors that operate on all components at once go here.

    The __getitem__ method lets us write code like:
        engineering.components["RCON1"].temperature = 5.2
    It returns a ComponentView instance, and we can set fields of that
    ComponentView instance to update the original data array.

    The end result should be an easy-to-use API that doesn't do anything
    unexpected!
    """

    def __init__(self, owner: 'EngineeringState'):
        self._owner = owner
        self._component_array = owner._array[owner._COMPONENT_START_INDEX:owner._COMPONENT_END_INDEX]

    def __getitem__(self, index: Union[str, int]) -> ComponentView:
        if isinstance(index, str):
            index = strings.COMPONENT_NAMES.index(index)
        if index >= N_COMPONENTS:
            raise IndexError()
        return ComponentView(self._owner, self._component_array, index)

    # Use list slicing (with strides, so there's two colons) to get a list of
    # all values of each quantity for each Component.
    # We only define this accessor for fields we use in _derive.
    def Connected(self) -> np.ndarray:
        return self._component_array[0 * N_COMPONENTS:1 * N_COMPONENTS]

    def Capacities(self) -> np.ndarray:
        return self._component_array[1 * N_COMPONENTS:2 * N_COMPONENTS]

    def Temperatures(self) -> np.ndarray:
        return self._component_array[2 * N_COMPONENTS:3 * N_COMPONENTS]

    def CoolantConnectionMatrix(self) -> np.ndarray:
        """Returns a matrix of dimensions 3xN_COMPONENTS', containing coolant
        connection status for each component/coolant loop combination."""
        list_hab_one = self._component_array[3 * N_COMPONENTS:4 * N_COMPONENTS]
        list_hab_two = self._component_array[4 * N_COMPONENTS:5 * N_COMPONENTS]
        list_ayse = self._component_array[5 * N_COMPONENTS:6 * N_COMPONENTS]
        return np.vstack((list_hab_one, list_hab_two, list_ayse))


class CoolantLoopList:
    """Allows engineering.coolant_loops[LP1] style indexing.

    See comments on ComponentList, a similar class, for more details."""

    def __init__(self, owner: 'EngineeringState'):
        self._owner = owner
        self._coolant_array = owner._array[owner._COOLANT_START_INDEX:owner._COOLANT_END_INDEX]

    def __getitem__(self, index: Union[str, int]) -> CoolantView:
        if isinstance(index, str):
            index = strings.COOLANT_LOOP_NAMES.index(index)
        if index >= N_COOLANT_LOOPS:
            raise IndexError()
        return CoolantView(self._coolant_array, index)

    # As above, list slicing with strides.
    def CoolantTemp(self) -> np.ndarray:
        return self._coolant_array[0 * N_COOLANT_LOOPS:1 * N_COOLANT_LOOPS]


class RadiatorList:
    """Allows engineering.radiators[RAD1] style indexing.

    See comments on ComponentList, a similar class, for more details."""

    def __init__(self, owner: 'EngineeringState'):
        self._owner = owner
        self._radiator_array = owner._array[owner._RADIATOR_START_INDEX:owner._RADIATOR_END_INDEX]

    def __getitem__(self, index: Union[str, int]) -> RadiatorView:
        if isinstance(index, str):
            index = strings.RADIATOR_NAMES.index(index)
        if index >= N_RADIATORS:
            raise IndexError()
        return RadiatorView(self._owner, self._radiator_array, index)

    # And as above, list slicing with strides.
    def Functioning(self) -> np.ndarray:
        return self._radiator_array[0 * N_RADIATORS:1 * N_RADIATORS]

"""
Contains all data about engineering systems in OrbitX, wrapped in the class
`EngineeringState`. This class gets instantiated by PhysicsState (see
data_structures.space).

A good chunk of the engineering complexity is handled by the relevant classes
for components, coolant loops, etc (see data_structures.eng_subsystems).
"""
from __future__ import annotations

import logging
from typing import Dict

import numpy as np

from orbitx import orbitx_pb2 as protos
from orbitx import strings
from orbitx.common import OhmicVars, N_COMPONENTS, N_COOLANT_LOOPS, N_RADIATORS
from orbitx.physics import electrofunctions, electroconstants
from orbitx.data_structures.eng_subsystems import (
    ComponentList, CoolantLoopList, RadiatorList,
    _N_COMPONENT_FIELDS, _N_COOLANT_FIELDS, _N_RADIATOR_FIELDS
)

log = logging.getLogger('orbitx')


class EngineeringState:
    """Wrapper around protos.EngineeringState.

    Access with physics_state.engineering, e.g.
        eng_state = physics_state.engineering
        eng_state.master_alarm = True
        print(eng_state.components[AUXCOM].resistance)
        eng_state.components[LOS].connected = True
        eng_state.radiators[RAD2].functioning = False
        eng_state.radiators[RAD2].get_coolant_loop().coolant_temp = 50
    """

    N_ENGINEERING_FIELDS = (
        N_COMPONENTS * _N_COMPONENT_FIELDS
        + N_COOLANT_LOOPS * _N_COOLANT_FIELDS
        + N_RADIATORS * _N_RADIATOR_FIELDS
    )

    _COMPONENT_START_INDEX = 0
    _COOLANT_START_INDEX = _COMPONENT_START_INDEX + N_COMPONENTS * _N_COMPONENT_FIELDS
    _RADIATOR_START_INDEX = _COOLANT_START_INDEX + N_COOLANT_LOOPS * _N_COOLANT_FIELDS

    _COMPONENT_END_INDEX = _COOLANT_START_INDEX
    _COOLANT_END_INDEX = _RADIATOR_START_INDEX
    _RADIATOR_END_INDEX = (_RADIATOR_START_INDEX + N_RADIATORS * _N_RADIATOR_FIELDS)

    def __init__(self,
                 array_rep: np.ndarray, proto_state: protos.EngineeringState, *,
                 parent_state: PhysicsState, populate_array: bool):
        """Called by a PhysicsState on creation.

        array_rep: a sufficiently-sized array to store all component, coolant,
                   and radiator data. EngineeringState has full control over
                   contents, starting at element 0.
        proto_state: the underlying proto we're wrapping. We keep one-off
                     variables in here (e.g. master_alarm)
        parent_state: provides a way for EngineeringState to mirror a couple
                      pieces of data from the parent, e.g. hab fuel.
        populate_array: flag that is set when we need to fill array_rep with data.
        """
        assert len(proto_state.components) == N_COMPONENTS, f"{len(proto_state.components)} != {N_COMPONENTS}"
        assert len(proto_state.coolant_loops) == N_COOLANT_LOOPS, f"{len(proto_state.coolant_loops)} != {N_COOLANT_LOOPS}"
        assert len(proto_state.radiators) == N_RADIATORS, f"{len(proto_state.radiators)} != {N_RADIATORS}"

        self._array = array_rep
        self._proto_state = proto_state
        self._parent_state = parent_state

        self.components = ComponentList(self)
        self.coolant_loops = CoolantLoopList(self)
        self.radiators = RadiatorList(self)

        if populate_array:
            # We've been asked to populate the data array.
            # The order of data in the array is of course important.
            write_marker = 0

            # Is this loop janky? I would say yes! Could this result in
            # out-of-bounds writes? I hope not!
            # This will turn the array (which is full of zeros) into:
            # [connected_1, connected_2, ..., temperature_1, temperature_2, ... ..., coolant_ayse_n] +
            # [coolant loop fields] + [radiator fields]
            for proto_list, descriptor in [
                (proto_state.components, protos.EngineeringState.Component.DESCRIPTOR),
                (proto_state.coolant_loops, protos.EngineeringState.CoolantLoop.DESCRIPTOR),
                (proto_state.radiators, protos.EngineeringState.Radiator.DESCRIPTOR),
            ]:
                for field in descriptor.fields:
                    for proto in proto_list:
                        array_rep[write_marker] = getattr(proto, field.name)
                        write_marker += 1

            assert write_marker == len(self._array), f"{write_marker} != {len(self._array)}"

    def BusElectricals(self) -> Dict[str, OhmicVars]:
        """Return Voltage, Current, Resistance, mapped to every bus name.
        
        For the voltage, current, and resistance of individual components, see
        the ComponentList subclass."""
        component_resistances = electrofunctions.component_resistances(self.components)
        active_power_sources = electrofunctions.active_power_sources(self.components)
        bus_electricals = electrofunctions.bus_electricals(component_resistances, active_power_sources)

        bus_electricals_map: Dict[str, OhmicVars] = {}

        # We assume electricals_list to be in the same order as electroconstants.POWER_BUSES,
        # i.e. hab primary is first etc.
        for bus_index, bus in enumerate(electroconstants.POWER_BUSES):
            bus_electricals_map[bus.name] = bus_electricals[bus_index]

        return bus_electricals_map

    @property
    def habitat_fuel(self):
        return self._parent_state[strings.HABITAT].fuel

    @property
    def ayse_fuel(self):
        return self._parent_state[strings.AYSE].fuel

    @property
    def master_alarm(self) -> bool:
        return self._proto_state.master_alarm

    @master_alarm.setter
    def master_alarm(self, val: bool):
        self._proto_state.master_alarm = val

    @property
    def radiation_alarm(self) -> bool:
        return self._proto_state.radiation_alarm

    @radiation_alarm.setter
    def radiation_alarm(self, val: bool):
        self._proto_state.radiation_alarm = val

    @property
    def asteroid_alarm(self) -> bool:
        return self._proto_state.asteroid_alarm

    @asteroid_alarm.setter
    def asteroid_alarm(self, val: bool):
        self._proto_state.asteroid_alarm = val

    @property
    def hab_reactor_alarm(self) -> bool:
        return self._proto_state.hab_reactor_alarm

    @hab_reactor_alarm.setter
    def hab_reactor_alarm(self, val: bool):
        self._proto_state.hab_reactor_alarm = val

    @property
    def ayse_reactor_alarm(self) -> bool:
        return self._proto_state.ayse_reactor_alarm

    @ayse_reactor_alarm.setter
    def ayse_reactor_alarm(self, val: bool):
        self._proto_state.ayse_reactor_alarm = val

    @property
    def hab_gnomes(self) -> bool:
        return self._proto_state.hab_gnomes

    @hab_gnomes.setter
    def hab_gnomes(self, val: bool):
        self._proto_state.hab_gnomes = val

    @property
    def rad_shield_percentage(self) -> int:
        return self._proto_state.rad_shield_percentage

    @rad_shield_percentage.setter
    def rad_shield_percentage(self, val: int):
        self._proto_state.rad_shield_percentage = int(val)

    def as_proto(self) -> protos.EngineeringState:
        """Returns a deep copy of this EngineeringState as a protobuf."""
        # If the ordering of component fields, change here too #Y_VECTOR_CHANGESITE
        constructed_protobuf = protos.EngineeringState()
        constructed_protobuf.CopyFrom(self._proto_state)
        for component_data, component in zip(self.components, constructed_protobuf.components):
            (
                component.connected, component.capacity,
                component.temperature, component.coolant_hab_one,
                component.coolant_hab_two, component.coolant_ayse
            ) = (
                component_data.connected, component_data.capacity,
                component_data.temperature, component_data.coolant_hab_one,
                component_data.coolant_hab_two, component_data.coolant_ayse
            )
        for coolant_data, coolant in zip(self.coolant_loops, constructed_protobuf.coolant_loops):
            (
                coolant.coolant_temp, coolant.primary_pump_on,
                coolant.secondary_pump_on
            ) = (
                coolant_data.coolant_temp, coolant_data.primary_pump_on,
                coolant_data.secondary_pump_on
            )
        for radiator_data, radiator in zip(self.radiators, constructed_protobuf.radiators):
            (
                radiator.attached_to_coolant_loop, radiator.functioning,
            ) = (
                radiator_data.attached_to_coolant_loop, radiator_data.functioning,
            )
        return constructed_protobuf

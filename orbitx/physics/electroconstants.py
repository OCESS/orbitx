""""
Hard-coded per-component physical and thermal constants.
I'm allowed to hard code data because I've already hard-coded the number of and
name of engineering components, and they're not going to reasonably change
per-savefile.

Some values imported from Dr. Magwood's OBIT5SEJ.txt.

YOLO.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Union, Final

import numpy as np

from orbitx import strings
from orbitx.common import N_COMPONENTS

# https://en.wikipedia.org/wiki/Temperature_coefficient
# Heat gain due to component inefficiency. Units are 1/K.
# If a component increases in temperature by 1 Kelvin, its resistance will change by [1*alpha] Ohms.
# Copper has a roughly 0.0039 alpha coefficient.
ALPHA_RESIST_GAIN: Final = 0.004

# Thermal inefficiency-related constant.
# With this constant, applying 1 Watt of power results in 0.0001 Kelvin/second of heating.
COEFF_TEMPERATURE_GAIN: Final = 0.0001

# Upper bound of how quickly a component can heat up (so the battery doesn't explode).
MAX_HEATING_RATE: Final = 20.

# https://en.wikipedia.org/wiki/Thermal_conduction#Fourier's_law
# Water has a k coefficient of 0.6 to 0.7. Better conductors have higher k-values.
K_CONDUCTIVITY: Final = 0.75

# The resistance, in Ohms, of a component when its temperature field is 0 and
# it's at 100% capacity.
# Used to calculate the resistance of a component at any temperature:
# R(temp) = BASE_RESISTANCE * (1 + common.ALPHA_RESIST_GAIN * temp)
# This array is populated later in this module, but for now the default value is 1 Ohm.
BASE_COMPONENT_RESISTANCES: Final = np.ones(N_COMPONENTS)


class VoltageConverter(NamedTuple):
    """Represents a DC-DC converter between two buses.
    For example, the AYSE-Habitat converter would have input_bus = AYSE_BUS,
    and would act similarly to a PowerSource."""
    name: str
    input_bus: PowerBus
    scale_factor: float  # input voltage * scale_factor = output voltage.


class PowerSource(NamedTuple):
    """Represents a reactor, fuel cell, or battery."""
    name: str
    internal_resistance: float


class PowerBus(NamedTuple):
    """
    Represents one of the power buses, to which components and power sources
    are connected."""
    name: str
    nominal_voltage: float
    # Ordered list; the *first* power source will be used to power this bus.
    power_sources: List[Union[PowerSource, VoltageConverter]]


AYSE_BUS: Final = PowerBus(
    name=strings.AYSE_BUS,
    nominal_voltage=100_000,
    power_sources=[
        PowerSource(name=strings.AYSE_REACT, internal_resistance=0.00003),
        PowerSource(name=strings.AYSE_BAT, internal_resistance=0.0055)
    ]
)

# Define some electrical buses and sources as nice structured NamedTuples,
# and then make a matrix/array copy of the same data for more efficient math.
HAB_PRIMARY_BUS: Final = PowerBus(
    name=strings.BUS1,
    nominal_voltage=10_000,
    power_sources=[
        VoltageConverter(
            name=strings.AYSE_CONV, input_bus=AYSE_BUS, scale_factor=10_000 / AYSE_BUS.nominal_voltage),
        PowerSource(name=strings.HAB_REACT, internal_resistance=0.00025),
    ]
)

HAB_SECONDARY_BUS: Final = PowerBus(
    name=strings.BUS2,
    nominal_voltage=120,
    power_sources=[
        VoltageConverter(
            name=strings.HAB_CONV, input_bus=HAB_PRIMARY_BUS, scale_factor=120 / HAB_PRIMARY_BUS.nominal_voltage),
        PowerSource(name=strings.FCELL, internal_resistance=0.00325),
        PowerSource(name=strings.BAT1, internal_resistance=0.01),
        PowerSource(name=strings.BAT2, internal_resistance=0.01)
    ]
)

# Collects the power buses together.
# Note: If bus A can be powered by a voltage converter attached to bus B, bus A must come before bus B
# (e.g., the Habitat power bus comes before the AYSE power bus).
POWER_BUSES: List[PowerBus] = [
    HAB_SECONDARY_BUS,
    HAB_PRIMARY_BUS,
    AYSE_BUS
]


# Temporary variable, just to build the component/powerbus connection matrix.
# Don't use this dict outside of this module, use one of the matrices or
# NamedTuples instead.
_component_to_bus_mapping = {
    strings.RADS1: 1,
    strings.RADS2: 1,
    strings.AGRAV: 1,
    strings.RCON1: 1,
    strings.RCON2: 1,
    strings.ARCON1: 2,
    strings.ARCON2: 2,
    strings.ACC1: 1,
    strings.ION1: 1,
    strings.ACC2: 1,
    strings.ION2: 1,
    strings.ACC3: 1,
    strings.ION3: 1,
    strings.ACC4: 1,
    strings.ION4: 1,
    strings.PRIMARY_PUMP_1: 1,
    strings.PRIMARY_PUMP_2: 1,
    strings.SECONDARY_PUMP_1: 0,
    strings.SECONDARY_PUMP_2: 0,
    strings.HAB_CONV: 1,
    strings.FCELL: 0,
    strings.BAT1: 0,
    strings.BAT2: 0,
    strings.AYSE_BAT: 2,
    strings.RCSP: 1,
    strings.COM: 0,
    strings.HAB_REACT: 1,
    strings.REACTOR_HEATER: 0,
    strings.REACT_INJ1: 1,
    strings.REACT_INJ2: 1,
    strings.ENGINE_INJ1: 1,
    strings.ENGINE_INJ2: 1,
    strings.FCELL_INJ: 0,
    strings.AYSE_CONV: 2,
    strings.AYSE_REACT: 2,
    strings.RADAR: 1,
    strings.INS: 0,
    strings.GNC: 0,
    strings.LOS: 0,
    strings.SRB: 1,
    strings.EECOM: 0,
    strings.NETWORK: 0,
    strings.GPD1: 2,
    strings.GPD2: 2,
    strings.GPD3: 2,
    strings.GPD4: 2,
    strings.TTC: 2,
    strings.AYSE_PUMP_1: 2,
    strings.AYSE_PUMP_2: 2,
    strings.AYSE_INJ1: 2,
    strings.AYSE_INJ2: 2,
}
assert len(_component_to_bus_mapping) == len(strings.COMPONENT_NAMES)

# A 4*N matrix, with exactly N number of 1s in it (N = N_COMPONENTS).
# A 1 at COMPONENT_BUS_CONNECTION_MATRIX[bus_k][component_j] means
# component_j is connected to bus_k.
# The matrix looks roughly like:
# [0 0 0 1 0 0 1 ... 0]  Hab secondary bus components
# [1 1 1 0 0 1 0 ... 0]  Hab primary bus components
# [0 0 0 0 0 0 0 ... 1]  AYSE bus components
COMPONENT_BUS_CONNECTION_MATRIX: Final[np.ndarray] = np.zeros(
    shape=(len(POWER_BUSES), N_COMPONENTS), dtype=int
)

# Use the component -> bus mapping we defined to build the connection matrix.
for component_name, bus in _component_to_bus_mapping.items():
    COMPONENT_BUS_CONNECTION_MATRIX[bus][strings.COMPONENT_NAMES.index(component_name)] = 1

# Same as above, but in the 1-D form of [0 0 0 1 2 0 ... 1]
COMPONENT_BUS_CONNECTION_MAPPING: Final[np.ndarray] = np.zeros(shape=(N_COMPONENTS), dtype=int)

for component_name, bus in _component_to_bus_mapping.items():
    COMPONENT_BUS_CONNECTION_MAPPING[strings.COMPONENT_NAMES.index(component_name)] = bus

del _component_to_bus_mapping

# -- Below here are heating/cooling and thermal exchange-related constants. -- #
# -- These have been cribbed from Dr. Magwood's obitsej.txt data file.      -- #

# Coefficient representing how much of the power delivered to a component is
# lost to inefficiencies and resistive heating.
# A value of 0 means a component is completely efficient and does not generate
# waste heat. A value of 0.8 means 80% of power delivered to a component is
# turned into waste heat.
POWER_INEFFICIENCY: Final = np.zeros(N_COMPONENTS)

# How quickly a component radiates away heat.
PASSIVE_HEAT_LOSS: Final = np.zeros(N_COMPONENTS)

# How efficiently each component can exchange heat with each coolant loop.
# The conductivity between component j and loop k is COOLANT_CONDUCTIVITY_MATRIX[k][j]
# For example, if this matrix looks like:
#     3, 0, 6, 3, .., 3
#     4, 0, 8, 4, .., 4
#     0, 9, 0, 0, .., 0
# Then we can say the second component is cooled only by the third loop. As well,
# we can say the third component is cooled twice as much as the first component.
COOLANT_CONDUCTIVITY_MATRIX: Final = np.zeros((3, N_COMPONENTS))

# If a component is above this temperature, it will cool faster.
RESTING_TEMPERATURE: Final = np.ones(N_COMPONENTS)


def _set_base_resistance(name: str, base_resistance: float):
    """Helper only for use in this file."""
    BASE_COMPONENT_RESISTANCES[strings.COMPONENT_NAMES.index(name)] = base_resistance


def _use_orbitv_constants(name: str, hab_component: bool, power_inefficiency: float,
                          passive_heat_loss: float, secondary_loop_conductivity: float,
                          primary_loop_conductivity: float, resting_temperature: float):
    """Helper only for use in this file. Values here were just imported from obitsej.txt.
    That's why this function is allowed to be so ugly."""
    # Note: we're modifying globals here. We don't need a `global` statement
    # since we're only modifying elements of an array, but just pointing it out.

    POWER_INEFFICIENCY[strings.COMPONENT_NAMES.index(name)] = power_inefficiency
    PASSIVE_HEAT_LOSS[strings.COMPONENT_NAMES.index(name)] = passive_heat_loss
    COOLANT_CONDUCTIVITY_MATRIX[1][strings.COMPONENT_NAMES.index(name)] = secondary_loop_conductivity
    RESTING_TEMPERATURE[strings.COMPONENT_NAMES.index(name)] = resting_temperature

    if hab_component:
        COOLANT_CONDUCTIVITY_MATRIX[0][strings.COMPONENT_NAMES.index(name)] = primary_loop_conductivity
    else:
        # This is an AYSE component
        COOLANT_CONDUCTIVITY_MATRIX[2][strings.COMPONENT_NAMES.index(name)] = primary_loop_conductivity


# i forget if its ion1 then acc1, or acc1 then ion1
# TODO: reimport from the enghabw newest updated obitsej.txt
_use_orbitv_constants(strings.HAB_REACT, True, 0, 5e-5, 7.2e-3, 7.2e-3, 80.5)
_use_orbitv_constants(strings.RADS1, True, 3.0e-10, 4.7e-4, 7.0, 9.9, .25)
_use_orbitv_constants(strings.RADS2, True, 3.0e-10, 4.7e-4, 7.0, 9.9, .25)
_use_orbitv_constants(strings.AGRAV, True, 9.2e-10, 2.9e-4, 2.0e-4, 3.5e-3, .25)
_use_orbitv_constants(strings.RCON1, True, 5.2e-12, 5.9e-7, 2.0e-6, 3.5e-5, .25)
_use_orbitv_constants(strings.RCON2, True, 5.2e-12, 5.9e-7, 2.0e-6, 3.5e-5, .25)
_use_orbitv_constants(strings.ACC1, True, 1.34e-9, 5.9e-5, 2.0e-4, 3.5e-3, 25)  # Double check this isnt ION
_use_orbitv_constants(strings.ACC2, True, 1.34e-9, 5.9e-5, 2.0e-4, 3.5e-3, 25)
_use_orbitv_constants(strings.ACC3, True, 1.34e-9, 5.9e-5, 2.0e-4, 3.5e-3, 25)
_use_orbitv_constants(strings.ACC4, True, 1.34e-9, 5.9e-5, 2.0e-4, 3.5e-3, 25)
_use_orbitv_constants(strings.ION1, True, 1.48e-8, 2.7e-5, 5.0e-4, 2.0e-3, 25)
_use_orbitv_constants(strings.ION2, True, 1.48e-8, 2.7e-5, 5.0e-4, 2.0e-3, 25)
_use_orbitv_constants(strings.ION3, True, 1.48e-8, 2.7e-5, 5.0e-4, 2.0e-3, 25)
_use_orbitv_constants(strings.ION4, True, 1.48e-8, 2.7e-5, 5.0e-4, 2.0e-3, 25)
_use_orbitv_constants(strings.FCELL, True, 0, 4e-5, 5e-4, 5e-4, .5)
_use_orbitv_constants(strings.BAT1, True, 0, 1e-5, 3e-5, 3e-5, .5)
_use_orbitv_constants(strings.AYSE_BAT, True, 0, 1e-5, 1e-5, 1e-5, 0)
# _use_orbitv_constants(Aeng1, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng2, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng3, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng4, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Af10, False, 1e-10, 1e-6, 0, 3e-3, 10)
# _use_orbitv_constants(TODO, False, 0, 1.4e-5, 0, 3.3e-3, 80.5)

_set_base_resistance(strings.ACC1, 11_577.5)
_set_base_resistance(strings.ACC2, 11_577.5)
_set_base_resistance(strings.ACC3, 11_577.5)
_set_base_resistance(strings.ACC4, 11_577.5)
_set_base_resistance(strings.ION1, 610.0)
_set_base_resistance(strings.ION2, 610.0)
_set_base_resistance(strings.ION3, 610.0)
_set_base_resistance(strings.ION4, 610.0)
_set_base_resistance(strings.PRIMARY_PUMP_1, 1000.0)
_set_base_resistance(strings.PRIMARY_PUMP_2, 1000.0)
_set_base_resistance(strings.SECONDARY_PUMP_1, 10.0)
_set_base_resistance(strings.SECONDARY_PUMP_2, 10.0)
_set_base_resistance(strings.COM, 8.0)

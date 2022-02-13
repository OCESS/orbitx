""""
Hard-coded per-component physical and thermal constants.
I'm allowed to hard code data because I've already hard-coded the number of and
name of engineering components, and they're not going to reasonably change
per-savefile.

Values imported from Dr. Magwood's OBIT5SEJ.txt.

YOLO.
"""

from typing import Tuple

import numpy as np

from orbitx import data_structures
from orbitx import strings

# The resistance, in Ohms, of a component when its temperature field is 0.
# Used to calculate the resistance of a component at any temperature:
# R(temp) = BASE_RESISTANCE * (1 + common.ALPHA_RESIST_GAIN * temp)
BASE_COMPONENT_RESISTANCES = np.zeros(data_structures.N_COMPONENTS)

# The voltage, in Volts, drawn by a component when it is connected to a
# sufficiently-powered power bus at 100% capacity.
NOMINAL_COMPONENT_VOLTAGE = np.zeros(data_structures.N_COMPONENTS)


# -- Below here are heating/cooling and thermal exchange-related constants. -- #
# -- These have been cribbed from Dr. Magwood's obitsej.txt data file.      -- #

# Coefficient representing how much of the power delivered to a component is
# lost to inefficiencies and resistive heating.
# A value of 0 means a component is completely efficient and does not generate
# waste heat. A value of 0.8 means 80% of power delivered to a component is
# turned into waste heat.
POWER_INEFFICIENCY = np.zeros(data_structures.N_COMPONENTS)

# How quickly a component radiates away heat.
PASSIVE_HEAT_LOSS = np.zeros(data_structures.N_COMPONENTS)

# How efficiently a component can exchange heat with each coolant loop.
LOOP_1_CONDUCTIVITY = np.zeros(data_structures.N_COMPONENTS)
LOOP_2_CONDUCTIVITY = np.zeros(data_structures.N_COMPONENTS)
LOOP_3_CONDUCTIVITY = np.zeros(data_structures.N_COMPONENTS)

# If a component is above this temperature, it will cool faster.
RESTING_TEMPERATURE = np.zeros(data_structures.N_COMPONENTS)


def _use_orbitv_constants(name: str, hab_component: bool, power_inefficiency: float,
                          passive_heat_loss: float, secondary_loop_conductivity: float,
                          primary_loop_conductivity: float, resting_temperature: float):
    """Helper only for use in this file. Values here were just imported from obitsej.txt.
    That's why this function is allowed to be so ugly."""
    # Note: we're modifying globals here. We don't need a `global` statement
    # since we're only modifying elements of an array, but just pointing it out.

    POWER_INEFFICIENCY[strings.COMPONENT_NAMES.index(name)] = power_inefficiency
    PASSIVE_HEAT_LOSS[strings.COMPONENT_NAMES.index(name)] = passive_heat_loss
    LOOP_2_CONDUCTIVITY[strings.COMPONENT_NAMES.index(name)] = secondary_loop_conductivity
    RESTING_TEMPERATURE[strings.COMPONENT_NAMES.index(name)] = resting_temperature

    if hab_component:
        LOOP_1_CONDUCTIVITY[strings.COMPONENT_NAMES.index(name)] = primary_loop_conductivity
    else:
        # This is an AYSE component
        LOOP_3_CONDUCTIVITY[strings.COMPONENT_NAMES.index(name)] = primary_loop_conductivity


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
_use_orbitv_constants(strings.BAT2, True, 0, 1e-5, 3e-5, 3e-5, .5)
_use_orbitv_constants(strings.AYSE_BAT, True, 0, 1e-5, 1e-5, 1e-5, 0)
# _use_orbitv_constants(Aeng1, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng2, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng3, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Aeng4, False, 5e-11, 9e-6, 0, 4e-3, 15)
# _use_orbitv_constants(Af10, False, 1e-10, 1e-6, 0, 3e-3, 10)
# _use_orbitv_constants(AYSELTCHARMMMMMMM, False, 0, 1.4e-5, 0, 3.3e-3, 80.5)

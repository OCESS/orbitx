"""
Electrofunctions is not a word. I made it up.
It sounds cool though.

This module contains helpers to calculate the Voltage/Current/Resistance and
resistive heating of electrical components on our power grid."""

import numpy as np

from orbitx import common
from orbitx.data_structures import EngineeringState, N_COMPONENTS


def big_func(y: EngineeringState):
    # Engineering values
    R = y.components.Resistance()
    I = y.components.Current()

    # The following block of code implements conductive cooling of components by connected coolant loops.
    # https://en.wikipedia.org/wiki/Thermal_conduction#Fourier's_law shows the high-level math and theory.
    # If N = the number of components, and there are 3 coolant loops, we can scale two adjacency matrices of
    # component/coolant loop connections by the temperature of the components and temperature of coolants,
    # respectively, and subtract them from each other to find the temperature difference between each component
    # and the connected coolant loop. Then, we can use Fourier's law to find out how much component is cooled
    # (and each coolant loop is heated).

    # Create a 3xN adjacency matrix to encode what components are connected to which coolant loops.
    connected_loops_matrix = y.components.CoolantConnectionMatrix()

    # N-long vector of component temperatures.
    component_temperature_row_vector = y.components.Temperature()

    # 3-long vector of coolant temperatures.
    # np.newaxis is required for tranposed vector to be used in matrix math
    coolant_temperature_col_vector = y.coolant_loops.CoolantTemp()[np.newaxis]

    temperature_difference_matrix = (
        component_temperature_row_vector * connected_loops_matrix -
        connected_loops_matrix * coolant_temperature_col_vector.transpose()
    )

    # Components heat up when they are powered.
    resistive_heat = common.COEFF_TEMPERATURE_GAIN * V * I

    # Components transfer heat to coolant.
    coolant_heat_loss = temperature_difference_matrix.sum(axis=0) * common.K_CONDUCTIVITY

    # TODO: Calculate heating of coolant from component cooling.
    # TODO: Calculate cooling of coolant from radiators connected to coolant loops.
    # TODO: Encapsulate this in a helper function.

    T_deriv = resistive_heat - coolant_heat_loss
    R_deriv = common.ALPHA_RESIST_GAIN * T_deriv

    # Voltage and current do not change
    V_deriv = I_deriv = np.zeros(N_COMPONENTS)

def _calculate_bus_resistance(y: EngineeringState) -> np.ndarray:
	pass
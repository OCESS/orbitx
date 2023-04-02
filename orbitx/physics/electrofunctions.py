"""
Electrofunctions is not a word. I made it up.
It sounds cool though.

This module contains helpers to calculate the Voltage/Current/Resistance and
resistive heating of electrical components on our power grid."""
from __future__ import annotations

from typing import List

import numpy as np

from orbitx.common import OhmicVars
from orbitx.physics import electroconstants


def _bus_electricals(component_resistances: np.ndarray) -> List[OhmicVars]:
    """Given resistances for each component, calculate the V, I, R for the electrical bus as a whole.
    Outputs a List[OhmicVars], where the first element is the primary bus, etc, per the order defined
    in electroconstants.POWER_BUSES."""

    bus_resistances: List[float] = np.zeros(len(electroconstants.POWER_BUSES))
    bus_voltages: List[float] = np.zeros(len(electroconstants.POWER_BUSES))
    bus_currents: List[float] = np.zeros(len(electroconstants.POWER_BUSES))

    # It might be slightly more efficient to do matrix math instead of using a for loop, but this
    # is more readable :)
    for bus_n, bus in enumerate(electroconstants.POWER_BUSES):
        # Calculate 1/resistance for each component, then sum them all up to find the resistance on a power bus.
        # We shouldn't have to guard against divide-by-zero here, because resistances shouldn't
        # be zero. If we _do_ divide by zero, we've configured np.seterr elsewhere to raise an exception.

        # The right side of this first assignment evaluates to an array with a 0 or 1 for every component.
        components_on_this_bus = (electroconstants.COMPONENT_BUS_CONNECTION_MATRIX[bus_n] != 0)
        # For every component attached to this bus, sum 1/(component_resistance)
        sum_of_reciprocals = np.sum(np.reciprocal(component_resistances[components_on_this_bus]))

        if sum_of_reciprocals == 0.0:
            # There are no components connected.
            bus_resistance = np.inf
        else:
            bus_resistance = 1 / sum_of_reciprocals
        bus_resistances[bus_n] = bus_resistance

        # Assuming the hab reactor has an internal resistance, calculate the voltage drop given the bus load.
        # This equation is derived from https://en.wikipedia.org/wiki/Internal_resistance, specifically
        # R_reactor_internal = (V_bus_nominal / V_bus_loaded - 1) * R_bus_loaded
        # If we solve for V_bus_loaded (since we know the value of all other variables):
        # V_bus_loaded = V_bus_nominal / (R_reactor_internal / R_bus_loaded + 1)
        bus_voltages[bus_n] = bus.nominal_voltage / (bus.primary_power_source.internal_resistance / bus_resistance + 1)
        # TODO: Take into account secondary voltage sources. Specifically, we can share current across multiple sources
        # scaling with 1/Rn / (1/R1 + 1/R2) * current.
        # TODO: Take into account what buses are connected to each other. Specifically, the voltage drop should happen
        # across multiple buses, in addition to current sharing. Maybe some sort of big matrix multiplication?

    # https://en.wikipedia.org/wiki/Nodal_admittance_matrix calculate what current is 'admitted' to other buses.
    bus_currents = electroconstants.BUS_ADMITTANCE_MATRIX * bus_voltages

    buses: List[OhmicVars] = []
    for bus_n in range(0, len(electroconstants.POWER_BUSES)):
        buses.append(OhmicVars(voltage=bus_voltages[bus_n],
                               current=bus_currents[bus_n],
                               resistance=bus_resistances[bus_n]))

    return buses


def component_resistances(components: ComponentList) -> np.ndarray:
    """Returns an array of each component's effective resistance.
    If a component is not connected to the bus, or it has been set
    to 0% capacity, it will have infinite resistance."""

    # This is a per-component list of scalars.
    # A value of 1 means a component is 'on' and at 100% capacity.
    # A value of 0 means a component is 'off', or at 0% capacity.
    # A value of 1.2 means a component is 'on' and at 120% capacity.
    # Values can be in the range [0, 1], as well as greater than 1.
    component_capacities = components.Connected() * components.Capacities()

    component_resistances_assuming_full_capacity = (
        electroconstants.BASE_COMPONENT_RESISTANCES
        + electroconstants.ALPHA_RESIST_GAIN * components.Temperatures()
        * electroconstants.BASE_COMPONENT_RESISTANCES
    )

    return np.divide(
        component_resistances_assuming_full_capacity,
        component_capacities,

        # If we would divide by zero, instead just skip that step and return Inf.
        # We don't want to divide by zero here, because we've configured np.seterr
        # to raise an exception on divide-by-zero.
        # https://stackoverflow.com/a/37977222/1333978 for this divide-by-zero guarding code.
        where=(component_capacities != 0), out=np.full_like(component_capacities, np.inf)
    )


def component_heating_rate(
        y: EngineeringState, component_resist_array: np.ndarray, power_buses: List[OhmicVars]
) -> np.ndarray:
    """Calculate an array of length N_COMPONENTS, for how much each component is heating or cooling."""

    # Calculate the voltage of each component.
    # Really, this is just a fancy way of selecting which of the four bus voltages
    # to use.
    bus_voltages_column_vector = np.array([[
        power_buses[0].voltage,
        power_buses[1].voltage,
        power_buses[2].voltage,
        power_buses[3].voltage
    ]]).T

    component_voltages = np.sum(bus_voltages_column_vector * electroconstants.COMPONENT_BUS_CONNECTION_MATRIX, axis=0)

    # Calculate the power of each component.
    # Since P = IV and I = V/R, we can just use the P = V^2 / R shortcut.
    # We use the voltage of the respective power bus, since the voltage of
    # every component in a single parallel circuit is the same.
    component_powers = np.square(component_voltages) / component_resist_array

    # A bit of the power going through a component gets turned into heat.
    resistive_heating = component_powers * electroconstants.POWER_INEFFICIENCY

    # In enghabw, heat^2 is used for a bunch of calculation. We'll do the same calculations in OrbitX as well.
    temperature_squared = np.square(y.components.Temperatures())

    # Calculate how much heat each component radiates away.
    passive_cooling = temperature_squared * electroconstants.PASSIVE_HEAT_LOSS

    # Calculate how much each component is cooled by their respective coolant loops.
    active_cooling = (
        temperature_squared
        * electroconstants.COOLANT_CONDUCTIVITY_MATRIX
        / y.coolant_loops.CoolantTemp()[np.newaxis].T
        # The [np.newaxis].T trick on the line above just forces .CoolantTemp() to be a column vector,
        # so that the temperature of each coolant loop gets broadcasted across COOLANT_CONDUCTIVITY_MATRIX
        # properly.
    )

    # TODO: Calculate atmospheric cooling.
    # TODO: Calculate coolant loop temperature increase.

    degrees_above_resting_temp = np.clip(y.components.Temperatures() - electroconstants.RESTING_TEMPERATURE, 0, np.inf)

    # Collapse the columns down by summing them, so we get a 1D array of how much each component is being cooled.
    effective_coolant_cooling = np.sum(active_cooling, axis=0)

    # Put everything together, finding the derivative of temperature for all components.
    net_heating = resistive_heating - passive_cooling - effective_coolant_cooling

    # Set upper and lower bounds on how quickly components heat and cool.
    # A component can only heat by at most 20 degrees/second (to prevent, say, the battery exploding).
    # A component can only cool by at most `degrees_above_resting_temp` degrees/second, which should not
    # usually have any significant impact but improves the stability of the simulation for Reasons(tm).
    # (Those 'Reasons' are to do with scipy's implementation of the solve_ivp function. Suffice to say,
    # it messes up the scipy simulation if a value in OrbitX has a wildly-fluctuating differential.)
    capped_net_heating = np.clip(net_heating, -1 * degrees_above_resting_temp, electroconstants.MAX_HEATING_RATE)

    return capped_net_heating

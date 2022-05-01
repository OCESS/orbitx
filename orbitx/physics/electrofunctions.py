"""
Electrofunctions is not a word. I made it up.
It sounds cool though.

This module contains helpers to calculate the Voltage/Current/Resistance and
resistive heating of electrical components on our power grid."""

from typing import NamedTuple

import numpy as np

from orbitx import common
from orbitx.physics import electroconstants
from orbitx.data_structures import EngineeringState, N_COMPONENTS


class OhmicVars(NamedTuple):
    """
    Encapsulates a Voltage, Current, and Resistance where V = IR.
    This class is called 'Ohmic' because it's all the things for Ohm's law.
    I don't think Ohmic is a word. I made it up. I like to think it sounds cool.
    """
    voltage: float
    current: float
    resistance: float


def bus_electricity(component_resistances: np.ndarray) -> OhmicVars:
    """Given resistances for each component, calculate the V, I, R for the electrical bus as a whole."""

    # Calculate 1/resistance for each component, then sum them all up into a single scalar.
    # We shouldn't have to guard against divide-by-zero here, because resistances shouldn't
    # be zero. If we _do_ divide by zero, we've configured np.seterr elsewhere to raise an exception.
    sum_of_reciprocals = np.sum(np.reciprocal(component_resistances))

    if sum_of_reciprocals == 0:
        # There are no components connected, so this simplifies our calculations.
        return OhmicVars(resistance=np.inf, current=0, voltage=electroconstants.NOMINAL_BUS_VOLTAGE)

    bus_resistance = 1/sum_of_reciprocals

    # Assuming the hab reactor has an internal resistance, calculate the voltage drop given the bus load.
    # This equation is derived from https://en.wikipedia.org/wiki/Internal_resistance, specifically
    # R_reactor_internal = (V_bus_nominal / V_bus_loaded - 1) * R_bus_loaded
    # If we solve for V_bus_loaded (since we know the value of all other variables):
    # V_bus_loaded = V_bus_nominal / (R_reactor_internal / R_bus_loaded + 1)
    bus_voltage = (
        electroconstants.NOMINAL_BUS_VOLTAGE /
        (electroconstants.REACTOR_INTERNAL_RESISTANCE / bus_resistance + 1)
    )

    # Ohm's law gives us this.
    bus_current = bus_voltage / bus_resistance
    return OhmicVars(voltage=bus_voltage, current=bus_current, resistance=bus_resistance)


def component_resistances(y: EngineeringState) -> np.ndarray:
    """Returns an array of each component's effective resistance.
    If a component is not connected to the bus, or it has been set
    to 0% capacity, it will have infinite resistance."""

    # This is a per-component list of scalars.
    # A value of 1 means a component is 'on' and at 100% capacity.
    # A value of 0 means a component is 'off', or at 0% capacity.
    # A value of 1.2 means a component is 'on' and at 120% capacity.
    # Values can be in the range [0, 1], as well as greater than 1.
    component_capacities = y.components.Connected() * y.components.Capacities()

    component_resistances_assuming_full_capacity = (
        electroconstants.BASE_COMPONENT_RESISTANCES +
        electroconstants.ALPHA_RESIST_GAIN * y.components.Temperatures() *
        electroconstants.BASE_COMPONENT_RESISTANCES
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


def component_heating_rate(y: EngineeringState, component_resist_array: np.ndarray, bus_voltage: float) -> np.ndarray:
    # Calculate the power of each component.
    # Since P = IV and I = V/R, we can just use the P = V^2 / R shortcut.
    component_powers = bus_voltage * bus_voltage / component_resist_array

    # A bit of the power going through a component gets turned into heat.
    resistive_heating = component_powers * electroconstants.POWER_INEFFICIENCY

    # In enghabw, heat^2 is used for a bunch of calculation. We'll do the same calculations in OrbitX as well.
    temperature_squared = np.square(y.components.Temperatures())

    # Calculate how much heat each component radiates away.
    passive_cooling = temperature_squared * electroconstants.PASSIVE_HEAT_LOSS

    # Calculate how much each component is cooled by their respective coolant loops.
    active_cooling = (
        temperature_squared *
        electroconstants.COOLANT_CONDUCTIVITY_MATRIX /
        y.coolant_loops.CoolantTemp()[np.newaxis].T
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

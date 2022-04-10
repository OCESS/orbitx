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
    """Encapsulates a Voltage, Current, and Resistance where V = IR"""
    voltage: float
    current: float
    resistance: float


def bus_electricity(component_resistances: np.ndarray) -> OhmicVars:
    """Given resistances for each component, calculate the V, I, R for the electrical bus as a whole."""

    # Standard formula for finding total resistance of a parallel circuit, safguarded from divide-by-zero errors.
    bus_resistance = 1 / np.sum(np.reciprocal(component_resistances), where=(component_resistances != 0))

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
    to 0% capacity, it will not be counted."""
    return (
        y.components.Connected() * y.components.Capacities() * (
            electroconstants.BASE_COMPONENT_RESISTANCES +
            electroconstants.ALPHA_RESIST_GAIN * y.components.Temperatures() *
            electroconstants.BASE_COMPONENT_RESISTANCES
        )
    )


def component_heating_rate(y: EngineeringState, component_resist_array: np.ndarray, bus_voltage: float) -> np.ndarray:
    # Calculate the power of each component.
    # Since P = IV and I = V/R, we can just use the P = V^2 / R shortcut.
    component_powers = bus_voltage * bus_voltage / component_resist_array

    # A bit of the power going through a component gets turned into heat.
    resistive_heating = np.multiply(component_powers, electroconstants.POWER_INEFFICIENCY)

    # In enghabw, heat^2 is used for a bunch of calculation. So we use it here as well.
    square_of_heat = np.square(y.components.Temperatures())

    passive_cooling = square_of_heat * electroconstants.PASSIVE_HEAT_LOSS
    active_cooling = square_of_heat * electroconstants.COOLANT_CONDUCTIVITY_MATRIX
    # TODO: Calculate atmospheric cooling.

    # Reduce coolant cooling rate when within 1 degree of the minimum temperature. Note, passive cooling is unaffected.
    # Why? Because that's how enghabw does it :)
    degrees_over_min_temp = y.components.Temperatures() - electroconstants.RESTING_TEMPERATURE
    cooling_scaling = np.clip(degrees_over_min_temp, 0, 1)
    # Note: we can't just immediately stop the cooling effect when we reach the resting temperature, because
    # anything that causes the derivative function of the temperature to suddenly change behaviour will probably
    # not work very well with our ODE solver. Google something like 'scipy odeint stiff function' if you want to
    # know more, or just message Patrick.

    # If a coolant is connected to a component, and that component is greater than 1 degree above its resting
    # temperature, the coolant will be fully used.
    coolant_usage_matrix = y.components.CoolantConnectionMatrix() * cooling_scaling

    effective_coolant_cooling = np.sum(
        coolant_usage_matrix * active_cooling,
        axis=0  # Collapse the columns down by summing them, so we get a 1D array of size N_COMPONENTS.
    )

    # Put everything together, finding the derivative of temperature for all components.
    return resistive_heating + passive_cooling + effective_coolant_cooling

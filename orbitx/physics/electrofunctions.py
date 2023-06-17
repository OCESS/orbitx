"""
Electrofunctions is not a word. I made it up.
It sounds cool though.

This module contains helpers to calculate the Voltage/Current/Resistance and
resistive heating of electrical components on our power grid."""
from __future__ import annotations

from typing import List, Union

import numpy as np

from orbitx import strings
from orbitx.common import OhmicVars
from orbitx.data_structures.engineering import EngineeringState
from orbitx.physics.eng_subsystems import ComponentList
from orbitx.physics import electroconstants
from orbitx.physics.electroconstants.electroconstants import PowerSource, VoltageConverter


# dont have power sources have a resistance
# instead, calculate component resistances naively,
# then select the active power source for each bus,
# allowing for cross-bus voltage converters (e.g. bus1 -> AYSE Reactor).
# Once you have Optional[generator] -> List[bus] mapping, each generator will calculate current draw via
# 1/Rt = 1/a + 1/b + .. [+ 1/output_bus_total_resistance if there's a connection]
#   solve for Rt, then Vnominal/(Rintern/Rt+1) = Vactual
#   Then Vactual/Rt = current out of generator
#   And Vactual*scale_factor = Vactual_on_output_bus
#   And thus, Ioutputbus = Vactual*scale_factor/output_bus_total_resistance


def bus_electricals(
    component_resistances: np.ndarray,
    active_power_sources: List[Union[PowerSource, VoltageConverter, None]]
) -> List[OhmicVars]:
    bus_resistances = np.full(len(electroconstants.POWER_BUSES), np.nan)
    bus_voltages = np.full(len(electroconstants.POWER_BUSES), np.nan)
    bus_currents = np.full(len(electroconstants.POWER_BUSES), np.nan)

    # Step 1: Calculate total resistances on each bus.
    for bus_i, no_power_source in enumerate(active_power_sources):
        # Calculate unpowered buses first. Poor them, they could use the attention.
        if no_power_source is not None:
            # Only unpowered buses.
            continue

        bus_resistances[bus_i] = np.inf
        bus_currents[bus_i] = 0
        bus_voltages[bus_i] = 0

    for bus_i, voltage_converter in enumerate(active_power_sources):
        # Then calculate the resistances of any buses powered by a power converter.
        # Their voltage and current will come later.
        if not isinstance(voltage_converter, VoltageConverter):
            # Only voltage converters, thank you very much.
            continue

        bus_resistances[bus_i] = _bus_resistance(bus_i, component_resistances)

        # Then, set the resistance of the voltage converter so that the input bus will realize it's a load.
        converter_i = strings.COMPONENT_NAMES.index(voltage_converter.name)
        component_resistances[converter_i] = bus_resistances[bus_i]

    for bus_i, generator in enumerate(active_power_sources):
        if not isinstance(generator, PowerSource):
            # Only actual power sources like reactors now, we've done everything else.
            continue

        bus_resistances[bus_i] = _bus_resistance(bus_i, component_resistances)

        # Step 2: Calculate the actual voltage output of each power generator.
        # We figure out the voltage drop on each bus by reading the equation in
        # https://en.wikipedia.org/wiki/Internal_resistance and solving for V_fl.
        bus_voltages[bus_i] = (
            electroconstants.POWER_BUSES[bus_i].nominal_voltage
            / (generator.internal_resistance / bus_resistances[bus_i] + 1)
        )
        bus_currents[bus_i] = bus_voltages[bus_i] / bus_resistances[bus_i]

    for output_bus_i, voltage_converter in enumerate(active_power_sources):
        # Step 3: Now that we know the voltage of the input bus that's powering this converter,
        # calculate the voltage of the output bus that is powered by this converter.
        if not isinstance(voltage_converter, VoltageConverter):
            # Only voltage converters, thank you very much.
            continue

        input_bus_i = electroconstants.POWER_BUSES.index(voltage_converter.input_bus.name)
        bus_voltages[output_bus_i] = bus_voltages[input_bus_i] * voltage_converter.scale_factor
        bus_currents[output_bus_i] = bus_currents[input_bus_i] / voltage_converter.scale_factor

    buses: List[OhmicVars] = []
    for bus_n in range(0, len(electroconstants.POWER_BUSES)):
        buses.append(OhmicVars(voltage=bus_voltages[bus_n],
                               current=bus_currents[bus_n],
                               resistance=bus_resistances[bus_n]))
    return buses


def _bus_resistance(bus_i: int, component_resistances: np.ndarray) -> float:
    # Calculate 1/resistance for each component, then sum them all up to find the resistance on a power bus.
    # We shouldn't have to guard against divide-by-zero here, because resistances shouldn't
    # be zero. If we _do_ divide by zero, we've configured np.seterr elsewhere to raise an exception.

    # The right side of this first assignment evaluates to an array with a 0 or 1 for every component.
    components_on_this_bus = (electroconstants.COMPONENT_BUS_CONNECTION_MATRIX[bus_i] != 0)
    # For every component attached to this bus, sum 1/(component_resistance)
    sum_of_reciprocals = np.sum(np.reciprocal(component_resistances[components_on_this_bus]))

    if sum_of_reciprocals == 0.0:
        # There are no components connected.
        return np.inf
    else:
        return 1 / sum_of_reciprocals


def component_resistances(components: ComponentList) -> np.ndarray:
    """Returns each component's effective resistance.
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

    component_resistances = np.divide(
        component_resistances_assuming_full_capacity,
        component_capacities,

        # If we would divide by zero, instead just skip that step and return Inf.
        # We don't want to divide by zero here, because we've configured np.seterr
        # to raise an exception on divide-by-zero.
        # https://stackoverflow.com/a/37977222/1333978 for this divide-by-zero guarding code.
        where=(component_capacities != 0), out=np.full_like(component_capacities, np.inf)
    )

    return component_resistances


def component_heating_rate(
        y: EngineeringState, component_resist_array: np.ndarray, power_buses: List[OhmicVars]
) -> np.ndarray:
    """Calculate an array of length N_COMPONENTS, for how much each component is heating or cooling."""

    # Calculate the voltage of each component.
    # Really, this is just a fancy way of selecting which of the four bus voltages
    # to use.
    # TODO: fixup
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


def active_power_sources(components: ComponentList) -> List[PowerSource, VoltageConverter, None]:
    """TODO explain lmao."""
    active_power_source_list = []

    for bus in electroconstants.POWER_BUSES:
        # Try to find a power source.
        active_power_source: Union[PowerSource, VoltageConverter, None] = None
        for power_source in bus.power_sources:
            power_source_index = strings.COMPONENT_NAMES.index(power_source.name)
            if components[power_source_index].connected * components[power_source_index].capacity != 0:
                # We select the first power source in the ordered list of bus.power_sources, and use it!
                active_power_source = power_source
                break

        # Note: active_power_source could be None at this point.
        active_power_source_list.append(active_power_source)

    return active_power_source_list

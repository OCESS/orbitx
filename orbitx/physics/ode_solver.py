"""
This is the differential function and event functions given to the scipy ODE solver.

The most important function here is simulation_differential_function, which
has its own large comment block.
"""

from typing import Union, Tuple, Callable, List
import logging

import numpy as np
import scipy
from orbitx import strings
from orbitx import common
from orbitx.common import N_COMPONENTS, N_COOLANT_LOOPS, N_RADIATORS  # These get typed a lot, import them directly.
from orbitx.data_structures.engineering import EngineeringState
from orbitx.data_structures.eng_subsystems import (
    _N_COMPONENT_FIELDS, _N_COOLANT_FIELDS, _N_RADIATOR_FIELDS
)
from orbitx.data_structures.space import PhysicsState
from orbitx.data_structures.entity import _ENTITY_FIELD_ORDER

from orbitx.strings import AYSE, HABITAT
from orbitx.physics import calc, electrofunctions, helpers
from orbitx.orbitx_pb2 import PhysicalState


log = logging.getLogger('orbitx')


def simulation_differential_function(
    t: float, y_1d: np.ndarray,
    pass_through_state: PhysicalState,
    masses: np.ndarray, artificials: np.ndarray
) -> np.ndarray:
    """
    Given the state of a simulation, calculate its instantaneous rate-of-change.

    This function is probably one of the most important ones in OrbitX :)
    Everything from "an object with a velocity will change position" to
    "the habitat reactor heats up when it's being used" is encoded here.

    This function is used by scipy.solve_ivp, which unfortunately requires
    that the y_1d input of this function is a single 1-dimensional array.
    We also have the same requirement of this function's output. This means
    that we have to encode almost the entire state of the OrbitX simulation
    in the y_1d input array, and every single value in that array has to have
    a corresponding output value in the output array. This is a big array!

    This is roughly the ordering of fields in the input array:

    y_1d =
     [X, Y, VX, VY, Heading, Spin, Fuel, Throttle, LandedOn, Broken] +
     SRB_time_left + time_acc (these are both single values) +
     [ComponentData, CoolantLoopData, RadiatorData]
    returns the derivative of y_1d, i.e.
    [VX, VY, AX, AY, Spin, 0, Fuel consumption, 0, 0, 0] + -constant + 0
    (zeroed-out fields are changed elsewhere)

    The ordering of fields is determined by the ordering in orbitx.proto.
    If the structure of the y_1d array changes, make sure to update this
    function and anywhere annotated with #Y_VECTOR_CHANGESITE!

    !!!!!!!!!!! IMPORTANT !!!!!!!!!!!
    This function should return a DERIVATIVE. The numpy.solve_ivp function
    will do the rest of the work of the simulation, this function just
    describes how things _move_.
    At its most basic level, this function takes in the _position_ of
    everything (plus some random stuff), and returns the _velocity_ of
    everything (plus some random stuff).
    Essentially, numpy.solve_ivp does this calculation:
    new_positions_of_system = t_delta * _derive(
                                            current_t_of_system,
                                            current_y_of_system)

    Any arguments after `t` and `y_1d` are just extra constants and
    pass-through state, which should remain constant during normal simulation.
    They are passed in to speed up computation, since this function is the most
    performance-sensitive part of the orbitx codebase(!!!)
    """

    # Note: we create this y as a PhysicsState for convenience, but if you
    # set any values of y, the changes will be discarded! The only way they
    # will be propagated out of this function is by numpy using the return
    # value of this function as a derivative, as explained above.
    # If you want to set values in y, look at _reconcile_entity_dynamics.
    y = PhysicsState(y_1d, pass_through_state)
    acc_matrix = calc.grav_acc(y.X, y.Y, masses, y.Fuel)
    zeros = np.zeros(y._n)
    fuel_cons = np.zeros(y._n)

    # Engine thrust and fuel consumption
    for artif_index in artificials:
        if y[artif_index].fuel > 0 and y[artif_index].throttle > 0:
            # We have fuel remaining, calculate thrust
            entity = y[artif_index]
            capability = common.craft_capabilities[entity.name]

            fuel_cons[artif_index] = \
                -abs(capability.fuel_cons * entity.throttle)
            eng_thrust = (capability.thrust * entity.throttle
                          * calc.heading_vector(entity.heading))
            mass = entity.mass + entity.fuel

            if entity.name == AYSE and \
                    y[HABITAT].landed_on == AYSE:
                # It's bad that this is hardcoded, but it's also the only
                # place that this comes up so IMO it's not too bad.
                hab = y[HABITAT]
                mass += hab.mass + hab.fuel

            eng_acc = eng_thrust / mass
            acc_matrix[artif_index] += eng_acc

    # And SRB thrust
    srb_usage = 0
    try:
        if y.srb_time >= 0:
            hab_index = y._name_to_index(HABITAT)
            hab = y[hab_index]
            srb_acc = common.SRB_THRUST / (hab.mass + hab.fuel)
            srb_acc_vector = srb_acc * calc.heading_vector(hab.heading)
            acc_matrix[hab_index] += srb_acc_vector
            srb_usage = -1
    except PhysicsState.NoEntityError:
        # The Habitat doesn't exist.
        pass

    # Drag effects
    craft = y.craft
    if craft is not None:
        craft_index = y._name_to_index(y.craft)
        drag_acc = calc.drag(y)
        acc_matrix[craft_index] -= drag_acc

    # Centripetal acceleration to keep landed entities glued to each other.
    landed_on = y.LandedOn
    for landed_i in landed_on:
        lander = y[landed_i]
        ground = y[landed_on[landed_i]]

        centripetal_acc = (lander.pos - ground.pos) * ground.spin ** 2
        acc_matrix[landed_i] = \
            acc_matrix[landed_on[landed_i]] - centripetal_acc

    # Time for the Engineering section.
    component_resistances = electrofunctions.component_resistances(y.engineering.components)
    bus_electricals = electrofunctions._bus_electricals(component_resistances)
    bus_power = bus_electricals[0].voltage * bus_electricals[0].current

    # Just lifted this from DM's enghabw.bas code. Probably has deeper significance.
    fuel_usage_rate = .05 * bus_power / 50_000_000
    # TODO: Replace the existing fuel consumption calculations with this calculation.

    component_heating_rate_array = electrofunctions.component_heating_rate(
        y.engineering, component_resistances, bus_electricals
    )

    # Sets velocity and spin of a couple more entities.
    # If you want to set the acceleration of an entity, do it above and
    # keep that logic in _derive. If you want to set the velocity and spin
    # or any other fields that an Entity has, you should put that logic in
    # this _reconcile_entity_dynamics helper.
    y = helpers._reconcile_entity_dynamics(y)

    # If the ordering of fields in orbitx.proto changes, change here too. #Y_VECTOR_CHANGESITE
    y_differential = np.concatenate((
        y.VX, y.VY, np.hsplit(acc_matrix, 2), y.Spin,
        zeros, fuel_cons, zeros, zeros, zeros, np.array([srb_usage, 0]),
        np.zeros(N_COMPONENTS), np.zeros(N_COMPONENTS),  # connected and capacity fields
        component_heating_rate_array,
        np.zeros(N_COMPONENTS), np.zeros(N_COMPONENTS), np.zeros(N_COMPONENTS),  # coolant connection states
        np.zeros(N_COOLANT_LOOPS * _N_COOLANT_FIELDS),
        np.zeros(N_RADIATORS * _N_RADIATOR_FIELDS)
    ), axis=None)

    return y_differential


class Event:
    """Implements an event function. See numpy documentation for solve_ivp."""
    # These two fields tell scipy to stop simulation when __call__ returns 0
    terminal = True
    direction = -1

    # Implement this in an event subclass
    def __call___(self, t: float, y_1d: np.ndarray) -> float:
        ...


class SrbFuelEvent(Event):
    def __call__(self, t, y_1d) -> float:
        """Returns how much SRB burn time is left.
        This will cause simulation to stop when SRB burn time reaches 0."""
        return y_1d[PhysicsState.SRB_TIME_INDEX]


class HabFuelEvent(Event):
    def __init__(self, initial_state: PhysicsState):
        self.initial_state = initial_state

    def __call__(self, t, y_1d) -> float:
        """Return a 0 only when throttle is nonzero."""
        y = PhysicsState(y_1d, self.initial_state._proto_state)
        for index, entity in enumerate(y._proto_state.entities):
            if entity.artificial and y.Throttle[index] != 0:
                return y.Fuel[index]
        return np.inf


class CollisionEvent(Event):
    def __init__(self, initial_state: PhysicsState, radii: np.ndarray):
        self.initial_state = initial_state
        self.radii = radii

    def __call__(self, t, y_1d, return_pair=False
                 ) -> Union[float, Tuple[int, int]]:
        """Returns a scalar, with 0 indicating a collision and a sign change
        indicating a collision has happened."""
        y = PhysicsState(y_1d, self.initial_state._proto_state)
        n = len(self.initial_state)
        # 2xN of (x, y) positions
        posns = np.column_stack((y.X, y.Y))
        # An n*n matrix of _altitudes_ between each entity
        alt_matrix = (
            scipy.spatial.distance.cdist(posns, posns)
            - np.array([self.radii]) - np.array([self.radii]).T)
        # To simplify calculations, an entity's altitude from itself is inf
        np.fill_diagonal(alt_matrix, np.inf)
        # For each pair of objects that have collisions disabled between
        # them, also set their altitude to be inf

        # If there are any entities landed on any other entities, ignore
        # both the landed and the landee entity.
        landed_on = y.LandedOn
        for index in landed_on:
            alt_matrix[index, landed_on[index]] = np.inf
            alt_matrix[landed_on[index], index] = np.inf

        if return_pair:
            # Returns the actual pair of indicies instead of a scalar.
            flattened_index = alt_matrix.argmin()
            # flattened_index is a value in the interval [1, n*n]-1.
            # Turn it into a  2D index.
            object_i = flattened_index // n
            object_j = flattened_index % n
            return object_i, object_j
        else:
            # solve_ivp invocation, return scalar
            return np.min(alt_matrix)


class LiftoffEvent(Event):
    def __init__(self, initial_state: PhysicsState):
        self.initial_state = initial_state

    def __call__(self, t, y_1d) -> float:
        """Return 0 when the craft is landed but thrusting enough to lift off,
        and a positive value otherwise."""
        y = PhysicsState(y_1d, self.initial_state._proto_state)
        if y.craft is None:
            # There is no craft, return early.
            return np.inf
        craft = y.craft_entity()

        if not craft.landed():
            # We don't have to lift off because we already lifted off.
            return np.inf

        planet = y[craft.landed_on]
        if planet.artificial:
            # If we're docked with another satellite, undocking is governed
            # by other mechanisms. Ignore this.
            return np.inf

        thrust = common.craft_capabilities[craft.name].thrust * craft.throttle
        if y.srb_time > 0 and y.craft == HABITAT:
            thrust += common.SRB_THRUST

        pos = craft.pos - planet.pos
        # This is the G(m1*m2)/r^2 formula
        weight = common.G * craft.mass * planet.mass / np.inner(pos, pos)

        # This should be positive when the craft isn't thrusting enough, and
        # zero when it is thrusting enough.
        return max(0, common.LAUNCH_TWR - thrust / weight)


class HighAccEvent(Event):
    def __init__(
            self, derive: Callable[[float, np.ndarray], np.ndarray],
            artificials: List[int], acc_bound: float, current_acc: float,
            n_entities: int):
        self.derive = derive
        self.artificials = artificials
        self.acc_bound = acc_bound
        self.current_acc = round(current_acc)
        self.ax_offset = n_entities * _ENTITY_FIELD_ORDER['vx']
        self.ay_offset = n_entities * _ENTITY_FIELD_ORDER['vy']

    def __call__(self, t: float, y_1d: np.ndarray) -> float:
        """Return positive if the current time acceleration is accurate, zero
        then negative otherwise."""
        if self.current_acc == 1:
            # If we can't lower the time acc, don't bother doing any work.
            return np.inf
        derive_result = self.derive(t, y_1d)
        max_acc_mag = 0.0005  # A small nonzero value.
        for artif_index in self.artificials:
            accel = (derive_result[self.ax_offset] + artif_index,
                     derive_result[self.ay_offset] + artif_index)
            acc_mag = calc.fastnorm(accel)
            if acc_mag > max_acc_mag:
                max_acc_mag = acc_mag
        return max(self.acc_bound - acc_mag, 0)


class HabReactorTempEvent(Event):
    # Trigger this event if we're going above or below dangerous temperature.
    direction = 0

    def __call__(self, t, y_1d) -> float:
        """Returns how close reactor temp is to danger.
        This will cause simulation to stop at the dangerous temp."""
        # This janky manual array accessing negates the need to build an
        # EngineeringState at every simulation step. But! This should be
        # kept in sync with ComponentView.temperature.
        return y_1d[
            PhysicsState.ENGINEERING_START_INDEX
            + EngineeringState._COMPONENT_START_INDEX
            + (
                strings.COMPONENT_NAMES.index(strings.HAB_REACT)
                * _N_COMPONENT_FIELDS
                + 1)
        ] - common.DANGEROUS_REACTOR_TEMP


class AyseReactorTempEvent(Event):
    # Trigger this event if we're going above or below dangerous temperature.
    direction = 0

    def __call__(self, t, y_1d) -> float:
        """Returns how close reactor temp is to danger.
        This will cause simulation to stop at the dangerous temp."""
        # This janky manual array accessing negates the need to build an
        # EngineeringState at every simulation step. But! This should be
        # kept in sync with ComponentView.temperature.
        return y_1d[
            PhysicsState.ENGINEERING_START_INDEX
            + EngineeringState._COMPONENT_START_INDEX
            + (
                strings.COMPONENT_NAMES.index(strings.AYSE_REACT)
                * _N_COMPONENT_FIELDS
                + 1)
        ] - common.DANGEROUS_REACTOR_TEMP

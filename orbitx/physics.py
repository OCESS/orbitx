import collections
import functools
import logging
import threading
import time
import warnings
from typing import Tuple, Union

import numpy as np
import scipy.integrate
import scipy.spatial
import scipy.special


from . import orbitx_pb2 as protos
from . import common
from .physic_functions import *
from .physics_entity import Habitat
from .physics_state import PhysicsState

SOLUTION_CACHE_SIZE = 5

warnings.simplefilter('error')  # Raise exception on numpy RuntimeWarning
scipy.special.seterr(all='raise')
log = logging.getLogger()

# Note on variable naming:
# a lowercase single letter, like `x`, is likely a scalar
# an uppercase single letter, like `X`, is likely a 1D row vector of scalars
# `y` is either the y position, or a vector of the form [X, Y, DX, DY]. i.e. 2D
# `y_1d` specifically is the 1D row vector flattened version of the above `y`
#     2D y vector, which is required by `solve_ivp` inputs and outputs

# Note on the np.array family of functions:
# https://stackoverflow.com/a/52103839/1333978
# Basically, it can sometimes be important in this module whether a call to
# np.array() is copying something, or changing the dtype, etc.


class PEngine(object):
    """Physics Engine class. Encapsulates simulating physical state.

    Methods beginning with an underscore are not part of the API and change!

    Example usage:
    pe = PEngine(flight_savefile)
    state = pe.get_state()
    pe.set_time_acceleration(20)
    # Simulates 20 * [amount of time elapsed since last get_state() call]:
    state = pe.get_state()

    This class will start a background thread to simulate physics when __init__
    is called. This background thread may restart at arbitrary times.
    This class is designed to be access from the main thread by methods that
    don't begin with an underscore, so thread synchronization between the main
    thread and the background solutions thread is done with this assumption in
    mind. If this assumption changes, change thread synchronization code very
    deliberately and carefully! Specifically, if you're in spacesim, feel free
    to hit me (Patrick) up, and I can help.
    """

    def __init__(self, physical_state):
        # A PhysicalState, but no x, y, vx, or vy. That's handled by get_state.
        self._template_physical_state = protos.PhysicalState()

        # Controls access to self._solutions. If anything changes that is
        # related to self._solutions, this condition variable should be
        # notified. Currently, that's just if self._solutions or
        # self._last_simtime changes.
        self._solutions_cond = threading.Condition()
        self._solutions: collections.Deque
        self._last_monotime: float = time.monotonic()
        self._time_acceleration: float = common.DEFAULT_TIME_ACC
        self._simthread_exception: Exception = None

        self.set_state(physical_state)

    def set_time_acceleration(self, time_acceleration, requested_t=None):
        """Change the speed at which this PEngine simulates at."""
        self.handle_command(protos.Command(
            ident=protos.Command.TIME_ACC_SET, arg=time_acceleration))

    def _simtime(self, requested_t=None, *, peek_time=False):
        """Gets simulation time, accounting for time acceleration and passage.

        peek_time: if True, doesn't change any internal state. Use this as True
                   for internal log messages, and False for external APIs.
        """
        # During runtime, strange things will happen if you mix calling
        # this with None (like in flight.py) or with values (like in test.py)

        if requested_t is None:
            time_elapsed = max(
                time.monotonic() - self._last_monotime,
                0.0001
            )
            if not peek_time:
                self._last_monotime = time.monotonic()
            requested_t = (
                self._last_simtime + time_elapsed * self._time_acceleration)

        if not peek_time:
            with self._solutions_cond:
                self._last_simtime = requested_t
                self._solutions_cond.notify_all()

        return requested_t

    def _stop_simthread(self):
        if hasattr(self, '_simthread'):
            with self._solutions_cond:
                self._stopping_simthread = True
                self._solutions_cond.notify_all()
            self._simthread.join()

    def _restart_simulation(self, t0: float, y0: PhysicsState) -> None:
        self._stop_simthread()

        self._simthread = threading.Thread(
            target=self._simthread_target,
            args=(t0, y0),
            name=f'simthread {round(t0)}',
            daemon=True
        )
        self._stopping_simthread = False

        # We don't need to synchronize self._last_simtime or
        # self._solutions here, because we just stopped the background
        # simulation thread only a few lines ago.
        self._last_simtime = t0

        # Essentially just a cache of ODE solutions.
        self._solutions = collections.deque(maxlen=SOLUTION_CACHE_SIZE)

        # Fork self._simthread into the background.
        self._simthread.start()

    def set_control_craft_index(self, index):
        self.control_craft_index = index

    def handle_command(self, command, requested_t=None):
        """Interface to set habitat controls.

        Use an argument to change habitat throttle or spinning, and simulation
        will restart with this new information."""
        requested_t = self._simtime(requested_t)
        y0 = PhysicsState(None, self.get_state(requested_t))
        log.info(f'Got command for simtime t={requested_t}: {command}')

        # temp change before implementatin of spacestation
        control_craft_index = self._hab_index

        def launch():
            nonlocal y0
            # Make sure that we're slightly above the surface of an attachee
            # before un-attaching two entities
            attached_to = y0.AttachedTo
            if control_craft_index in attached_to.keys():
                ship = y0[control_craft_index]
                attachee = y0[attached_to[control_craft_index]]

                norm = ship.pos - attachee.pos
                unit_norm = norm / np.linalg.norm(norm)
                # This magic number is anything that is small to make much of
                # an effect, but positive so that a collision will be detected
                ship.pos = attachee.pos + unit_norm * (
                    common.LAUNCH_SEPARATION + attachee.r + ship.r)
                ship.attached_to = ''

                y0[control_craft_index] = ship

        if command.ident == protos.Command.HAB_SPIN_CHANGE:
            if control_craft_index not in y0.AttachedTo:
                hab = y0[control_craft_index]
                hab.spin += Habitat.spin_change(
                    requested_spin_change=command.arg)
                y0[control_craft_index] = hab
        elif command.ident == protos.Command.HAB_THROTTLE_CHANGE:
            launch()
            hab = y0[control_craft_index]
            hab.throttle += command.arg
            y0[control_craft_index] = hab
        elif command.ident == protos.Command.HAB_THROTTLE_SET:
            launch()
            hab = y0[control_craft_index]
            hab.throttle = command.arg
            y0[control_craft_index] = hab

        elif command.ident == protos.Command.TIME_ACC_SET:
            assert command.arg > 0
            self._time_acceleration = command.arg

        # Have to restart simulation when any controls are changed
        self._restart_simulation(requested_t, y0)

    def set_state(self, physical_state):
        self._artificials = np.where(
            np.array([
                entity.artificial
                for entity in physical_state.entities]) >= 1)[0]
        try:
            self._hab_index = [
                entity.name for entity in physical_state.entities
            ].index('Habitat')
        except ValueError:
            self._hab_index = 0

        try:
            self._spacestation_index = [
                entity.name for entity in physical_state.entities
            ].index('SpaceStation')
        except ValueError:
            self._spacestation_index = 0

        y0 = PhysicsState(None, physical_state)
        # We keep track of the PhysicalState because our simulation only
        # simulates things that change like position and velocity, not things
        # that stay constant like names and mass. self._last_physical_state
        # contains these constants.
        self._last_physical_state: protos.PhysicalState = physical_state
        self.R = np.array([entity.r for entity in physical_state.entities])
        self.M = np.array([entity.mass for entity in physical_state.entities])

        self._restart_simulation(physical_state.timestamp, y0)

    def _collision_decision(self, t, y, altitude_event):
        e1_index, e2_index = altitude_event(
            t, y.y0(), return_pair=True)
        e1 = y[e1_index]
        e2 = y[e2_index]

        log.info(f'Collision {t - self._simtime(peek_time=True)} seconds in '
                 f' the future, {e1} and {e2}')

        if (e2.attached_to is not "") or (e1.attached_to is not ""):
            log.info('Entities are attached, returning early')
            return e1, e2

        if e1.artificial:
            self._land(e1, e2)
        elif e2.artificial:
            self._land(e2, e1)
        else:
            self._bounce(e1, e2)

        y[e1_index] = e1
        y[e2_index] = e2
        return y

    def _bounce(self, e1, e2):
        # Resolve a collision by:
        # 1. calculating positions and velocities of the two entities
        # 2. do a 1D collision calculation along the normal between the two
        # 3. recombine the velocity vectors
        log.info(f'Bouncing {e1.name} and {e2.name}')
        norm = e1.pos - e2.pos
        unit_norm = norm / np.linalg.norm(norm)
        # The unit tangent is perpendicular to the unit normal vector
        unit_tang = np.asarray([-unit_norm[1], unit_norm[0]])

        # Calculate both normal and tangent velocities for both entities
        v1n = scipy.dot(unit_norm, e1.v)
        v1t = scipy.dot(unit_tang, e1.v)
        v2n = scipy.dot(unit_norm, e2.v)
        v2t = scipy.dot(unit_tang, e2.v)

        # Use https://en.wikipedia.org/wiki/Elastic_collision
        # to find the new normal velocities (a 1D collision)
        new_v1n = ((v1n * (e1.mass - e2.mass) + 2 * e2.mass * v2n) /
                   (e1.mass + e2.mass))
        new_v2n = ((v2n * (e2.mass - e1.mass) + 2 * e1.mass * v1n) /
                   (e1.mass + e2.mass))

        # Calculate new velocities
        e1.v = new_v1n * unit_norm + v1t * unit_tang
        e2.v = new_v2n * unit_norm + v2t * unit_tang

    def _land(self, e1, e2):
        # e1 is an artificial object
        # if 2 artificial object collide (habitat, spacespation)
        # or small astroid collision (need deletion), handle later
        log.info(f'Landing {e1.name} on {e2.name}')
        assert e2.artificial is False
        e1.attached_to = e2.name

        # Currently does nothing
        e1.broken = bool(
            np.linalg.norm(e1.v - e2.v) > e1.habitat_hull_strength)

        # set right heading for future takeoff
        norm = e1.pos - e2.pos
        e1.heading = np.arctan2(norm[1], norm[0])
        e1.throttle = 0
        e1.spin = e2.spin
        e1.v = e2.v

    def get_state(self, requested_t=None):
        """Return the latest physical state of the simulation."""
        requested_t = self._simtime(requested_t)

        # Wait until there is a solution for our requested_t. The .wait_for()
        # call will block until a new ODE solution is created.
        with self._solutions_cond:
            self._last_simtime = requested_t
            self._solutions_cond.wait_for(
                lambda:
                len(self._solutions) != 0 and
                self._solutions[-1].t_max >= requested_t or
                self._simthread_exception is not None
            )

            # Check if the simthread crashed
            if self._simthread_exception is not None:
                raise self._simthread_exception

            # We can't integrate backwards, so if integration has gone
            # beyond what we need, fail early.
            assert requested_t >= self._solutions[0].t_min

            for soln in self._solutions:
                if soln.t_min <= requested_t and requested_t <= soln.t_max:
                    solution = soln

        return PhysicsState(
            solution(requested_t), self._last_physical_state
        ).as_proto(requested_t)

    def _simthread_target(self, t, y):
        log.debug('simthread started')
        try:
            self._generate_new_ode_solutions(t, y)
        except Exception as e:
            log.exception('simthread got exception, forwarding to main thread')
            self._simthread_exception = e
        log.debug('simthread exited')

    def _derive(self, t: float, y_1d: np.ndarray,
                proto_state: protos.PhysicalState) -> np.ndarray:
        """
        y_1d =
         [X, Y, VX, VY, Heading, Spin, Fuel, Throttle, AttachedTo, Broken]
        returns the derivative of y_1d, i.e.
        [VX, VY, AX, AY, Spin, 0, Fuel consumption, 0, 0, 0]
        (zeroed-out fields are changed elsewhere)

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
        """
        y = PhysicsState(y_1d, proto_state)
        Xa, Ya = grav_acc(y.X, y.Y, self.M + y.Fuel)
        zeros = np.zeros(y._n)
        fuel_cons = np.zeros(y._n)

        for index in self._artificials:
            if y[index].fuel > 0:
                # We have fuel remaining, calculate thrust
                throttle = y[index].throttle
                fuel_cons[index] = - \
                    Habitat.fuel_cons(throttle=throttle)
                hab_eng_acc_x, hab_eng_acc_y = Habitat.acceleration(
                    throttle=throttle, heading=y[index].heading)
                Xa[index] += hab_eng_acc_x
                Ya[index] += hab_eng_acc_y

        # Keep attached entities glued together
        attached_to = y.AttachedTo
        for index in attached_to:
            attached = y[index]
            attachee = y[attached_to[index]]

            # If we're attached to something, make sure we move in lockstep.
            attached.v = attachee.v
            Xa[index] = Xa[attached_to[index]]
            Ya[index] = Ya[attached_to[index]]

            # We also add velocity and centripetal acceleration that comes
            # from being attached to the surface of a spinning object.
            norm = attached.pos - attachee.pos
            unit_norm = norm / np.linalg.norm(norm)
            # The unit tangent is perpendicular to the unit normal vector
            unit_tang = np.asarray([-unit_norm[1], unit_norm[0]])
            # These two lines courtesy of wikipedia "Circular motion"
            circular_velocity = unit_tang * attachee.spin * attachee.r
            centripetal_acc = unit_norm * attachee.spin ** 2 * attachee.r
            attached.v += circular_velocity
            y[index] = attached
            Xa[index] += centripetal_acc[0]
            Ya[index] += centripetal_acc[1]

        # for futur spacestation code
        # if y.Fuel[self._spacestation_index] > 0:
        #    # We have fuel remaining, calculate thrust
        #    throttle = y.Throttle[self._spacestation_index]
        #    fuel_cons[self._spacestation_index] = \
        #        -Habitat.fuel_cons(throttle=throttle)
        #    hab_eng_acc_x, hab_eng_acc_y = Habitat.acceleration(
        #        throttle=throttle,
        #        heading=y.Heading[self._spacestation_index])
        #    Xa[self._spacestation_index] += hab_eng_acc_x
        #    Ya[self._spacestation_index] += hab_eng_acc_y

        return np.concatenate((
            y.VX, y.VY, Xa, Ya, y.Spin,
            zeros, fuel_cons, zeros, zeros, zeros
        ), axis=None)

    def _generate_new_ode_solutions(self, t: float, y: PhysicsState) -> None:
        # An overview of how time is managed:
        #
        # self._last_simtime is the main thread's latest idea of
        # what the current time is in the simulation. Every call to
        # get_state(), self._timetime_of_last_request is incremented by the
        # amount of time that passed since the last call to get_state(),
        # factoring in self._time_acceleration.
        #
        # self._solutions is a fixed-size queue of ODE solutions.
        # Each element has an attribute, t_max, which describes the largest
        # time that the solution can be evaluated at and still be accurate.
        # The highest such t_max should always be larger than the current
        # simulation time, i.e. self._last_simtime
        proto_state = y._proto_state

        while not self._stopping_simthread:
            # self._solutions contains ODE solutions for the interval
            # [self._solutions[0].t_min, self._solutions[-1].t_max]
            # If we're in this function, requested_t is not in this interval!
            # Then we should integrate the interval of
            # [self._solutions[-1].t_max, requested_t]
            # and hopefully a bit farther past the end of that interval.
            hab_fuel_event = HabFuelEvent(proto_state)
            altitude_event = AltitudeEvent(proto_state, self.R)

            ivp_out = scipy.integrate.solve_ivp(
                functools.partial(self._derive, proto_state=proto_state),
                [t, t + self._time_acceleration],
                # solve_ivp requires a 1D y0 array
                y.y0(),
                events=[altitude_event, hab_fuel_event],
                # np.sqrt is here to give a slower-than-linear step size growth
                max_step=np.sqrt(self._time_acceleration),
                dense_output=True
            )

            if ivp_out.status < 0:
                # Integration error
                raise Exception(ivp_out.message)

            # When we create a new solution, let other people know.
            with self._solutions_cond:
                # If adding another solution to our max-sized deque would drop
                # our oldest solution, and the main thread is still asking for
                # state in the t interval of our oldest solution, take a break
                # until the main thread has caught up.
                self._solutions_cond.wait_for(
                    lambda:
                    len(self._solutions) < SOLUTION_CACHE_SIZE or
                    self._last_simtime > self._solutions[0].t_max or
                    self._stopping_simthread
                )
                if self._stopping_simthread:
                    break

                self._solutions.append(ivp_out.sol)
                self._solutions_cond.notify_all()

            y = PhysicsState(ivp_out.y[:, -1], proto_state)
            t = ivp_out.t[-1]

            if ivp_out.status > 0:
                log.debug(f'Got event: {ivp_out.t_events}')
                if len(ivp_out.t_events[0]):
                    # Collision, simulation ended. Handled it and continue.
                    assert len(ivp_out.t_events[0]) == 1
                    assert len(ivp_out.t) >= 2
                    y = self._collision_decision(t, y, altitude_event)
                elif len(ivp_out.t_events[1]):
                    log.debug(f'Got fuel empty at {t}')

                    for index in self._artificials:
                        artificial = y[index]
                        # Habitat's out of fuel, the next iteration won't
                        # consume any fuel. Set throttle to zero anyway.
                        artificial.throttle = 0
                        # Set fuel to a negative value, so it doesn't trigger
                        # the event function
                        artificial.fuel = 0
                        y[index] = artificial


class Event:
    # These two fields tell scipy to stop simulation when __call__ returns 0
    terminal = True
    direction = -1

    # Implement this in an event subclass
    def __call___(self, t: float, y_1d: np.ndarray) -> float:
        raise NotImplemented


class HabFuelEvent(Event):
    def __init__(self, proto_state: protos.PhysicalState):
        self.proto_state = proto_state

    def __call__(self, t, y_1d) -> float:
        """Return a 0 only when throttle is nonzero."""
        y = PhysicsState(y_1d, self.proto_state)
        for index, entity in enumerate(y._proto_state.entities):
            if entity.artificial and y.Throttle[index] != 0:
                return y.Fuel[index]
        return 1


class AltitudeEvent(Event):
    def __init__(self, proto_state: protos.PhysicalState, radii: np.ndarray):
        self.proto_state = proto_state
        self.radii = radii

    def __call__(self, t, y_1d, return_pair=False
                 ) -> Union[float, Tuple[int, int]]:
        """An event function. See numpy documentation for solve_ivp.

        Returns a scalar, with 0 indicating a collision and a sign change
            indicating a collision has happened.
        """
        y = PhysicsState(y_1d, self.proto_state)
        n = len(self.proto_state.entities)
        # 2xN of (x, y) positions
        posns = np.column_stack((y.X, y.Y))
        # An n*n matrix of _altitudes_ between each entity
        alt_matrix = (
            scipy.spatial.distance.cdist(posns, posns) -
            np.array([self.radii]) - np.array([self.radii]).T)
        # To simplify calculations, an entity's altitude from itself is inf
        np.fill_diagonal(alt_matrix, np.inf)
        # For each pair of objects that have collisions disabled between
        # them, also set their altitude to be inf

        # If there are any entities attached to any other entities, ignore
        # both the attachee and the attached entity.
        attached_to = y.AttachedTo
        for index in attached_to:
            alt_matrix[index, attached_to[index]] = np.inf
            alt_matrix[attached_to[index], index] = np.inf

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

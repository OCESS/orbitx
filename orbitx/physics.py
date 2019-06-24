import collections
import functools
import logging
import threading
import time
import warnings
from typing import Optional, Tuple, Union

import numpy as np
import scipy.integrate
import scipy.spatial
import scipy.special

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.network import Request
from orbitx.orbitx_pb2 import PhysicalState

SOLUTION_CACHE_SIZE = 10

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


class PEngine:
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

    def __init__(self, physical_state: state.PhysicsState):
        # Controls access to self._solutions. If anything changes that is
        # related to self._solutions, this condition variable should be
        # notified. Currently, that's just if self._solutions or
        # self._last_simtime changes.
        self._solutions_cond = threading.Condition()
        self._solutions: collections.deque
        self._last_monotime: float = time.monotonic()
        self._simthread: Optional[threading.Thread] = None
        self._simthread_exception: Optional[Exception] = None
        self._last_physical_state: state.protos.PhysicalState

        self.set_state(physical_state)

    def set_time_acceleration(self, time_acceleration, requested_t=None):
        """Change the speed at which this PEngine simulates at."""
        self.handle_request(Request(
            ident=Request.TIME_ACC_SET, time_acc_set=time_acceleration))

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
                self._last_simtime +
                time_elapsed * self._last_physical_state.time_acc
            )

        if not peek_time:
            with self._solutions_cond:
                self._last_simtime = requested_t
                self._solutions_cond.notify_all()

        return requested_t

    def _stop_simthread(self):
        if self._simthread is not None:
            with self._solutions_cond:
                self._stopping_simthread = True
                self._solutions_cond.notify_all()
            self._simthread.join()

    def _restart_simulation(self, t0: float, y0: state.PhysicsState) -> None:
        self._stop_simthread()

        if y0.time_acc == 0:
            # We've paused the simulation. Don't start a new simthread
            return

        # We don't need to synchronize self._last_simtime or
        # self._solutions here, because we just stopped the background
        # simulation thread only a few lines ago.
        self._last_simtime = t0

        # Essentially just a cache of ODE solutions.
        self._solutions = collections.deque(maxlen=SOLUTION_CACHE_SIZE)

        self._simthread = threading.Thread(
            target=self._simthread_target,
            args=(t0, y0),
            name=f'simthread t={round(t0)} acc={y0.time_acc}',
            daemon=True
        )
        self._stopping_simthread = False

        # Fork self._simthread into the background.
        self._simthread.start()

    def handle_request(self, request: Request, requested_t=None):
        """Interface to set habitat controls.

        Use an argument to change habitat throttle or spinning, and simulation
        will restart with this new information."""
        if request.ident == Request.NOOP:
            # We don't care about these requests
            return
        requested_t = self._simtime(requested_t)
        log.info(f'Got command at simtime={requested_t}')

        if request.ident == Request.TIME_ACC_SET:
            # Immediately change the time acceleration, don't wait for the
            # simulation to catch up. This deals with the case where we're at
            # 100,000x time acc, and the program seems frozen for the user and
            # they try lowering time acc. We should immediately be able to
            # restart simulation at a lower time acc without any waiting.
            requested_t = min(self._solutions[-1].t_max, requested_t)

        y0 = self.get_state(requested_t)

        if request.ident == Request.HAB_SPIN_CHANGE:
            if y0.navmode != state.Navmode['Manual']:
                # We're in autopilot, ignore this command
                return
            craft = y0[y0.craft]
            if not craft.landed():
                # TODO: on the next line, not every craft is a hab.
                craft.spin += state.Habitat.spin_change(
                    requested_spin_change=request.spin_change)
                y0[y0.craft] = craft
        elif request.ident == Request.HAB_THROTTLE_CHANGE:
            craft = y0[y0.craft]
            craft.throttle += request.throttle_change
            y0[y0.craft] = craft
        elif request.ident == Request.HAB_THROTTLE_SET:
            craft = y0[y0.craft]
            craft.throttle = request.throttle_set
            y0[y0.craft] = craft
        elif request.ident == Request.TIME_ACC_SET:
            assert request.time_acc_set >= 0
            y0.time_acc = request.time_acc_set
        elif request.ident == Request.ENGINEERING_UPDATE:
            # Multiply this value by 100, because OrbitV considers engines at
            # 100% to be 100x the maximum thrust.
            state.Habitat.engine.max_thrust = \
                100 * request.engineering_update.max_thrust
            hab = y0[common.HABITAT]
            ayse = y0[common.AYSE]
            hab.fuel = request.engineering_update.hab_fuel
            ayse.fuel = request.engineering_update.ayse_fuel
            y0[common.HABITAT] = hab
            y0[common.AYSE] = ayse
        elif request.ident == Request.UNDOCK:
            habitat = y0[common.HABITAT]

            if habitat.landed_on == common.AYSE:
                ayse = y0[common.AYSE]
                habitat.landed_on = ''

                norm = habitat.pos - ayse.pos
                unit_norm = norm / np.linalg.norm(norm)
                habitat.v += unit_norm * 1  # Give a 1 m/s push

                y0[common.HABITAT] = habitat

        elif request.ident == Request.REFERENCE_UPDATE:
            y0.reference = request.reference
        elif request.ident == Request.TARGET_UPDATE:
            y0.target = request.target
        elif request.ident == Request.LOAD_SAVEFILE:
            y0 = common.load_savefile(common.savefile(request.loadfile))
        elif request.ident == Request.NAVMODE_SET:
            y0.navmode = state.Navmode(request.navmode)
            if y0.navmode == state.Navmode['Manual']:
                craft = y0[y0.craft]
                craft.spin = 0
                y0[y0.craft] = craft

        self.set_state(y0)

    def set_state(self, physical_state: state.PhysicsState):
        self._artificials = np.where(
            np.array([
                entity.artificial
                for entity in physical_state]) >= 1)[0]

        # We keep track of the PhysicalState because our simulation only
        # simulates things that change like position and velocity, not things
        # that stay constant like names and mass. self._last_physical_state
        # contains these constants.
        self._last_physical_state = physical_state._proto_state
        self.R = np.array([entity.r for entity in physical_state])
        self.M = np.array([entity.mass for entity in physical_state])

        self._restart_simulation(physical_state.timestamp, physical_state)

    def _collision_decision(self, t, y, altitude_event):
        e1_index, e2_index = altitude_event(
            t, y.y0(), return_pair=True)
        e1 = y[e1_index]
        e2 = y[e2_index]

        log.info(f'Collision {t - self._simtime(peek_time=True)} seconds in '
                 f' the future, {e1} and {e2}')

        # TODO: does this break three-body collisions? e.g. both Hab and AYSE
        # or does it even get triggered at all?
        if e2.landed_on or e1.landed_on:
            log.info('Entities are landed, returning early')
            return e1, e2

        if e1.artificial:
            if e2.artificial:
                if e2.dockable:
                    self._docking(e1, e2, e2_index)
                elif e1.dockable:
                    self._docking(e2, e1, e1_index)
                else:
                    self._bounce(e1, e2)
            else:
                self._land(e1, e2)
        elif e2.artificial:
            self._land(e2, e1)
        else:
            self._bounce(e1, e2)

        y[e1_index] = e1
        y[e2_index] = e2
        return y

    def _docking(self, e1, e2, e2_index):
        # e1 is an artificial object
        # if 2 artificial object to be docked on (spacespation)

        norm = e1.pos - e2.pos
        collision_angle = np.arctan2(norm[1], norm[0])
        collision_angle = collision_angle % (2 * np.pi)

        ANGLE_MIN = (e2.heading + 0.7 * np.pi) % (2 * np.pi)
        ANGLE_MAX = (e2.heading + 1.3 * np.pi) % (2 * np.pi)

        if collision_angle < ANGLE_MIN or collision_angle > ANGLE_MAX:
            # add damage ?
            self._bounce(e1, e2)
            return

        log.info(f'Docking {e1.name} on {e2.name}')
        e1.landed_on = e2.name

        # Currently does nothing
        e1.broken = bool(
            np.linalg.norm(e1.v - e2.v) > e1.habitat_hull_strength)

        # set right heading for future takeoff
        e2_opposite = e2.heading + np.pi
        e1.pos = [np.cos(e2_opposite) * e2.r + e2.pos[0],
                  np.sin(e2_opposite) * e2.r + e2.pos[1]]
        e1.heading = (e2_opposite) % (2 * np.pi)
        e1.throttle = 0
        e1.spin = 0
        e1.v = e2.v

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
        e1.landed_on = e2.name

        # Currently does nothing
        e1.broken = bool(
            np.linalg.norm(e1.v - e2.v) > e1.habitat_hull_strength)

        # set right heading for future takeoff
        norm = e1.pos - e2.pos
        e1.heading = np.arctan2(norm[1], norm[0])
        e1.throttle = 0
        e1.spin = e2.spin
        e1.v = calc.rotational_speed(e1, e2)

    def get_state(self, requested_t=None) -> state.PhysicsState:
        """Return the latest physical state of the simulation."""
        requested_t = self._simtime(requested_t)

        # Wait until there is a solution for our requested_t. The .wait_for()
        # call will block until a new ODE solution is created.
        with self._solutions_cond:
            self._last_simtime = requested_t
            self._solutions_cond.wait_for(
                lambda:
                (len(self._solutions) != 0 and
                 self._solutions[-1].t_max >= requested_t) or
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

        newest_state = state.PhysicsState(
            solution(requested_t), self._last_physical_state
        )
        newest_state.timestamp = requested_t

        return newest_state

    def _simthread_target(self, t, y):
        try:
            self._run_simulation(t, y)
        except Exception as e:
            log.exception('simthread got exception, forwarding to main thread')
            self._simthread_exception = e
            with self._solutions_cond:
                self._solutions_cond.notify_all()

    def _derive(self, t: float, y_1d: np.ndarray,
                pass_through_state: PhysicalState) -> np.ndarray:
        """
        y_1d =
         [X, Y, VX, VY, Heading, Spin, Fuel, Throttle, LandedOn, Broken]
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
        # Note: we create this y as a PhysicsState for convenience, but if you
        # set any values of y, the changes will be discarded! The only way they
        # will be propagated out of this function is by numpy using the return
        # value of this function as a derivative, as explained above.
        y = state.PhysicsState(y_1d, pass_through_state)
        Ax, Ay = calc.grav_acc(y.X, y.Y, self.M + y.Fuel)
        zeros = np.zeros(y._n)
        fuel_cons = np.zeros(y._n)

        for index in self._artificials:
            if y[index].fuel > 0:
                # We have fuel remaining, calculate thrust
                entity = y[index]
                fuel_cons[index] = -state.Habitat.fuel_cons(
                    throttle=entity.throttle)
                hab_eng_acc_x, hab_eng_acc_y = (
                    state.Habitat.thrust(
                        throttle=entity.throttle, heading=entity.heading) /
                    (entity.mass + entity.fuel)
                )
                Ax[index] += hab_eng_acc_x
                Ay[index] += hab_eng_acc_y

        if y.navmode != state.Navmode['Manual']:
            craft = y.craft_entity()
            craft.spin = calc.navmode_spin(y)
            y[y.craft] = craft

        try:
            craft_index = y._name_to_index(y.craft)
            drag_acc = calc.drag(y)
            Ax[craft_index] -= drag_acc[0]
            Ay[craft_index] -= drag_acc[1]
        except state.PhysicsState.NoEntityError:
            pass

        # Keep landed entities glued together
        landed_on = y.LandedOn
        for index in landed_on:
            # If we're landed on something, make sure we move in lockstep.
            lander = y[index]
            ground = y[landed_on[index]]

            lander.spin = ground.spin
            lander.v = calc.rotational_speed(lander, ground)
            y[index] = lander

            # We also centripetal acceleration that comes
            # from being landed on the surface of a spinning object.
            centripetal_acc = (lander.pos - ground.pos) * ground.spin ** 2
            Ax[index] = Ax[landed_on[index]] - centripetal_acc[0]
            Ay[index] = Ay[landed_on[index]] - centripetal_acc[1]

        return np.concatenate((
            y.VX, y.VY, Ax, Ay, y.Spin,
            zeros, fuel_cons, zeros, zeros, zeros
        ), axis=None)

    def _run_simulation(self, t: float, y: state.PhysicsState) -> None:
        # An overview of how time is managed:
        #
        # self._last_simtime is the main thread's latest idea of
        # what the current time is in the simulation. Every call to
        # get_state(), self._timetime_of_last_request is incremented by the
        # amount of time that passed since the last call to get_state(),
        # factoring in time_acc
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
            hab_fuel_event = HabFuelEvent(y)
            altitude_event = AltitudeEvent(y, self.R)
            liftoff_event = LiftoffEvent(y)

            ivp_out = scipy.integrate.solve_ivp(
                functools.partial(
                    self._derive, pass_through_state=proto_state),
                # np.sqrt is here to give a slower-than-linear step size growth
                [t, t + np.sqrt(y.time_acc)],
                # solve_ivp requires a 1D y0 array
                y.y0(),
                events=[altitude_event, hab_fuel_event, liftoff_event],
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

            y = state.PhysicsState(ivp_out.y[:, -1], proto_state)
            t = ivp_out.t[-1]

            if ivp_out.status > 0:
                log.info(f'Got event: {ivp_out.t_events}')
                if len(ivp_out.t_events[0]):
                    # Collision, simulation ended. Handled it and continue.
                    assert len(ivp_out.t_events[0]) == 1
                    assert len(ivp_out.t) >= 2
                    y = self._collision_decision(t, y, altitude_event)
                if len(ivp_out.t_events[1]):
                    log.info(f'Got fuel empty at {t}')

                    for index in self._artificials:
                        artificial = y[index]
                        # Habitat's out of fuel, the next iteration won't
                        # consume any fuel. Set throttle to zero anyway.
                        artificial.throttle = 0
                        # Set fuel to a negative value, so it doesn't trigger
                        # the event function
                        artificial.fuel = 0
                        y[index] = artificial
                if len(ivp_out.t_events[2]):
                    craft = y.craft_entity()
                    log.info('We have liftoff of the '
                             f'{craft.name} from {craft.landed_on} at {t}')
                    craft.landed_on = ''
                    y[y.craft] = craft


class Event:
    """Implements an event function. See numpy documentation for solve_ivp."""
    # These two fields tell scipy to stop simulation when __call__ returns 0
    terminal = True
    direction = -1

    # Implement this in an event subclass
    def __call___(self, t: float, y_1d: np.ndarray) -> float:
        raise NotImplementedError


class HabFuelEvent(Event):
    def __init__(self, initial_state: state.PhysicsState):
        self.initial_state = initial_state

    def __call__(self, t, y_1d) -> float:
        """Return a 0 only when throttle is nonzero."""
        y = state.PhysicsState(y_1d, self.initial_state._proto_state)
        for index, entity in enumerate(y._proto_state.entities):
            if entity.artificial and y.Throttle[index] != 0:
                return y.Fuel[index]
        return np.inf


class AltitudeEvent(Event):
    def __init__(self, initial_state: state.PhysicsState, radii: np.ndarray):
        self.initial_state = initial_state
        self.radii = radii

    def __call__(self, t, y_1d, return_pair=False
                 ) -> Union[float, Tuple[int, int]]:
        """Returns a scalar, with 0 indicating a collision and a sign change
        indicating a collision has happened."""
        y = state.PhysicsState(y_1d, self.initial_state._proto_state)
        n = len(self.initial_state)
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
    def __init__(self, initial_state: state.PhysicsState):
        self.initial_state = initial_state

    def __call__(self, t, y_1d) -> float:
        """Return 0 when the craft is landed but thrusting enough to lift off,
        and a positive value otherwise."""
        y = state.PhysicsState(y_1d, self.initial_state._proto_state)
        try:
            craft = y.craft_entity()
        except state.PhysicsState.NoEntityError:
            # There is no craft, return early.
            return np.inf

        if not craft.landed():
            # We don't have to lift off because we already lifted off.
            return np.inf

        planet = y[craft.landed_on]
        if planet.artificial:
            # If we're docked with another satellite, undocking is governed
            # by other mechanisms. Ignore this.
            return np.inf

        thrust = np.linalg.norm(state.Habitat.thrust(
            throttle=craft.throttle, heading=craft.heading))
        pos = craft.pos - planet.pos
        # This is the G(m1*m2)/r^2 formula
        weight = common.G * craft.mass * planet.mass / np.inner(pos, pos)

        # This should be positive when the craft isn't thrusting enough, and
        # zero when it is thrusting enough.
        return max(0, common.LAUNCH_TWR - thrust / weight)

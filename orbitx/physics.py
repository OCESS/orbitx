import collections
import functools
import logging
import math
import threading
import time
import warnings
from typing import Callable, List, Optional, Tuple, NamedTuple, Union

import numpy as np
import scipy.integrate
import scipy.spatial
import scipy.special
from google.protobuf.text_format import MessageToString

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.network import Request
from orbitx.orbitx_pb2 import PhysicalState

SOLUTION_CACHE_SIZE = 2

warnings.simplefilter('error')  # Raise exception on numpy RuntimeWarning
scipy.special.seterr(all='raise')
log = logging.getLogger()


TIME_ACC_TO_BOUND = {time_acc.value: time_acc.accurate_bound
                     for time_acc in common.TIME_ACCS}


class TimeAccChange(NamedTuple):
    """Describes when the time acc of the simulation changes, and what to."""
    time_acc: float
    start_simtime: float


class PEngine:
    """Physics Engine class. Encapsulates simulating physical state.

    Methods beginning with an underscore are not part of the API and change!

    Example usage:
    pe = PEngine(flight_savefile)
    state = pe.get_state()
    pe.handle_request(Request(ident=..., ...))  # Change some state.
    # Simulates 20 seconds:
    state = pe.get_state(requested_t=20)

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

        self._simthread: Optional[threading.Thread] = None
        self._simthread_exception: Optional[Exception] = None
        self._last_physical_state: state.protos.PhysicalState
        self._last_monotime: float = time.monotonic()
        self._last_simtime: float
        self._time_acc_changes: collections.deque

        self.set_state(physical_state)

    def _simtime(self, requested_t=None):
        """Gets simulation time, accounting for time acc and elapsed time."""
        # During runtime, strange things will happen if you mix calling
        # this with None (like from orbitx.py) or with values (like in test.py)
        if requested_t is None:
            # "Alpha time" refers to time in the real world
            # (just as the spacesim wiki defines it).
            alpha_time_elapsed = max(
                time.monotonic() - self._last_monotime,
                0.0001
            )
            self._last_monotime = time.monotonic()

            simtime = self._last_simtime

            assert self._time_acc_changes
            # This while loop will increment simtime and decrement
            # time_elapsed correspondingly until the second time acc change
            # starts farther in the future than we will increment simtime.
            while len(self._time_acc_changes) > 1 and \
                self._time_acc_changes[1].start_simtime < (
                simtime + self._time_acc_changes[0].time_acc *
                    alpha_time_elapsed):
                remaining_simtime = \
                    self._time_acc_changes[1].start_simtime - simtime
                simtime = self._time_acc_changes[1].start_simtime
                alpha_time_elapsed -= \
                    remaining_simtime / self._time_acc_changes[0].time_acc
                # We've advanced past self._time_acc_changes[0],
                # we can forget it now.
                self._time_acc_changes.popleft()

            # Now we will just advance partway into the span of time
            # between self._time_acc_changes[0].startime and [1].startime.
            simtime += alpha_time_elapsed * self._time_acc_changes[0].time_acc
            requested_t = simtime

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

    def _start_simthread(self, t0: float, y0: state.PhysicsState) -> None:
        if round(y0.time_acc) == 0:
            # We've paused the simulation. Don't start a new simthread
            log.debug('Pausing simulation')
            return

        # We don't need to synchronize self._last_simtime or
        # self._solutions here, because we just stopped the background
        # simulation thread only a few lines ago.
        self._last_simtime = t0
        # This double-ended queue should always have at least one element in
        # it, and the first element should have a start_simtime less
        # than self._last_simtime.
        self._time_acc_changes = collections.deque(
            [TimeAccChange(time_acc=y0.time_acc,
             start_simtime=y0.timestamp)]
        )

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

    def handle_requests(self, requests: List[Request], requested_t=None):
        requested_t = self._simtime(requested_t)
        if len(requests) == 0:
            return

        if len(requests) and requests[0].ident == Request.TIME_ACC_SET:
            # Immediately change the time acceleration, don't wait for the
            # simulation to catch up. This deals with the case where we're at
            # 100,000x time acc, and the program seems frozen for the user and
            # they try lowering time acc. We should immediately be able to
            # restart simulation at a lower time acc without any waiting.
            if len(self._solutions) == 0:
                # We haven't even simulated any solutions yet.
                requested_t = self._last_physical_state.timestamp
            else:
                requested_t = min(self._solutions[-1].t_max, requested_t)

        if len(self._solutions) == 0:
            y0 = state.PhysicsState(None, self._last_physical_state)
        else:
            y0 = self.get_state(requested_t)

        for request in requests:
            if request.ident == Request.NOOP:
                # We don't care about these requests
                continue
            y0 = _one_request(request, y0)
            if request.ident == Request.TIME_ACC_SET:
                assert request.time_acc_set >= 0
                self._time_acc_changes.append(
                    TimeAccChange(time_acc=y0.time_acc,
                                  start_simtime=y0.timestamp)
                )

        self.set_state(y0)

    def set_state(self, physical_state: state.PhysicsState):
        self._stop_simthread()

        physical_state = _reconcile_entity_dynamics(physical_state)
        self._artificials = np.where(
            np.array([
                entity.artificial
                for entity in physical_state]) >= 1)[0]

        # We keep track of the PhysicalState because our simulation
        # only simulates things that change like position and velocity,
        # not things that stay constant like names and mass.
        # self._last_physical_state contains these constants.
        self._last_physical_state = physical_state.as_proto()
        self.R = np.array([entity.r for entity in physical_state])
        self.M = np.array([entity.mass for entity in physical_state])

        self._start_simthread(physical_state.timestamp, physical_state)

    def get_state(self, requested_t=None) -> state.PhysicsState:
        """Return the latest physical state of the simulation."""
        requested_t = self._simtime(requested_t)

        # Wait until there is a solution for our requested_t. The .wait_for()
        # call will block until a new ODE solution is created.
        with self._solutions_cond:
            self._last_simtime = requested_t
            self._solutions_cond.wait_for(
                # Wait until we're paused, there's a solution, or an exception.
                lambda:
                self._last_physical_state.time_acc == 0 or
                (len(self._solutions) != 0 and
                 self._solutions[-1].t_max >= requested_t) or
                self._simthread_exception is not None
            )

            # Check if the simthread crashed
            if self._simthread_exception is not None:
                raise self._simthread_exception

            if self._last_physical_state.time_acc == 0:
                # We're paused, so there are no solutions being generated.
                # Exit this 'with' block and release our _solutions_cond lock.
                pass
            else:
                # We can't integrate backwards, so if integration has gone
                # beyond what we need, fail early.
                assert requested_t >= self._solutions[0].t_min

                for soln in self._solutions:
                    if soln.t_min <= requested_t and requested_t <= soln.t_max:
                        solution = soln

        if self._last_physical_state.time_acc == 0:
            # We're paused, so return the only state we have.
            return state.PhysicsState(None, self._last_physical_state)
        else:
            # We have a solution, return it.
            newest_state = state.PhysicsState(
                solution(requested_t), self._last_physical_state
            )
            newest_state.timestamp = requested_t
            return newest_state

    class RestartSimulationException(Exception):
        """A request to restart the simulation with new t and y."""
        def __init__(self, t: float, y: state.PhysicsState):
            self.t = t
            self.y = y

    def _simthread_target(self, t, y):
        while True:
            try:
                self._run_simulation(t, y)
                if self._stopping_simthread:
                    return
            except PEngine.RestartSimulationException as e:
                t = e.t
                y = e.y
                log.info(f'Simulation restarted itself at {t}.')
            except Exception as e:
                log.error(f'simthread got exception {repr(e)}.')
                self._simthread_exception = e
                with self._solutions_cond:
                    self._solutions_cond.notify_all()
                return

    def _derive(self, t: float, y_1d: np.ndarray,
                pass_through_state: PhysicalState) -> np.ndarray:
        """
        y_1d =
         [X, Y, VX, VY, Heading, Spin, Fuel, Throttle, LandedOn, Broken] +
         SRB_time_left + time_acc (these are both single values)
        returns the derivative of y_1d, i.e.
        [VX, VY, AX, AY, Spin, 0, Fuel consumption, 0, 0, 0] + -constant + 0
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
        # If you want to set values in y, look at _reconcile_entity_dynamics.
        y = state.PhysicsState(y_1d, pass_through_state)
        Ax, Ay = calc.grav_acc(y.X, y.Y, self.M + y.Fuel)
        zeros = np.zeros(y._n)
        fuel_cons = np.zeros(y._n)

        # Engine thrust and fuel consumption
        for index in self._artificials:
            if y[index].fuel > 0 and y[index].throttle > 0:
                # We have fuel remaining, calculate thrust
                entity = y[index]
                capability = common.craft_capabilities[entity.name]

                fuel_cons[index] = -abs(capability.fuel_cons * entity.throttle)
                eng_thrust = capability.thrust * entity.throttle * \
                    calc.heading_vector(entity.heading)
                mass = entity.mass + entity.fuel

                if entity.name == common.AYSE and \
                        y[common.HABITAT].landed_on == common.AYSE:
                    # It's bad that this is hardcoded, but it's also the only
                    # place that this comes up so IMO it's not too bad.
                    hab = y[common.HABITAT]
                    mass += hab.mass + hab.fuel

                eng_acc = eng_thrust / mass
                Ax[index] += eng_acc[0]
                Ay[index] += eng_acc[1]

        # And SRB thrust
        srb_usage = 0
        try:
            if y.srb_time >= 0:
                hab_index = y._name_to_index(common.HABITAT)
                hab = y[hab_index]
                srb_acc = common.SRB_THRUST / (hab.mass + hab.fuel)
                srb_acc_vector = srb_acc * calc.heading_vector(hab.heading)
                Ax[hab_index] += srb_acc_vector[0]
                Ay[hab_index] += srb_acc_vector[1]
                srb_usage = -1
        except state.PhysicsState.NoEntityError:
            # The Habitat doesn't exist.
            pass

        # Drag effects
        craft = y.craft
        if craft is not None:
            craft_index = y._name_to_index(y.craft)
            drag_acc = calc.drag(y)
            Ax[craft_index] -= drag_acc[0]
            Ay[craft_index] -= drag_acc[1]

        # Centripetal acceleration to keep landed entities glued to each other.
        landed_on = y.LandedOn
        for index in landed_on:
            lander = y[index]
            ground = y[landed_on[index]]

            centripetal_acc = (lander.pos - ground.pos) * ground.spin ** 2
            Ax[index] = Ax[landed_on[index]] - centripetal_acc[0]
            Ay[index] = Ay[landed_on[index]] - centripetal_acc[1]

        # Sets velocity and spin of a couple more entities.
        # If you want to set the acceleration of an entity, do it above and
        # keep that logic in _derive. If you want to set the velocity and spin
        # or any other fields that an Entity has, you should put that logic in
        # this _reconcile_entity_dynamics helper.
        y = _reconcile_entity_dynamics(y)

        return np.concatenate((
            y.VX, y.VY, Ax, Ay, y.Spin,
            zeros, fuel_cons, zeros, zeros, zeros, np.array([srb_usage, 0])
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
            derive_func = functools.partial(
                self._derive, pass_through_state=proto_state)

            events: List[Event] = [
                CollisionEvent(y, self.R), HabFuelEvent(y), LiftoffEvent(y),
                SrbFuelEvent()
            ]
            if y.craft is not None:
                craft_index = y._name_to_index(y.craft)
                events.append(HighAccEvent(derive_func,
                              2 * len(y) + craft_index,
                              3 * len(y) + craft_index,
                              TIME_ACC_TO_BOUND[round(y.time_acc)],
                              y.time_acc))

            ivp_out = scipy.integrate.solve_ivp(
                derive_func,
                # math.pow is here to give a sub-linear step size growth.
                [t, t + math.pow(y.time_acc, 1/1.2)],
                # solve_ivp requires a 1D y0 array
                y.y0(),
                events=events,
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

                # self._solutions contains ODE solutions for the interval
                # [self._solutions[0].t_min, self._solutions[-1].t_max].
                self._solutions.append(ivp_out.sol)
                self._solutions_cond.notify_all()

            y = state.PhysicsState(ivp_out.y[:, -1], proto_state)
            t = ivp_out.t[-1]

            if ivp_out.status > 0:
                log.info(f'Got event: {ivp_out.t_events} at t={t}.')
                for index, event_t in enumerate(ivp_out.t_events):
                    if len(event_t) == 0:
                        # If this event didn't occur, then event_t == []
                        continue
                    event = events[index]
                    if isinstance(event, CollisionEvent):
                        # Collision, simulation ended. Handled it and continue.
                        assert len(ivp_out.t_events[0]) == 1
                        assert len(ivp_out.t) >= 2
                        y = _collision_decision(t, y, events[0])
                        y = _reconcile_entity_dynamics(y)
                    if isinstance(event, HabFuelEvent):
                        # Something ran out of fuel.
                        for index in self._artificials:
                            artificial = y[index]
                            if round(artificial.fuel) != 0:
                                continue
                            log.info(f'{artificial.name} ran out of fuel.')
                            # This craft is out of fuel, the next iteration
                            # won't consume any fuel. Set throttle to zero.
                            artificial.throttle = 0
                            # Set fuel to a negative value, so it doesn't
                            # trigger the event function.
                            artificial.fuel = 0
                    if isinstance(event, LiftoffEvent):
                        # A craft has a TWR > 1
                        craft = y.craft_entity()
                        log.info(
                            'We have liftoff of the '
                            f'{craft.name} from {craft.landed_on} at {t}.')
                        craft.landed_on = ''
                    if isinstance(event, SrbFuelEvent):
                        # SRB fuel exhaustion.
                        log.info('SRB exhausted.')
                        y.srb_time = common.SRB_EMPTY
                    if isinstance(event, HighAccEvent):
                        # The acceleration acting on the craft is high, might
                        # result in inaccurate results. SLOOWWWW DOWWWWNNNN.
                        slower_time_acc_index = list(
                            TIME_ACC_TO_BOUND.keys()
                        ).index(round(y.time_acc)) - 1
                        assert slower_time_acc_index >= 0
                        slower_time_acc = \
                            common.TIME_ACCS[slower_time_acc_index]
                        assert slower_time_acc.value > 0
                        log.info(
                            f'{y.time_acc} is too fast, '
                            f'slowing down to {slower_time_acc.value}')
                        # We should lower the time acc.
                        y.time_acc = slower_time_acc.value
                        raise PEngine.RestartSimulationException(t, y)


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
        return y_1d[state.PhysicsState.SRB_TIME_INDEX]


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


class CollisionEvent(Event):
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
        if y.srb_time > 0 and y.craft == common.HABITAT:
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
        ax_index: int, ay_index: int, acc_bound: float, current_acc: float
            ):
        self.derive = derive
        self.ax_index = ax_index
        self.ay_index = ay_index
        self.acc_bound = acc_bound
        self.current_acc = round(current_acc)

    def __call__(self, t: float, y_1d: np.ndarray) -> float:
        """Return positive if the current time acceleration is accurate, zero
        then negative otherwise."""
        if self.current_acc == 1:
            # If we can't lower the time acc, don't bother doing any work.
            return np.inf
        derive_result = self.derive(t, y_1d)
        accel_vector = np.array(
            [derive_result[self.ax_index], derive_result[self.ay_index]])
        acc = np.linalg.norm(accel_vector)
        return self.acc_bound - acc


def _reconcile_entity_dynamics(y: state.PhysicsState) -> state.PhysicsState:
    """Idempotent helper that sets velocities and spins of some entities.
    This is in its own function because it has a couple calling points."""
    # Navmode auto-rotation
    if y.navmode != state.Navmode['Manual']:
        craft = y.craft_entity()
        craft.spin = calc.navmode_spin(y)

    # Keep landed entities glued together
    landed_on = y.LandedOn
    for index in landed_on:
        # If we're landed on something, make sure we move in lockstep.
        lander = y[index]
        ground = y[landed_on[index]]

        if ground.name == common.AYSE and lander.name == common.HABITAT:
            # Always put the Habitat at the docking port.
            lander.pos = ground.pos - \
                calc.heading_vector(ground.heading) * (lander.r + ground.r)
        else:
            norm = lander.pos - ground.pos
            unit_norm = norm / np.linalg.norm(norm)
            lander.pos = ground.pos + unit_norm * (ground.r + lander.r)

        lander.spin = ground.spin
        lander.v = calc.rotational_speed(lander, ground)

    return y


def _collision_decision(t, y, altitude_event):
    e1_index, e2_index = altitude_event(
        t, y.y0(), return_pair=True)
    e1 = y[e1_index]
    e2 = y[e2_index]

    log.info(f'Collision at t={t} betwixt {e1.name} and {e2.name}')

    if e1.artificial:
        if e2.artificial:
            if e2.dockable:
                _docking(e1, e2, e2_index)
            elif e1.dockable:
                _docking(e2, e1, e1_index)
            else:
                _bounce(e1, e2)
        else:
            _land(e1, e2)
    elif e2.artificial:
        _land(e2, e1)
    else:
        _bounce(e1, e2)

    return y


def _docking(e1, e2, e2_index):
    # e1 is an artificial object
    # if 2 artificial object to be docked on (spacespation)

    norm = e1.pos - e2.pos
    collision_angle = np.arctan2(norm[1], norm[0])
    collision_angle = collision_angle % (2 * np.pi)

    ANGLE_MIN = (e2.heading + 0.7 * np.pi) % (2 * np.pi)
    ANGLE_MAX = (e2.heading + 1.3 * np.pi) % (2 * np.pi)

    if collision_angle < ANGLE_MIN or collision_angle > ANGLE_MAX:
        # add damage ?
        _bounce(e1, e2)
        return

    log.info(f'Docking {e1.name} on {e2.name}')
    e1.landed_on = e2.name

    # Currently this flag has almost no effect.
    e1.broken = bool(
        np.linalg.norm(calc.rotational_speed(e1, e2) - e1.v) >
        common.craft_capabilities[e1.name].hull_strength
    )

    # set right heading for future takeoff
    e2_opposite = e2.heading + np.pi
    e1.pos = e2.pos + (e1.r + e2.r) * calc.heading_vector(e2_opposite)
    e1.heading = (e2_opposite) % (2 * np.pi)
    e1.throttle = 0
    e1.spin = e2.spin
    e1.v = e2.v


def _bounce(e1, e2):
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


def _land(e1, e2):
    # e1 is an artificial object
    # if 2 artificial object collide (habitat, spacespation)
    # or small astroid collision (need deletion), handle later

    log.info(f'Landing {e1.name} on {e2.name}')
    assert e2.artificial is False
    e1.landed_on = e2.name

    # Currently does nothing
    e1.broken = bool(
        np.linalg.norm(calc.rotational_speed(e1, e2) - e1.v) >
        common.craft_capabilities[e1.name].hull_strength
    )

    # set right heading for future takeoff
    norm = e1.pos - e2.pos
    e1.heading = np.arctan2(norm[1], norm[0])
    e1.throttle = 0
    e1.spin = e2.spin
    e1.v = calc.rotational_speed(e1, e2)


def _one_request(request: Request, y0: state.PhysicsState) \
        -> state.PhysicsState:
    """Interface to set habitat controls.

    Use an argument to change habitat throttle or spinning, and simulation
    will restart with this new information."""
    log.info(f'At simtime={y0.timestamp}, '
             f'Got {MessageToString(request, as_one_line=True)}')

    if request.ident != Request.TIME_ACC_SET:
        # Reveal the type of y0.craft as str (not None).
        assert y0.craft is not None

    if request.ident == Request.HAB_SPIN_CHANGE:
        if y0.navmode != state.Navmode['Manual']:
            # We're in autopilot, ignore this command
            return y0
        craft = y0[y0.craft]
        if not craft.landed():
            craft.spin += request.spin_change
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
        common.craft_capabilities[common.HABITAT] = \
            common.craft_capabilities[common.HABITAT]._replace(
                thrust=100 * request.engineering_update.max_thrust)
        hab = y0[common.HABITAT]
        ayse = y0[common.AYSE]
        hab.fuel = request.engineering_update.hab_fuel
        ayse.fuel = request.engineering_update.ayse_fuel
        y0[common.HABITAT] = hab
        y0[common.AYSE] = ayse

        if request.engineering_update.module_state == \
            Request.DETACHED_MODULE and \
            common.MODULE not in y0._entity_names and \
                not hab.landed():
            # If the Habitat is freely floating and engineering asks us to
            # detach the Module, spawn in the Module.
            module = state.Entity(state.protos.Entity(
                name=common.MODULE, mass=100, r=10, artificial=True))
            module.pos = hab.pos - (module.r + hab.r) * \
                calc.heading_vector(hab.heading)
            module.v = calc.rotational_speed(module, hab)

            y0_proto = y0.as_proto()
            y0_proto.entities.extend([module.proto])
            y0 = state.PhysicsState(None, y0_proto)

    elif request.ident == Request.UNDOCK:
        habitat = y0[common.HABITAT]

        if habitat.landed_on == common.AYSE:
            ayse = y0[common.AYSE]
            habitat.landed_on = ''

            norm = habitat.pos - ayse.pos
            unit_norm = norm / np.linalg.norm(norm)
            habitat.v += unit_norm * common.UNDOCK_PUSH
            habitat.spin = ayse.spin

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
    elif request.ident == Request.PARACHUTE:
        y0.parachute_deployed = request.deploy_parachute
    elif request.ident == Request.IGNITE_SRBS:
        if round(y0.srb_time) == common.SRB_FULL:
            y0.srb_time = common.SRB_BURNTIME

    return y0

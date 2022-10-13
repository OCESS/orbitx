"""This is the core of the OrbitX physics engine. Here, we simulate the state
of the solar system over time. To do this, we start a thread running in the
background to run the simulation, while our main thread handles all other
user interaction.

I've tried to provide a clean interface to this module, so that you don't have
to mess with the internals too much. Unfortunately, the internals are a bit
tied together, and can break in unforeseen ways if changed without
understanding how all the bits fit together.

Get in contact with me if you want to add new functionality! I'm more than
happy to help :)"""

import collections
import functools
import logging
import threading
import time
import warnings
from typing import List, Optional, NamedTuple

import numpy as np
import scipy.integrate
import scipy.spatial
import scipy.special

from orbitx import common
from orbitx.common import Request
from orbitx.physics import helpers, ode_solver
from orbitx.orbitx_pb2 import PhysicalState
from orbitx.data_structures.space import PhysicsState

SOLUTION_CACHE_SIZE = 2

log = logging.getLogger('orbitx')

TIME_ACC_TO_BOUND = {time_acc.value: time_acc.accurate_bound
                     for time_acc in common.TIME_ACCS}


class NumpyLogger:
    """Pass this to numpy to log sketchy floating-point errors."""
    @staticmethod
    def write(message: str):
        log.warning(message)


def set_floating_point_fatality():
    """Decide what to do when this thread encounters a floating point error in scipy/numpy."""
    warnings.simplefilter('error')  # Raise exception on scipy/numpy RuntimeWarning
    scipy.special.seterr(all='raise')
    np.seterrcall(NumpyLogger())
    np.seterr(all='raise')

    # Over- and underflow is bad, but we shouldn't stop someone mid-mission for it.
    np.seterr(over='log', under='log')


class TimeAccChange(NamedTuple):
    """Describes when the time acc of the simulation changes, and what to."""
    time_acc: float
    start_simtime: float


class PhysicsEngine:
    """Physics Engine class. Encapsulates simulating physical state.

    Methods beginning with an underscore are not part of the API and change!

    Example usage:
    pe = PhysicsEngine(flight_savefile)
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
    # Increasing this constant results in the simulation being faster to
    # compute but less accurate of an approximation. If Phobos starts crashing
    # into Mars, tweak this downwards.
    MAX_STEP_SIZE = 100

    def __init__(self, physical_state: PhysicsState):
        # Controls access to self._solutions. If anything changes that is
        # related to self._solutions, this condition variable should be
        # notified. Currently, that's just if self._solutions or
        # self._last_simtime changes.
        self._solutions_cond = threading.Condition()
        self._solutions: collections.deque

        self._simthread: Optional[threading.Thread] = None
        self._simthread_exception: Optional[Exception] = None
        self._last_physical_state: PhysicalState
        self._last_monotime: float = time.monotonic()
        self._last_simtime: float
        self._time_acc_changes: collections.deque

        # This will change how we handle floating point errors on the *main*
        # thread only (i.e. the thread that Python code runs on by default).
        # When self._start_simthread starts a simthread, we have to call this
        # function in that new thread as well.
        set_floating_point_fatality()

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

            # TODO: This will likely cause the simulation to hang for a bit when
            # stepping down values of time acceleration; the _last_simtime will
            # probably have been set by a call to _simtime() with a high time acc,
            # and a subsequent call to _simtime with (e.g.) a 10x slower time acc
            # will not have any effect until the simulation time advances to the
            # most recently-requested time, which will now take 10x as much alpha
            # time.
            simtime = self._last_simtime

            assert self._time_acc_changes
            # This while loop will increment simtime and decrement
            # time_elapsed correspondingly until the second time acc change
            # starts farther in the future than we will increment simtime.
            while len(self._time_acc_changes) > 1 and \
                    self._time_acc_changes[1].start_simtime < (
                    simtime + self._time_acc_changes[0].time_acc
                    * alpha_time_elapsed):
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

    def _start_simthread(self, t0: float, y0: PhysicsState) -> None:
        if round(y0.time_acc) == 0:
            # We've paused the simulation. Don't start a new simthread
            log.info('Pausing simulation')
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
            y0 = PhysicsState(None, self._last_physical_state)
        else:
            y0 = self.get_state(requested_t)

        for request in requests:
            if request.ident == Request.NOOP:
                # We don't care about these requests
                continue
            y0 = helpers._one_request(request, y0)
            if request.ident == Request.TIME_ACC_SET:
                assert request.time_acc_set >= 0
                self._time_acc_changes.append(
                    TimeAccChange(time_acc=y0.time_acc,
                                  start_simtime=y0.timestamp)
                )

        self.set_state(y0)

    def set_state(self, physical_state: PhysicsState):
        self._stop_simthread()

        physical_state = helpers._reconcile_entity_dynamics(physical_state)
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

    def get_state(self, requested_t=None) -> PhysicsState:
        """Return the latest physical state of the simulation."""
        requested_t = self._simtime(requested_t)

        # Wait until there is a solution for our requested_t. The .wait_for()
        # call will block until a new ODE solution is created.
        with self._solutions_cond:
            self._last_simtime = requested_t
            self._solutions_cond.wait_for(
                # Wait until we're paused, there's a solution, or an exception.
                lambda: (
                    self._last_physical_state.time_acc == 0
                    or (len(self._solutions) != 0 and self._solutions[-1].t_max >= requested_t)
                    or self._simthread_exception is not None
                )
            )

            # Check if the simthread crashed, and do some logging.
            if self._simthread_exception is not None:
                if self._solutions:
                    log.debug('Last solution:')
                    log.debug(f'{self._solutions[-1].y_events[-1]}')
                log.debug('Last physical_state:')
                log.debug(f'{self._last_physical_state}')
                raise self._simthread_exception

            if self._last_physical_state.time_acc == 0:
                # We're paused, so there are no solutions being generated.
                # Exit this 'with' block and release our _solutions_cond lock.
                pass
            else:
                # We can't integrate backwards, so if integration has gone
                # beyond what we need, fail early.
                assert requested_t >= self._solutions[0].t_min, \
                    (self._solutions[0].t_min, self._solutions[-1].t_max)

                for soln in self._solutions:
                    if soln.t_min <= requested_t <= soln.t_max:
                        solution = soln

        if self._last_physical_state.time_acc == 0:
            # We're paused, so return the only state we have.
            return PhysicsState(None, self._last_physical_state)
        else:
            # We have a solution, return it.
            newest_state = PhysicsState(
                solution(requested_t), self._last_physical_state
            )
            newest_state.timestamp = requested_t
            return newest_state

    class RestartSimulationException(Exception):
        """A request to restart the simulation with new t and y."""

        def __init__(self, t: float, y: PhysicsState):
            self.t = t
            self.y = y

    def _simthread_target(self, t, y):
        set_floating_point_fatality()
        while True:
            try:
                self._run_simulation(t, y)
                if self._stopping_simthread:
                    return
            except PhysicsEngine.RestartSimulationException as e:
                t = e.t
                y = e.y
                log.info(f'Simulation restarted itself at {t}.')
            except Exception as e:
                log.error(f'simthread got exception {repr(e)}.')
                self._simthread_exception = e
                with self._solutions_cond:
                    self._solutions_cond.notify_all()
                return

    def _run_simulation(self, t: float, y: PhysicsState) -> None:
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
                ode_solver.simulation_differential_function,
                pass_through_state=proto_state,
                masses=self.M, artificials=self._artificials)

            events: List[ode_solver.Event] = [
                ode_solver.CollisionEvent(y, self.R),
                ode_solver.HabFuelEvent(y),
                ode_solver.LiftoffEvent(y),
                ode_solver.SrbFuelEvent(),
                ode_solver.HabReactorTempEvent(),
                ode_solver.AyseReactorTempEvent()
            ]
            if y.craft is not None:
                events.append(ode_solver.HighAccEvent(
                    derive_func,
                    self._artificials,
                    TIME_ACC_TO_BOUND[round(y.time_acc)],
                    y.time_acc,
                    len(y)))

            ivp_out = scipy.integrate.solve_ivp(
                fun=derive_func,
                t_span=[t, t + min(y.time_acc, 10 * self.MAX_STEP_SIZE)],
                # solve_ivp requires a 1D y0 array
                y0=y.y0(),
                events=events,
                dense_output=True,
                max_step=self.MAX_STEP_SIZE
            )

            if not ivp_out.success:
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
                    len(self._solutions) < SOLUTION_CACHE_SIZE
                    or self._last_simtime > self._solutions[0].t_max
                    or self._stopping_simthread
                )
                if self._stopping_simthread:
                    break

                # self._solutions contains ODE solutions for the interval
                # [self._solutions[0].t_min, self._solutions[-1].t_max].
                self._solutions.append(ivp_out.sol)
                self._solutions_cond.notify_all()

            y = PhysicsState(ivp_out.y[:, -1], proto_state)
            t = ivp_out.t[-1]

            if ivp_out.status > 0:
                log.info(f'Got event: {ivp_out.t_events} at t={t}.')
                for index, event_t in enumerate(ivp_out.t_events):
                    if len(event_t) == 0:
                        # If this event didn't occur, then event_t == []
                        continue
                    event = events[index]
                    if isinstance(event, ode_solver.CollisionEvent):
                        # Collision, simulation ended. Handled it and continue.
                        assert len(ivp_out.t_events[0]) == 1
                        assert len(ivp_out.t) >= 2
                        y = helpers._collision_decision(t, y, events[0])
                        y = helpers._reconcile_entity_dynamics(y)
                    if isinstance(event, ode_solver.HabFuelEvent):
                        # Something ran out of fuel.
                        for artificial_index in self._artificials:
                            artificial = y[artificial_index]
                            if round(artificial.fuel) != 0:
                                continue
                            log.info(f'{artificial.name} ran out of fuel.')
                            # This craft is out of fuel, the next iteration
                            # won't consume any fuel. Set throttle to zero.
                            artificial.throttle = 0
                            # Set fuel to a negative value, so it doesn't
                            # trigger the event function.
                            artificial.fuel = 0
                    if isinstance(event, ode_solver.LiftoffEvent):
                        # A craft has a TWR > 1
                        craft = y.craft_entity()
                        log.info(
                            'We have liftoff of the '
                            f'{craft.name} from {craft.landed_on} at {t}.')
                        craft.landed_on = ''
                    if isinstance(event, ode_solver.SrbFuelEvent):
                        # SRB fuel exhaustion.
                        log.info('SRB exhausted.')
                        y.srb_time = common.SRB_EMPTY
                    if isinstance(event, ode_solver.HighAccEvent):
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
                        raise PhysicsEngine.RestartSimulationException(t, y)
                    if isinstance(event, ode_solver.HabReactorTempEvent):
                        y.engineering.hab_reactor_alarm = \
                            not y.engineering.hab_reactor_alarm
                    if isinstance(event, ode_solver.AyseReactorTempEvent):
                        y.engineering.ayse_reactor_alarm = \
                            not y.engineering.ayse_reactor_alarm

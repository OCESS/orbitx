import collections
import logging
import threading
import time
import warnings

import numpy as np
import numpy.linalg as linalg
import scipy.spatial
import scipy.special
from scipy.integrate import *

from . import orbitx_pb2 as protos
from . import common

#from Entity import * # not really implemented


default_dtype = np.longdouble

# Higher values of this result in faster simulation but more chance of missing
# a collision. Units of this are in seconds.
STEP_SIZE_MULT = 1.0
SOLUTION_CACHE_SIZE = 100

warnings.simplefilter('error')  # Raise exception on numpy RuntimeWarning
scipy.special.seterr(all='raise')
log = logging.getLogger()

# Note on variable naming:
# a lowercase single letter, like `x`, is likely a scalar
# an uppercase single letter, like `X`, is likely a 1D row vector of scalars
# `y` is either the y position, or a vector of the form [X, Y, DX, DY]. i.e. 2D
# `y_1d` is the 1D row vector flattened version of the above `y` 2D vector,
#     which is required by `solve_ivp` inputs and outputs

# Note on the np.array family of functions
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
        # self._simtime_of_last_request changes.
        self._solutions_cond = threading.Condition()
        self._time_of_last_request = time.monotonic()
        self._time_acceleration = common.DEFAULT_TIME_ACC
        self._simthread_exception = None

        self.set_state(physical_state)

    def set_time_acceleration(self, time_acceleration, requested_t=None):
        """Change the speed at which this PEngine simulates at."""
        if time_acceleration <= 0:
            log.error(f'Time acceleration {time_acceleration} must be > 0')
            return

        if requested_t is None:
            requested_t = \
                self._simtime_of_last_request + self._simtime_elapsed()

        y = _y_from_state(self.get_state(requested_t))
        self._time_acceleration = time_acceleration

        # TODO: stability hack, ignore collisions over a certain time acc.
        if time_acceleration > 1000:
            self._events_function = lambda t, y: 1
        else:
            self._events_function = _smallest_altitude_event

        self._restart_simulation(requested_t, y)

    def _simtime_elapsed(self):
        time_elapsed = max(
            time.monotonic() - self._time_of_last_request,
            0.0001
        )

        with self._solutions_cond:
            self._time_of_last_request = time.monotonic()
            self._solutions_cond.notify_all()

        return time_elapsed * self._time_acceleration

    def _stop_simthread(self):
        if hasattr(self, '_simthread'):
            with self._solutions_cond:
                self._stopping_simthread = True
                self._solutions_cond.notify_all()
            self._simthread.join()

    def _restart_simulation(self, t, y):
        self._stop_simthread()

        self._simthread = threading.Thread(
            target=self._simthread_target,
            args=(t, y),
            daemon=True
        )
        self._stopping_simthread = False

        # We don't need to synchronize self._simtime_of_last_request or
        # self._solutions here, because we just stopped the background
        # simulation thread only a few lines ago.
        self._simtime_of_last_request = t

        # Essentially just a cache of ODE solutions.
        self._solutions = collections.deque(maxlen=SOLUTION_CACHE_SIZE)

        # Fork self._simthread into the background.
        self._simthread.start()

    def _physics_entity_at(self, y, i):
        """Returns a PhysicsEntity constructed from the i'th entity."""
        physics_entity = PhysicsEntity(
            self._template_physical_state.entities[i])
        physics_entity.pos = np.array([y[0][i], y[1][i]])
        physics_entity.v = np.array([y[2][i], y[3][i]])
        return physics_entity

    def _merge_physics_entity_into(self, physics_entity, y, i):
        """Inverse of _physics_entity_at, merges a physics_entity into y."""
        y[0][i], y[1][i] = physics_entity.pos
        y[2][i], y[3][i] = physics_entity.v
        return y

    def set_state(self, physical_state):
        #Temporary solution to find Habitat
        self.HabIndex=-1
        index=-1
        for entity in physical_state.entities:
            index+=1
            if entity.name=="Habitat":
                self.HabIndex=index
                #self.Habitat=Habitat(physical_state.entities[index]) #keep this potentially needed later
        #Temporary solution end
        X, Y, DX, DY = _y_from_state(physical_state)
        self.S = np.array([entity.spin for entity in physical_state.entities]
                          ).astype(default_dtype)
        self.R = np.array([entity.r for entity in physical_state.entities]
                          ).astype(default_dtype)
        self.M = np.array([entity.mass for entity in physical_state.entities]
                          ).astype(default_dtype)
        self.Fuel = \
            np.array([entity.fuel for entity in physical_state.entities]
                     ).astype(default_dtype)
        _smallest_altitude_event.radii = self.R.reshape(1, -1)  # Column vector

        # Don't store positions and velocities in the physical_state,
        # it should only be returned from get_state()
        self._template_physical_state.CopyFrom(physical_state)
        for entity in self._template_physical_state.entities:
            entity.ClearField('x')
            entity.ClearField('y')
            entity.ClearField('vx')
            entity.ClearField('vy')

        if len(self._template_physical_state.entities) > 1:
            self._events_function = _smallest_altitude_event
        else:
            # If there's only one entity, make a no-op events function
            self._events_function = lambda t, y: 1

        self._restart_simulation(physical_state.timestamp, (X, Y, DX, DY))

    def _resolve_collision(self, e1, e2):
        # Resolve a collision by:
        # 1. calculating positions and velocities of the two entities
        # 2. do a 1D collision calculation along the normal between the two
        # 3. recombine the velocity vectors

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
        new_v1n = (v1n * (e1.m - e2.m) + 2 * e2.m * v2n) / (e1.m + e2.m)
        new_v2n = (v2n * (e2.m - e1.m) + 2 * e1.m * v1n) / (e1.m + e2.m)

        # Calculate new velocities
        e1.v = new_v1n * unit_norm + v1t * unit_tang
        e2.v = new_v2n * unit_norm + v2t * unit_tang

        return e1, e2

    def _collision_handle(self, t, y):
        y = _extract_from_y_1d(y)
        e1_index, e2_index = _smallest_altitude_event(t, y, return_pair=True)
        e1 = self._physics_entity_at(y, e1_index)
        e2 = self._physics_entity_at(y, e2_index)
        e1, e2 = self._resolve_collision(e1, e2)
        log.info(f'Collision between {e1.name} and {e2.name} at t={t}')
        y = self._merge_physics_entity_into(e1, y, e1_index)
        y = self._merge_physics_entity_into(e2, y, e2_index)
        return y

    def _derive(self, t, y_1d):
        X, Y, DX, DY = _extract_from_y_1d(y_1d)
        Xa, Ya = _get_acc(X, Y, self.M + self.Fuel)
        # We got a 1d row vector, make sure to return a 1d row vector.
        return np.concatenate((DX, DY, Xa, Ya), axis=None)

    def _state_from_y(self, t, y):
        y = _extract_from_y_1d(y)
        state = protos.PhysicalState()
        state.MergeFrom(self._template_physical_state)
        state.timestamp = t
        for x, y, vx, vy, entity in zip(
                y[0], y[1], y[2], y[3], state.entities):
            entity.x = x
            entity.y = y
            entity.vx = vx
            entity.vy = vy
        return state

    def get_state(self, requested_t=None):
        """Return the latest physical state of the simulation."""
        if requested_t is None:
            requested_t = \
                self._simtime_of_last_request + self._simtime_elapsed()

        # Wait until there is a solution for our requested_t. The .wait_for()
        # call will block until a new ODE solution is created.
        with self._solutions_cond:
            self._simtime_of_last_request = requested_t

            self._solutions_cond.wait_for(
                lambda: len(self._solutions) != 0 and
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

        return self._state_from_y(requested_t, solution(requested_t))

    def _simthread_target(self, t, y):
        log.debug('simthread started')
        try:
            self._generate_new_ode_solutions(t, y)
        except Exception as e:
            log.debug('simthread got exception, forwarding to main thread')
            self._simthread_exception = e
        log.debug('simthread exited')

    def _generate_new_ode_solutions(self, t, y):
        # An overview of how time is managed:
        # self._simtime_of_last_request is the main thread's latest idea of
        # what the current time is in the simulation. Every call to
        # get_state(), self._timetime_of_last_request is incremented by the
        # amount of time that passed since the last call to get_state(),
        # factoring in self._time_acceleration.
        # self._solutions is a fixed-size queue of ODE solutions.
        # Each element has an attribute, t_max, which describes the largest
        # time that the solution can be evaluated at and still be accurate.
        # The highest such t_max should always be larger than the current
        # simulation time, i.e. self._simtime_of_last_request.

        # solve_ivp requires a 1D y0 array
        y = np.concatenate(y, axis=None)

        while not self._stopping_simthread:
            # self._solutions contains ODE solutions for the interval
            # [self._solutions[0].t_min, self._solutions[-1].t_max]
            # If we're in this function, requested_t is not in this interval!
            # Then we should integrate the interval of
            # [self._solutions[-1].t_max, requested_t]
            # and hopefully a bit farther past the end of that interval.
            ivp_out = scipy.integrate.solve_ivp(
                self._derive,
                [t, t + self._time_acceleration],
                y,
                #method='LSODA',
                events=self._events_function,
                max_step=STEP_SIZE_MULT * self._time_acceleration,
                #min_step=1e-10,
                #rtol=max(np.log(self._time_acceleration) / 100, 1e-3),
                #atol=max(np.log(self._time_acceleration) / 100, 1e-6),
                dense_output=True
            )

            if ivp_out.status < 0:
                # Integration error
                log.error(ivp_out.message)
                log.error(('Retrying with decreased time acceleration = '
                           f'{self._time_acceleration / 10}'))
                self._time_acceleration /= 10
                if self._time_acceleration < 1:
                    # We can't lower the time acceleration anymore
                    breakpoint()
                    raise Exception(ivp_out.message)
                continue

            # When we create a new solution, let other people know.
            with self._solutions_cond:
                # If adding another solution to our max-sized deque would drop
                # our oldest solution, and the main thread is still asking for
                # state in the t interval of our oldest solution, take a break
                # until the main thread has caught up.
                self._solutions_cond.wait_for(
                    lambda: len(self._solutions) < SOLUTION_CACHE_SIZE or
                    self._simtime_of_last_request > self._solutions[0].t_max or
                    self._stopping_simthread
                )
                if self._stopping_simthread:
                    break

                self._solutions.append(ivp_out.sol)
                self._solutions_cond.notify_all()

            y = ivp_out.y[:, -1]
            t = ivp_out.t[-1]

            if ivp_out.status > 0:
                # We got a collision, simulation ends with the first collision.
                assert len(ivp_out.t_events[0]) == 1
                assert len(ivp_out.t) >= 2
                # The last column of the solution is the state at the collision
                y = np.concatenate(self._collision_handle(t, y), axis=None)


# These _functions are internal helper functions.
def _y_from_state(physical_state):
    X = np.array([entity.x for entity in physical_state.entities]
                 ).astype(default_dtype)
    Y = np.array([entity.y for entity in physical_state.entities]
                 ).astype(default_dtype)
    DX = np.array([entity.vx for entity in physical_state.entities]
                  ).astype(default_dtype)
    DY = np.array([entity.vy for entity in physical_state.entities]
                  ).astype(default_dtype)
    return (X, Y, DX, DY)


def _force(MM, X, Y):
    G = 6.674e-11
    D2 = np.square(X - X.transpose()) + np.square(Y - Y.transpose())
    # Calculate G * m1*m2/d^2 for each object pair.
    # In the diagonal case, i.e. an object paired with itself, force = 0.
    force_matrix = np.divide(MM, np.where(D2 != 0, D2, 1))
    np.fill_diagonal(force_matrix, 0)
    return G * force_matrix


def _force_sum(_force):
    return np.sum(_force, 0)


def _angle_matrix(X, Y):
    Xd = X - X.transpose()
    Yd = Y - Y.transpose()
    return np.arctan2(Yd, Xd)


def _polar_to_cartesian(ang, hyp):
    X = np.multiply(np.cos(ang), hyp)
    Y = np.multiply(np.sin(ang), hyp)
    return X.T, Y.T


def _f_to_a(f, M):
    return np.divide(f, M)


def _get_acc(X, Y, M):
    # Turn X, Y, M into column vectors, which is easier to do math with.
    # (row vectors won't transpose)
    X = X.reshape(1, -1)
    Y = Y.reshape(1, -1)
    M = M.reshape(1, -1)
    MM = np.outer(M, M)  # A square matrix of masses, units of kg^2
    ang = _angle_matrix(X, Y)
    FORCE = _force(MM, X, Y)
    Xf, Yf = _polar_to_cartesian(ang, FORCE)
    Xf = _force_sum(Xf)
    Yf = _force_sum(Yf)
    Xa = _f_to_a(Xf, M)
    Ya = _f_to_a(Yf, M)
    return np.array(Xa).reshape(-1), np.array(Ya).reshape(-1)


def _extract_from_y_1d(y_1d):
    # Split into 4 equal parts, [X, Y, DX, DY]
    if isinstance(y_1d, np.ndarray) and len(y_1d.shape) == 1:
        # If y is a 1D ODE input
        return np.hsplit(y_1d, 4)
    else:
        # If y is already 4 columns
        return y_1d


def _smallest_altitude_event(_, y_1d, return_pair=False):
    """This function is passed in to solve_ivp to detect a collision.

    To accomplish this, and also to stop solve_ivp when there is a collision,
    this function has the attributes `terminal = True` and `radii = [...]`.
    radii will be set by a PEngine when it's instantiated.
    Unfortunately this can't be a PEngine method, since attributes of a method
    can't be set.
    Ctrl-F 'events' in
    docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
    for more info.
    This should return a scalar, and specifically 0 to indicate a collision
    """
    X, Y, DX, DY = _extract_from_y_1d(y_1d)
    n = len(X)
    posns = np.column_stack((X, Y))  # An n*2 vector of (x, y) positions
    # An n*n matrix of _altitudes_ between each entity
    alt_matrix = scipy.spatial.distance.cdist(posns, posns) - \
        (_smallest_altitude_event.radii + _smallest_altitude_event.radii.T)
    # To simplify calculations, an entity's altitude from itself is inf
    np.fill_diagonal(alt_matrix, np.inf)

    if return_pair:
        # If we want to find out which entities collided, set return_pair=True.
        flattened_index = alt_matrix.argmin()
        # flattened_index is a value in the interval [1, n*n]-1. Turn it into a
        # 2D index.
        object_i = flattened_index // n
        object_j = flattened_index % n
        return object_i, object_j
    else:
        # This is how solve_ivp will invoke this function. Return a scalar.
        return np.min(alt_matrix)


_smallest_altitude_event.terminal = True  # Event stops integration
_smallest_altitude_event.direction = -1  # Event matters when going pos -> neg
_smallest_altitude_event.radii = np.array([])

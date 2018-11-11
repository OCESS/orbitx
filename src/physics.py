import collections
import itertools
import logging
import time

import google.protobuf.json_format
import numpy as np
import numpy.linalg as linalg
import scipy.special
from scipy.integrate import *

import orbitx_pb2 as protos
import common

# Higher values of this result in faster simulation but more chance of missing
# a collision. Units of this are in seconds.
MAX_STEP_SIZE = 1.0
FUTURE_WORK_SIZE = 10.0
scipy.special.seterr(all='raise')
log = logging.getLogger()

# Note on variable naming:
# a lowercase single letter, like `x`, is likely a scalar
# an uppercase single letter, like `X`, is likely a 1D row vector of scalars
# `y` is either the y position, or a vector of the form [X, Y, DX, DY]. i.e. 2D
# `y_1d` is the 1D row vector flattened version of the above `y` 2D vector,
#     which is required by `solve_ivp` inputs and outputs


def force(MM, X, Y):
    G = 6.674e-11
    D2 = np.square(X - X.transpose()) + np.square(Y - Y.transpose())
    # This matrix will tell np.divide to not divide along the diagonal, i.e.
    # don't calculate the force between an entity and itself.
    where_matrix = np.full(D2.shape, True)
    np.fill_diagonal(where_matrix, False)
    force_matrix = np.divide(MM, D2, where=where_matrix)
    return G * force_matrix


def force_sum(force):
    return np.sum(force, 0)


def angle_matrix(X, Y):
    Xd = X - X.transpose()
    Yd = Y - Y.transpose()
    return np.arctan2(Yd, Xd)


def polar_to_cartesian(ang, hyp):
    X = np.multiply(np.cos(ang), hyp)
    Y = np.multiply(np.sin(ang), hyp)
    return X.T, Y.T


def f_to_a(f, M):
    return np.divide(f, M)


def get_acc(X, Y, M):
    # Turn X, Y, M into column vectors, which is easier to do math with.
    # (row vectors won't transpose)
    X = np.array([X])
    Y = np.array([Y])
    M = np.array([M])
    MM = np.outer(M, M)  # A square matrix of masses, units of kg^2
    ang = angle_matrix(X, Y)
    FORCE = force(MM, X, Y)
    Xf, Yf = polar_to_cartesian(ang, FORCE)
    Xf = force_sum(Xf)
    Yf = force_sum(Yf)
    Xa = f_to_a(Xf, M)
    Ya = f_to_a(Yf, M)
    return np.array(Xa)[0], np.array(Ya)[0]


def extract_from_y_1d(y_1d):
    n = len(y_1d) // 4
    X = (y_1d[0:n])
    Y = (y_1d[n:2 * n])
    DX = (y_1d[2 * n:3 * n])
    DY = (y_1d[3 * n:4 * n])
    return X, Y, DX, DY


def event_altitude(x1, y1, vx1, vy1, r1, x2, y2, vx2, vy2, r2):
    # Return a negative value if two entities are moving closer,
    # Return zero if two entities are touching,
    # Return a positive value if two entities are moving farther.
    pos = [x1 - x2, y1 - y2]
    v = [vx1 - vx2, vy1 - vy2]
    altitude = linalg.norm(pos) - r1 - r2  # Should always be positive
    relative_speed = linalg.norm(v)  # Negative when moving closer
    if relative_speed == 0:
        return altitude
    else:
        return altitude * np.sign(relative_speed)


def smallest_altitude_pair(X, Y, DX, DY, R):
    assert len(X) > 1
    object_pairs = itertools.combinations(zip(X, Y, DX, DY, R), 2)
    return min(object_pairs,
               key=lambda pair: abs(event_altitude(*pair[0], *pair[1])))


def smallest_altitude_event(t, y_1d):
    """This function is passed in to solve_ivp to detect a collision.

    To accomplish this, and also to stop solve_ivp when there is a collision,
    this function has the attributes `terminal = True` and `radii = [...]`.
    radii will be set by a PEngine when it's instantiated.
    The only time the return value of this function matters is when it reaches
    zero. Ctrl-F 'events' in
    docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
    for more info.
    """
    X, Y, DX, DY = extract_from_y_1d(y_1d)
    pair = smallest_altitude_pair(X, Y, DX, DY, smallest_altitude_event.radii)
    return event_altitude(*pair[0], *pair[1])


# smallest_altitude_event.terminal = True  # Event stops integration TODO: demo
smallest_altitude_event.direction = -1  # Event matters when going pos -> neg
smallest_altitude_event.radii = []


class PhysicsEntity(object):
    def __init__(self, entity):
        assert isinstance(entity, protos.Entity)
        self.name = entity.name
        self.pos = np.asarray([entity.x, entity.y])
        self.R = entity.r
        self.v = np.asarray([entity.vx, entity.vy])
        self.m = entity.mass
        self.spin = entity.spin
        self.heading = entity.heading

    def as_proto(self):
        return protos.Entity(
            name=self.name,
            x=self.pos[0],
            y=self.pos[1],
            vx=self.v[0],
            vy=self.v[1],
            r=self.R,
            mass=self.m,
            spin=self.spin,
            heading=self.heading
        )


class PEngine(object):
    """Physics Engine class. Encapsulates simulating physical state.

    Methods beginning with an underscore are not part of the API and change!

    Example usage:
    pe = PEngine(flight_savefile)
    state = pe.get_state()
    pe.set_time_acceleration(20)
    # Simulates 20 * [amount of time elapsed since last get_state() call]:
    state = pe.get_state()
    """

    def __init__(self, flight_savefile=None, mirror_state=None):
        # A PhysicalState, but no x, y, vx, or vy. That's handled by get_state.
        self._template_physical_state = protos.PhysicalState()
        # TODO: get rid of this check by only taking in a PhysicalState as arg.
        if flight_savefile:
            self.Load_json(flight_savefile)
        elif mirror_state:
            self.set_state(mirror_state())
        else:
            raise ValueError('need either a file or a lead server')
        self._reset_solutions()
        self._time_acceleration = 1.0
        self._last_state_request_time = time.monotonic()
        if len(self._template_physical_state.entities) > 1:
            self._events_function = smallest_altitude_event
        else:
            # If there's only one entity, make a no-op events function
            self._events_function = lambda t, y: 1

    def set_time_acceleration(self, time_acceleration):
        """Change the speed at which this PEngine simulates at."""
        if time_acceleration <= 0:
            log.error(f'Time acceleration {time_acceleration} must be > 0')
            return
        self._time_acceleration = time_acceleration
        self._reset_solutions()

    def _time_elapsed(self):
        time_elapsed = time.monotonic() - self._last_state_request_time
        self._last_state_request_time = time.monotonic()
        return max(time_elapsed, 0.001)

    def _reset_solutions(self):
        # self._solutions is effectively a cache of ODE solutions, which
        # can be evaluated continuously for any value of t.
        # If something happens to invalidate this cache, clear the cache.
        self._solutions = collections.deque(maxlen=10)

    def _physics_entity_at(self, y, i):
        """Returns a PhysicsEntity constructed from the i'th entity."""
        physics_entity = PhysicsEntity(
            self._template_physical_state.entities[i])
        physics_entity.pos = np.asarray([y[0][i], y[1][i]])
        physics_entity.v = np.asarray([y[2][i], y[3][i]])
        return physics_entity

    def _merge_physics_entity_into(self, physics_entity, y, i):
        """Inverse of _physics_entity_at, merges a physics_entity into y."""
        y[0][i], y[1][i] = physics_entity.pos
        y[2][i], y[3][i] = physics_entity.v
        return y

    def Load_json(self, file):
        with open(file) as f:
            data = f.read()
        read_state = protos.PhysicalState()
        google.protobuf.json_format.Parse(data, read_state)
        self.set_state(read_state)

    def Save_json(self, file=common.AUTOSAVE_SAVEFILE):
        with open(file, 'w') as outfile:
            outfile.write(google.protobuf.json_format.MessageToJson(
                self._state_from_ode_solution(
                    self._template_physical_state.timestamp,
                    [self.X, self.Y, self.DX, self.DY])))

    def set_state(self, physical_state):
        self.X = np.asarray([entity.x for entity in physical_state.entities])
        self.Y = np.asarray([entity.y for entity in physical_state.entities])
        self.DX = np.asarray([entity.vx for entity in physical_state.entities])
        self.DY = np.asarray([entity.vy for entity in physical_state.entities])
        self.R = np.asarray([entity.r for entity in physical_state.entities])
        self.M = np.asarray(
            [entity.mass for entity in physical_state.entities])
        smallest_altitude_event.radii = self.R

        # Don't store positions and velocities in the physical_state,
        # it should only be returned from get_state()
        self._template_physical_state.CopyFrom(physical_state)
        for entity in self._template_physical_state.entities:
            entity.ClearField('x')
            entity.ClearField('y')
            entity.ClearField('vx')
            entity.ClearField('vy')

        self._reset_solutions()

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

    def _collision_handle(self, y):
        pair = smallest_altitude_pair(*y, self.R)
        # Find the indices of both objects, which are in the form (x, y, r)
        X = y[0]
        e1_index_list = np.where(X == pair[0][0])[0]
        e2_index_list = np.where(X == pair[1][0])[0]
        assert len(e1_index_list) == 1
        assert len(e2_index_list) == 1
        e1 = self._physics_entity_at(y, e1_index_list[0])
        e2 = self._physics_entity_at(y, e2_index_list[0])
        e1, e2 = self._resolve_collision(e1, e2)
        log.info(f'Collision between {e1.name} and {e2.name}')
        y = self._merge_physics_entity_into(e1, y, e1_index_list[0])
        y = self._merge_physics_entity_into(e2, y, e2_index_list[0])
        return y

    def _derive(self, t, y_1d):
        X, Y, DX, DY = extract_from_y_1d(y_1d)
        Xa, Ya = get_acc(X, Y, self.M)
        DX = DX + Xa
        DY = DY + Ya
        # We got a 1d row vector, make sure to return a 1d row vector.
        return np.concatenate([DX, DY, Xa, Ya], axis=None)

    def _state_from_ode_solution(self, t, y):
        y = extract_from_y_1d(y)
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
            # Always update the current timestamp of our physical state.
            time_elapsed = self._time_elapsed()
            requested_t = self._template_physical_state.timestamp + \
                time_elapsed * self._time_acceleration

        while len(self._solutions) == 0 or \
                self._solutions[-1].t_max < requested_t:
            self._generate_new_ode_solutions()  # TODO: need to pass in t?

        for soln in self._solutions:
            if soln.t_min <= requested_t and requested_t <= soln.t_max:
                return self._state_from_ode_solution(
                    requested_t, soln(requested_t))
        log.error((
            'AAAAAAAAAAAAAAAAAH got an oopsy-woopsy! Tell your code monkey!'
            f'{self._solutions[0].t_min}, {self._solutions[-1].t_max}, '
            f'{requested_t}'
        ))
        self._reset_solutions()
        return self.get_state(requested_t)

    def _generate_new_ode_solutions(self):
        # An overview of how time is managed:
        # self._template_physical_state.timestamp is the current time in the
        # simulation. Every call to get_state(), it is incremented by the
        # amount of time that passed since the last call to get_state(),
        # factoring in time_acceleration.
        # self._solutions is a fixed-size queue of ODE solutions.
        # Each element has an attribute, t_max, which describes the largest
        # time that the solution can be evaluated at and still be accurate.
        # The highest such t_max should always be larger than the current
        # simulation time, i.e. self._template_physical_state.timestamp.
        latest_y = (self.X, self.Y, self.DX, self.DY)
        latest_t = self._solutions[-1].t_max if \
            len(self._solutions) else \
            self._template_physical_state.timestamp

        while True:
            ivp_out = scipy.integrate.solve_ivp(
                self._derive,
                [latest_t,
                 latest_t + FUTURE_WORK_SIZE * self._time_acceleration],
                # solve_ivp requires a 1D y0 array
                np.concatenate(latest_y, axis=None),
                events=self._events_function,
                max_step=MAX_STEP_SIZE * self._time_acceleration,
                dense_output=True
            )

            self._solutions.append(ivp_out.sol)
            latest_y = extract_from_y_1d(ivp_out.y[:, -1])
            latest_t = ivp_out.t[-1]

            assert ivp_out.status >= 0
            if ivp_out.status == 0:
                # Finished integration successfully, done integrating
                break
            else:
                # We got a collision, simulation ends with the first collision.
                assert len(ivp_out.t_events[0]) == 1
                # The last column of the solution is the state at the collision
                latest_y = self._collision_handle(latest_y)
                # Redo the solve_ivp step
                continue

        self.X, self.Y, self.DX, self.DY = latest_y
        self._template_physical_state.timestamp = latest_t

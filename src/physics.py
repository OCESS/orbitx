import random
import string
import time

import google.protobuf.json_format
import numpy as np
import scipy.special
from scipy.integrate import *

import cs493_pb2 as protos
import common

scipy.special.seterr(all='raise')
# In[2]:


def distance(X, Y):
    return np.sqrt((X - X.transpose())**2 + (Y - Y.transpose())**2)


def force(MM, X, Y):
    G = 6.674e-11
    n = X.shape[1]
    D = (X - X.transpose())**2 + (Y - Y.transpose())**2
    return np.multiply(G * (MM / (D + 0.00001)),
                       np.where(np.identity(n), 0, 1))


def force_sum(force):
    return np.sum(force, 1)


def vec_to_angle(X, Y):
    Xd = X - X.transpose()
    Yd = Y - Y.transpose()
    return np.arctan2(Yd, Xd + 0.00001)


def angle_to_vec_stuff(ang, hyp):
    X = np.multiply(np.cos(ang), hyp)
    Y = np.multiply(np.sin(ang), hyp)
    return X, Y


def f_to_a(f, M):
    return np.divide(f, M)


def get_acc(X, Y, M):
    MM = M * np.transpose(M)
    ang = vec_to_angle(X, Y)
    FORCE = force(MM, X, Y)
    Xf, Yf = angle_to_vec_stuff(ang, FORCE)
    Xf = force_sum(Xf)
    Yf = force_sum(Yf)
    Xa = f_to_a(Xf, M)
    Ya = f_to_a(Yf, M)
    return Xa, Ya


def new_v(h, DX, DY, DX2, DY2):
    DX = DX + h * DX2
    DY = DY + h * DY2


def extract(y, n):
    X = (y[0:n]).reshape(1, n)
    Y = (y[n:2 * n]).reshape(1, n)
    DX = (y[2 * n:3 * n]).reshape(1, n)
    DY = (y[3 * n:4 * n]).reshape(1, n)
    # M=(y[4*n:5*n]).reshape(1,n)
    return X, Y, DX, DY


def derive(t, y, n, r, M):
    X, Y, DX, DY = extract(y, n)
    Xa, Ya = get_acc(X, Y, M)
    DX = DX + Xa
    DY = DY + Ya
    X = X + DX
    Y = Y + DY
    ans = [DX, DY, Xa, Ya]
    ans = np.concatenate(ans).ravel()
    return ans


# In[3]:


class Entity(object):
    def __init__(self, name, coor, r, M, v=[0, 0], spin=0, movable=True):
        self.name = name
        self.coordinates = coor
        self.r = r
        self.M = M
        self.V = v
        self.spin = spin
        self.movable = movable

    def json_save(self):
        return {
            "name": self.name,
            "velocity": self.V,
            "mass": self.M,
            "radius": self.r,
            "coordinates": self.coordinates,
            "angular speed": self.spin}


# In[4]:


class PEngine(object):
    class Bad_Merge(Exception):  # exception for merging same object
        def __init__(self, code=0):
            self.code = code

    def __init__(self, flight_savefile=None, mirror_state=None):
        # If this needs to be called again, call self.__init__ during runtime
        self.state = protos.PhysicalState(timestamp=0.0)
        if flight_savefile:
            self.Load_json(flight_savefile)
        elif mirror_state:
            self.state = mirror_state()
        self._integrator = None
        self._init = False
        self._last_step = time.monotonic()

    def _random_name(self):
        name = ''.join(
            random.choice(
                string.ascii_uppercase +
                string.digits) for _ in range(10))
        return name

    def random_entity(self, name=None):
        name = self._random_name(self)
        X = random.uniform(1e25, 1e30)
        Y = random.uniform(1e25, 1e30)
        r = random.uniform(1e5, 1e6)
        M = random.uniform(1e24, 1e26)
        self.add_entity(
            name=name, x=X, y=Y, vx=0, vy=0, r=r, mass=M, spin=0, heading=0)

    def add_entity(self, **kwargs):
        # How to use this magical function:
        # self.add_entity(name='Earth', x=5, y=10, etc etc etc)
        # Just pass all the variables that exist in an Entity message protobuf
        # (see cs493.proto) and it'll all happen automatically!
        self.state.entities.add(**kwargs)

    def Load_json(self, file):
        with open(file) as f:
            data = f.read()
        return google.protobuf.json_format.Parse(
            data, self.state)

    def Save_json(self, file=common.AUTOSAVE_SAVEFILE):
        with open(file, 'w') as outfile:
            outfile.write(google.protobuf.json_format.MessageToJson(
                self.state))

    def set_state(self, physical_state):
        self.state = physical_state
        self._gather_data()

    def _gather_data(self):
        self.X = np.asarray(
            [entity.x
                for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.Y = np.asarray(
            [entity.y
                for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.DX = np.asarray(
            [entity.vx
             for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.DY = np.asarray(
            [entity.vy
             for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.r = np.asarray(
            [entity.r
             for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.M = np.asarray(
            [entity.mass
             for entity in self.state.entities]
        ).reshape(1, len(self.state.entities))
        self.X = self.X.astype(object, copy=False)
        self.Y = self.Y.astype(object, copy=False)
        self.DX = self.DX.astype(object, copy=False)
        self.DY = self.DY.astype(object, copy=False)
        self.r = self.r.astype(object, copy=False)
        self.M = self.M.astype(object, copy=False)

    def _initialize(self):
        self._gather_data()
        # add code here for init
        self._init = True

    def update(self, y):
        for X, Y, DX, DY, entity in zip(
                y[0][0], y[1][0], y[2][0], y[3][0],
                self.state.entities):
            entity.x = X
            entity.y = Y
            entity.vx = DX
            entity.vy = DY

    def _merge(self, e1, e2):
        if e1 == e2:
            raise self.Bad_Merge()
        e1 = self.state.entities[e1]
        e2 = self.state.entities[e2]
        print(e1, e2)

        # Resolve a collision by:
        # 1. calculating positions and velocities of the two entities
        # 2. do a 1D collision calculation along the normal between the two
        # 3. recombine the velocity vectors
        e1_pos = np.asarray([e1.x, e1.y])
        e1_v = np.asarray([e1.vx, e1.vy])
        e2_pos = np.asarray([e2.x, e2.y])
        e2_v = np.asarray([e2.vx, e2.vy])

        norm = e1_pos - e2_pos
        unit_norm = norm / np.linalg.norm(norm)
        # The unit tangent is perpendicular to the unit normal vector
        unit_tang = unit_norm
        unit_tang[0], unit_tang[1] = -unit_tang[1], unit_tang[0]

        # Calculate both normal and tangent velocities for both entities
        v1n = scipy.dot(unit_norm, e1_v)
        v1t = scipy.dot(unit_tang, e1_v)
        v2n = scipy.dot(unit_norm, e2_v)
        v2t = scipy.dot(unit_tang, e2_v)

        # Use https://en.wikipedia.org/wiki/Elastic_collision
        # to find the new normal velocities (a 1D collision)
        new_v1n = (v1n * (e1.mass - e2.mass) + 2 *
                   e2.mass * v2n) / (e1.mass + e2.mass)
        new_v2n = (v2n * (e2.mass - e1.mass) + 2 *
                   e1.mass * v1n) / (e1.mass + e2.mass)

        # Calculate new velocities
        v1 = new_v1n * unit_norm + v1t * unit_tang
        v2 = new_v2n * unit_norm + v2t * unit_tang

        e1.vx = v1[0]
        e1.vy = v1[1]
        e2.vx = v2[0]
        e2.vy = v2[1]

    def _collision_handle(self, coll):
        for i, j in zip(coll[0], coll[1]):
            try:
                self._merge(i, j)
            except self.Bad_Merge:
                continue
            # except:
            #    print("Merge fail")
        self._gather_data()

    def _collision_detect(self, out):
        X = out[0]
        Y = out[1]
        D = distance(X, Y)
        R = self.r + self.r.transpose()
        # coll=np.where(((D-R)<0))
        coll = np.where(((D - R) < 0) - np.identity(D.shape[0]))
        if coll[0].shape[0] == 0:
            return False
        self._collision_handle(coll)
        return True

    def run_step(self, time_acceleration):
        # A note about time,
        # cribbed from https://docs.python.org/3/library/time.html
        # time.time() is the float number of seconds since epoch
        # however! it's not accurate enough for our needs (a precision
        # less than 1 second). Also, if someone sets the machine's time
        # back, time.time() will return non-monotonic values.
        # So our solution is:
        # in self.state.timestamp, store time.time(). Things like the GUI
        # will then format this timestamp as something like "October 2018" etc.
        # But if we want to find out how much time has passed between calls to
        # run_step, use time.monotonic()! This will be what self._integrator.t
        # is set to. Thus, self._integrator.t != self.state.timestamp!

        if not self._init:
            self._initialize()
        if self._integrator is None:
            t0 = 0.0
            y0 = [self.X, self.Y, self.DX, self.DY]
            y0 = np.concatenate(y0).ravel()
            self._integrator = ode(derive).set_integrator(
                'dopri5',
                rtol=0.01,
                nsteps=750*time_acceleration
            )
            self._integrator.set_initial_value(y0, t0).set_f_params(
                len(self.state.entities), self.r, self.M)

        # Simulate only the amount of time that has passed since the last call
        # to this function.
        time_step = time.monotonic() - self._last_step
        if time_step <= 0.0:
            print('time_step too small:', time_step)
            time_step = 1
        self._last_step = time.monotonic()
        out = self._integrator.integrate(
            self._integrator.t + time_acceleration * time_step
        )
        out = extract(out, len(self.state.entities))
        self.state.timestamp = time.time()
        self.out = out
        self.update(out)
        self._collision_detect(out)


# In[ ]:

# example code:
# PE=PEngine()
# PE.Load_json("data.json")
# PE.run_step(1)
# for i in range(0,90000000):
#    PE.run_step(1) #run step with h=1
# PE.Entities[C] #to get object with name C

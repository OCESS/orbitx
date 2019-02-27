import numpy as np
import scipy.integrate
import scipy.spatial
import scipy.special

from . import common

NO_INDEX = -1

def name_to_index(name, entities):
    names = [entity.name for entity in entities]
    return names.index(name) if name else NO_INDEX


def index_to_name(i, entities):
    i = int(i)
    return entities[i].name if i != NO_INDEX else ""



def grav_acc(X, Y, M):
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

# These _functions are internal helper functions.
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






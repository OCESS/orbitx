#!/usr/bin/env python3
import logging
import unittest

from . import common
from . import physics

log = logging.getLogger()

G = 6.67408e-11


class PhysicsEngineTestCase(unittest.TestCase):
    def test_simple_collision(self):
        physics_engine = physics.PEngine(
            flight_savefile=common.savefile('tests/simple-collision.json'))
        # In this case, the first entity is standing still and the second is
        # on a collision course going left to right. The two should bounce.
        approach = physics_engine.get_state(40)
        bounced = physics_engine.get_state(60)
        self.assertTrue(approach.entities[0].x > approach.entities[1].x)
        self.assertTrue(approach.entities[1].vx > 0)
        self.assertTrue(bounced.entities[0].x > bounced.entities[1].x)
        self.assertTrue(bounced.entities[1].vx < 0)

    def test_basic_movement(self):
        physics_engine = physics.PEngine(
            flight_savefile=common.savefile('tests/only-sun.json'))
        # In this case, the only entity is the Sun. It starts at (0, 0) with a
        # speed of (1, -1). It should move.
        initial = physics_engine.get_state(0)
        moved = physics_engine.get_state(10)
        self.assertEqual(initial.timestamp, 0)
        self.assertAlmostEqual(initial.entities[0].x, 0)
        self.assertAlmostEqual(initial.entities[0].y, 0)
        self.assertAlmostEqual(initial.entities[0].vx, 1)
        self.assertAlmostEqual(initial.entities[0].vy, -1)
        self.assertEqual(moved.timestamp, 10)
        self.assertAlmostEqual(moved.entities[0].x, 10)
        self.assertAlmostEqual(moved.entities[0].y, -10)
        self.assertAlmostEqual(moved.entities[0].vx, 1)
        self.assertAlmostEqual(moved.entities[0].vy, -1)

    def test_gravitation(self):
        physics_engine = physics.PEngine(
            flight_savefile=common.savefile('tests/massive-objects.json'))
        # In this case, the first entity is very massive and the second entity
        # should gravitate towards the first entity.
        initial = physics_engine.get_state(0)
        moved = physics_engine.get_state(1)
        self.assertAlmostEqual(initial.entities[1].vx, 0)
        # https://www.wolframalpha.com/input/?i=1e30+kg+*+G+%2F+(1e8+m)%5E2
        # According to the above, this should be somewhere between 6500 and
        # 7000 m/s after one second.
        self.assertTrue(moved.entities[1].vx > 5000,
                        msg=f'vx is actually {moved.entities[1].vx}')

        # Test the internal math that the internal derive function is doing
        # the right calculations. Break out your SPH4U physics equations!!
        X, Y, DX, DY = physics._y_from_state(initial)
        y_1d = np.concatenate((DX, DY, Xa, Ya), axis=None)
        Vx, Vy, Ax, Ay = \
            physics._extract_from_y1d(physics_engine._derive(0, y_1d))
        self.assertTrue(len(Vx) == len(Vy) == len(Ax) == len(Ay) == 2)
        self.assertAlmostEqual(Vx[0], 0)
        self.assertAlmostEqual(Vy[0], 0)
        self.assertAlmostEqual(abs(Ax[0]),
                               G * initial.entities[1].mass / (X[0] - X[1])**2)
        self.assertAlmostEqual(Ay[0], 0)

        self.assertAlmostEqual(Vx[1], 0)
        self.assertAlmostEqual(Vy[1], 0)
        self.assertAlmostEqual(abs(Ax[1]),
                               G * initial.entities[0].mass / (X[0] - X[1])**2)
        self.assertAlmostEqual(Ay[1], 0)


if __name__ == '__main__':
    unittest.main()

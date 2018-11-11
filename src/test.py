#!/usr/bin/env python3
import logging
import unittest

import common
import physics

log = logging.getLogger()


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
        self.assertAlmostEqual(initial.timestamp, 0)
        self.assertAlmostEqual(initial.entities[0].x, 0)
        self.assertAlmostEqual(initial.entities[0].y, 0)
        self.assertAlmostEqual(initial.entities[0].vx, 1)
        self.assertAlmostEqual(initial.entities[0].vy, -1)
        self.assertAlmostEqual(moved.timestamp, 10)
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

if __name__ == '__main__':
    unittest.main()

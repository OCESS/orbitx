#!/usr/bin/env python3
import logging
import sys
import unittest

import numpy as np

import orbitx.orbitx_pb2 as protos

import orbitx.common as common
import orbitx.physics as physics
from orbitx.physics_entity import Habitat, PhysicsEntity

log = logging.getLogger()

G = 6.67408e-11


class PhysicsEngine:
    """Ensures that the simthread is always shut down on test exit/failure."""

    def __init__(self, savefile):
        self.physics_engine = physics.PEngine(
            common.load_savefile(common.savefile(savefile)))

    def __enter__(self):
        return self.physics_engine

    def __exit__(self, *args):
        self.physics_engine._stop_simthread()


class PhysicsEngineTestCase(unittest.TestCase):
    def setUp(self):
        if '-v' in sys.argv:
            common.enable_verbose_logging()

    def test_simple_collision(self):
        with PhysicsEngine('tests/simple-collision.json') as physics_engine:
            # In this case, the first entity is standing still and the second
            # on a collision course going left to right. The two should bounce.
            # Entity 0 has r=50 and everything else 0.
            # Entity 2 has r=30, x=-500, vx=10, and everything else 0.
            # There's also entity 1, which is far away and shouldn't interact.
            # Let's do some math oh hey, they should collide at t=42.
            approach = physics_engine.get_state(41)
            bounced = physics_engine.get_state(43)
            self.assertTrue(approach.entities[0].x > approach.entities[2].x)
            self.assertTrue(approach.entities[2].vx > 0)
            self.assertTrue(bounced.entities[0].x > bounced.entities[2].x)
            self.assertTrue(bounced.entities[2].vx < 0)
            self.assertEqual(
                round(approach.entities[1].vy),
                round(bounced.entities[1].vy))

    def test_basic_movement(self):
        with PhysicsEngine('tests/only-sun.json') as physics_engine:
            # In this case, the only entity is the Sun. It starts at (0, 0)
            # with a speed of (1, -1). It should move.
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
        with PhysicsEngine('tests/massive-objects.json') as physics_engine:
            # In this case, the first entity is very massive and the second
            # entity should gravitate towards the first entity.
            initial = physics_engine.get_state(0)
            moved = physics_engine.get_state(1)
            # https://www.wolframalpha.com/input/?i=1e30+kg+*+G+%2F+(1e8+m)%5E2
            # According to the above, this should be somewhere between 6500 and
            # 7000 m/s after one second.
            self.assertTrue(moved.entities[1].vx > 5000,
                            msg=f'vx is actually {moved.entities[1].vx}')

            # Test the internal math that the internal derive function is doing
            # the right calculations. Break out your SPH4U physics equations!!
            y0 = physics.Y(initial)
            # Note that dy.X is actually the velocity at 0,
            # and dy.VX is acceleration.
            dy = physics.Y(physics_engine._derive(0, y0._y_1d))
            self.assertEqual(dy._n, 2)
            self.assertAlmostEqual(dy.X[0], y0.VX[0])
            self.assertAlmostEqual(dy.Y[0], y0.VY[0])
            self.assertEqual(round(abs(dy.VX[0])),
                             round(G * initial.entities[1].mass /
                                   (y0.X[0] - y0.X[1])**2))
            self.assertAlmostEqual(dy.VY[0], 0)

            self.assertAlmostEqual(dy.X[1], y0.VX[1])
            self.assertAlmostEqual(dy.Y[1], y0.VY[1])
            self.assertEqual(round(abs(dy.VX[1])),
                             round(G * initial.entities[0].mass /
                                   (y0.X[1] - y0.X[0])**2))
            self.assertAlmostEqual(dy.VY[1], 0)

    def test_engines(self):
        with PhysicsEngine('tests/habitat.json') as physics_engine:
            # In this test case, there is a single entity that has 300 kg fuel.
            # heading, velocity, and position are all 0.
            throttle = 1
            t_delta = 5

            physics_engine.handle_command(
                protos.Command(
                    ident=protos.Command.HAB_THROTTLE_CHANGE,
                    arg=throttle),
                requested_t=0)

            initial = physics_engine.get_state(0)
            moved = physics_engine.get_state(t_delta)

            self.assertAlmostEqual(initial.entities[0].heading, 0)

            self.assertAlmostEqual(
                moved.entities[0].fuel,
                (initial.entities[0].fuel -
                 t_delta * Habitat.fuel_cons(throttle=throttle)))
            self.assertAlmostEqual(
                moved.entities[0].vx,
                t_delta * Habitat.acceleration(
                    throttle=throttle, heading=initial.entities[0].heading)[0])

            t_no_fuel = (initial.entities[0].fuel /
                         Habitat.fuel_cons(throttle=throttle))
            empty_fuel = physics_engine.get_state(t_no_fuel)
            after_empty_fuel = physics_engine.get_state(t_no_fuel + t_delta)

            self.assertEqual(round(empty_fuel.entities[0].fuel), 0)
            self.assertEqual(round(after_empty_fuel.entities[0].vx),
                             round(empty_fuel.entities[0].vx))

    def test_three_body(self):
        with PhysicsEngine('tests/three-body.json') as physics_engine:
            # In this case, three entities form a 90-45-45 triangle, with the
            # entity at the right angle being about as massive as the sun.
            # The first entity is the massive entity, the second is far to the
            # left, and the third is far to the top.
            state = physics_engine.get_state(0)

            # Test that every single entity has the correct accelerations.
            y0 = physics.Y(state)
            dy = physics.Y(physics_engine._derive(0, y0._y_1d))
            self.assertEqual(dy._n, 3)

            self.assertAlmostEqual(dy.X[0], y0.VX[0])
            self.assertAlmostEqual(dy.Y[0], y0.VY[0])
            self.assertEqual(round(abs(dy.VX[0])),
                             round(G * state.entities[1].mass /
                                   (y0.X[0] - y0.X[1])**2))
            self.assertEqual(round(abs(dy.VY[0])),
                             round(G * state.entities[2].mass /
                                   (y0.Y[0] - y0.Y[2])**2))

            self.assertAlmostEqual(dy.X[1], y0.VX[1])
            self.assertAlmostEqual(dy.Y[1], y0.VY[1])
            self.assertEqual(round(abs(dy.VX[1])),
                             round(G * state.entities[0].mass /
                                   (y0.X[1] - y0.X[0])**2 +

                                   np.sqrt(2) * G * state.entities[2].mass /
                                   (y0.X[1] - y0.X[2])**2
                                   ))
            self.assertEqual(round(abs(dy.VY[1])),
                             round(np.sqrt(2) * G * state.entities[2].mass /
                                   (y0.X[1] - y0.X[2])**2))

            self.assertAlmostEqual(dy.X[2], y0.VX[2])
            self.assertAlmostEqual(dy.Y[2], y0.VY[2])
            self.assertEqual(round(abs(dy.VX[2])),
                             round(np.sqrt(2) * G * state.entities[2].mass /
                                   (y0.X[1] - y0.X[2])**2))
            self.assertEqual(round(abs(dy.VY[2])),
                             round(
                             G * state.entities[0].mass /
                             (y0.Y[2] - y0.Y[0])**2 +

                             np.sqrt(2) * G * state.entities[1].mass /
                             (y0.Y[2] - y0.Y[1])**2
                             ))

    def test_landing(self):
        with PhysicsEngine('tests/artificial-collision.json') \
                as physics_engine:
            # This case is the same as simple-collision, but the first entity
            # has the artificial flag set. Thus it should land and stick.
            # As in simple-collision, the collision happens at about t = 42.
            before = physics_engine.get_state(40)
            after = physics_engine.get_state(50)

            assert before.entities[0].artificial
            assert not before.entities[2].artificial

            self.assertTrue(before.entities[0].x > before.entities[2].x)
            self.assertTrue(before.entities[2].vx > 0)
            self.assertAlmostEqual(after.entities[0].vx, after.entities[2].vx)
            self.assertAlmostEqual(after.entities[0].x,
                                   (after.entities[2].x +
                                    after.entities[0].r +
                                    after.entities[2].r))


class PhysicsEntityTestCase(unittest.TestCase):
    """Tests that PhysicsEntity properly proxies underlying proto."""

    def test_fields(self):
        def test_field(pe: PhysicsEntity, field: str, val):
            pe.proto.Clear()
            setattr(pe, field, val)
            self.assertEqual(getattr(pe.proto, field), val)

        pe = PhysicsEntity(protos.Entity())
        test_field(pe, 'name', 'test')
        test_field(pe, 'x', 5)
        test_field(pe, 'y', 5)
        test_field(pe, 'vx', 5)
        test_field(pe, 'vy', 5)
        test_field(pe, 'r', 5)
        test_field(pe, 'mass', 5)
        test_field(pe, 'heading', 5)
        test_field(pe, 'spin', 5)
        test_field(pe, 'fuel', 5)
        test_field(pe, 'throttle', 5)
        test_field(pe, 'attached_to', 'other_test')
        test_field(pe, 'broken', True)
        test_field(pe, 'artificial', True)


if __name__ == '__main__':
    unittest.main()

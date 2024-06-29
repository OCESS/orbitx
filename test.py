#!/usr/bin/env python3
import logging
import sys
import unittest

import numpy as np

import orbitx.orbitx_pb2 as protos

from orbitx.physics import calc, ode_solver
from orbitx import common
from orbitx import logs
from orbitx import network
from orbitx import strings
from orbitx.common import N_COMPONENTS, N_COOLANT_LOOPS, N_RADIATORS
from orbitx.data_structures.engineering import EngineeringState
from orbitx.data_structures.entity import _EntityView, Entity
from orbitx.data_structures.space import PhysicsState
from orbitx.data_structures import savefile
from orbitx.physics import electroconstants
from orbitx.physics.simulation import PhysicsEngine
from orbitx.strings import HABITAT

log = logging.getLogger('orbitx')


class PhysicsEngineHarness:
    """Ensures that the simthread is always shut down on test exit/failure."""

    def __init__(self, savefile_name):
        self.physics_engine = PhysicsEngine(
            savefile.load_savefile(savefile.full_path(savefile_name)))

    def __enter__(self):
        return self.physics_engine

    def __exit__(self, *args):
        self.physics_engine._stop_simthread()


class PhysicsEngineTestCase(unittest.TestCase):
    """Test the motion of the simulated system is correct."""

    def test_simple_collision(self):
        """Test elastic collisions of two small-mass objects colliding."""
        with PhysicsEngineHarness('tests/simple-collision.json') as physics_engine:
            # In this case, the first entity is standing still and the second
            # on a collision course going left to right. The two should bounce.
            # Entity 0 has r=50 and everything else 0.
            # Entity 2 has r=30, x=-500, vx=10, and everything else 0.
            # There's also entity 1, which is far away and shouldn't interact.
            # Let's do some math oh hey, they should collide at t=42.
            approach = physics_engine.get_state(41)
            bounced = physics_engine.get_state(43)
            self.assertTrue(approach[0].x > approach[2].x)
            self.assertTrue(approach[2].vx > 0)
            self.assertTrue(bounced[0].x > bounced[2].x)
            self.assertTrue(bounced[2].vx < 0)
            self.assertEqual(
                round(approach[1].vy),
                round(bounced[1].vy))

    def test_basic_movement(self):
        """Test that a moving object changes its position."""
        with PhysicsEngineHarness('tests/only-sun.json') as physics_engine:
            # In this case, the only entity is the Sun. It starts at (0, 0)
            # with a speed of (1, -1). It should move.
            initial = physics_engine.get_state(1)
            moved = physics_engine.get_state(100)
            t0 = initial.timestamp
            t1 = moved.timestamp
            self.assertEqual(initial.timestamp, 1)
            self.assertAlmostEqual(initial[0].x, 0)
            self.assertAlmostEqual(initial[0].y, 0)
            self.assertAlmostEqual(initial[0].vx, 1)
            self.assertAlmostEqual(initial[0].vy, -1)
            self.assertEqual(moved.timestamp, t1)
            self.assertAlmostEqual(moved[0].x, t1 - t0)
            self.assertAlmostEqual(moved[0].y, -(t1 - t0))
            self.assertAlmostEqual(moved[0].vx, 1)
            self.assertAlmostEqual(moved[0].vy, -1)

    def test_gravitation(self):
        """Test that gravitational acceleration at t=0 is as expected."""
        with PhysicsEngineHarness('tests/massive-objects.json') as physics_engine:
            # In this case, the first entity is very massive and the second
            # entity should gravitate towards the first entity.
            t0 = 1
            t1 = 2
            initial = physics_engine.get_state(t0)
            moved = physics_engine.get_state(t1)
            # https://www.wolframalpha.com/input/?i=1e30+kg+*+G+%2F+(1e8+m)%5E2
            # According to the above, this should be somewhere between 6500 and
            # 7000 m/s after one second.
            self.assertTrue(moved[1].vx > 5000,
                            msg=f'vx is actually {moved[1].vx}')

            # Test the internal math that the internal derive function is doing
            # the right calculations. Break out your SPH4U physics equations!!
            y0 = initial
            # Note that dy.X is actually the velocity at 0,
            # and dy.VX is acceleration.
            dy = PhysicsState(
                ode_solver.simulation_differential_function(
                    0, y0.y0(), y0._proto_state, physics_engine.M, physics_engine._artificials),
                y0._proto_state)
            self.assertEqual(len(dy.X), 2)
            self.assertAlmostEqual(dy.X[0], y0.VX[0])
            self.assertAlmostEqual(dy.Y[0], y0.VY[0])
            self.assertEqual(round(abs(dy.VX[0])),
                             round(common.G * initial[1].mass
                                   / (y0.X[0] - y0.X[1]) ** 2))
            self.assertAlmostEqual(dy.VY[0], 0)

            self.assertAlmostEqual(dy.X[1], y0.VX[1])
            self.assertAlmostEqual(dy.Y[1], y0.VY[1])
            self.assertEqual(round(abs(dy.VX[1])),
                             round(common.G * initial[0].mass
                                   / (y0.X[1] - y0.X[0]) ** 2))
            self.assertAlmostEqual(dy.VY[1], 0)

    def test_engines(self):
        """Test that engines use fuel and accelerate at the expected."""
        with PhysicsEngineHarness('tests/habitat.json') as physics_engine:
            # In this test case, there is a single entity that has 300 kg fuel.
            # heading, velocity, and position are all 0.
            throttle = 1
            t0 = 1
            t1 = 5

            physics_engine.handle_requests([
                common.Request(
                    ident=common.Request.HAB_THROTTLE_SET,
                    throttle_set=throttle)],
                requested_t=t0)

            initial = physics_engine.get_state(t0)
            moved = physics_engine.get_state(t1)

            self.assertAlmostEqual(initial[0].heading, 0)

            self.assertAlmostEqual(
                moved[0].fuel,
                (initial[0].fuel
                 - (t1 - t0) * throttle
                 * common.craft_capabilities[HABITAT].fuel_cons))
            self.assertTrue(
                moved[0].vx
                < ((t1 - t0) * calc.engine_acceleration(moved)))

            t_no_fuel = t0 + initial[0].fuel / (throttle * common.craft_capabilities[HABITAT].fuel_cons)
            empty_fuel = physics_engine.get_state(t_no_fuel)
            after_empty_fuel = physics_engine.get_state(t_no_fuel + (t1 - t0))

            self.assertEqual(round(empty_fuel[0].fuel), 0)
            self.assertEqual(round(after_empty_fuel[0].vx),
                             round(empty_fuel[0].vx))

    def test_srbs(self):
        """Test that SRBs move the craft, and run out of fuel."""
        with PhysicsEngineHarness('tests/habitat.json') as physics_engine:
            t0 = 1
            t1 = 5
            physics_engine.handle_requests(
                [common.Request(ident=common.Request.IGNITE_SRBS)],
                requested_t=t0)

            initial = physics_engine.get_state(t0)
            moved = physics_engine.get_state(t1)

            self.assertAlmostEqual(initial[0].heading, 0)
            self.assertAlmostEqual(initial[0].vx, 0)
            self.assertAlmostEqual(moved[0].vx,
                                   (t1 - t0) * calc.engine_acceleration(moved))

            srb_empty = physics_engine.get_state(common.SRB_BURNTIME + t0)
            after_srb_empty = physics_engine.get_state(common.SRB_BURNTIME + (t1 - t0))

            self.assertAlmostEqual(srb_empty[0].vx, after_srb_empty[0].vx)

    def test_three_body(self):
        """Test gravitational acceleration between three bodies is expected."""
        with PhysicsEngineHarness('tests/three-body.json') as physics_engine:
            # In this case, three entities form a 90-45-45 triangle, with the
            # entity at the right angle being about as massive as the sun.
            # The first entity is the massive entity, the second is far to the
            # left, and the third is far to the top.
            physics_state = physics_engine.get_state(1)

            # Test that every single entity has the correct accelerations.
            y0 = physics_state
            dy = PhysicsState(
                ode_solver.simulation_differential_function(
                    0, y0.y0(), y0._proto_state, physics_engine.M, physics_engine._artificials),
                physics_state._proto_state)
            self.assertEqual(len(dy.X), 3)

            self.assertAlmostEqual(dy.X[0], y0.VX[0])
            self.assertAlmostEqual(dy.Y[0], y0.VY[0])
            self.assertEqual(round(abs(dy.VX[0])),
                             round(common.G * physics_state[1].mass
                                   / (y0.X[0] - y0.X[1]) ** 2))
            self.assertEqual(round(abs(dy.VY[0])),
                             round(common.G * physics_state[2].mass
                                   / (y0.Y[0] - y0.Y[2]) ** 2))

            self.assertAlmostEqual(dy.X[1], y0.VX[1])
            self.assertAlmostEqual(dy.Y[1], y0.VY[1])
            self.assertEqual(round(abs(dy.VX[1])),
                             round(common.G * physics_state[0].mass
                                   / (y0.X[1] - y0.X[0]) ** 2

                                   + np.sqrt(2) * common.G
                                   * physics_state[2].mass
                                   / (y0.X[1] - y0.X[2]) ** 2
                                   ))
            self.assertEqual(round(abs(dy.VY[1])),
                             round(np.sqrt(2) * common.G
                                   * physics_state[2].mass
                                   / (y0.X[1] - y0.X[2]) ** 2))

            self.assertAlmostEqual(dy.X[2], y0.VX[2])
            self.assertAlmostEqual(dy.Y[2], y0.VY[2])
            self.assertEqual(round(abs(dy.VX[2])),
                             round(np.sqrt(2) * common.G
                                   * physics_state[2].mass
                                   / (y0.X[1] - y0.X[2]) ** 2))
            self.assertEqual(round(abs(dy.VY[2])),
                             round(
                                 common.G * physics_state[0].mass
                                 / (y0.Y[2] - y0.Y[0]) ** 2

                                 + np.sqrt(2) * common.G * physics_state[1].mass
                                 / (y0.Y[2] - y0.Y[1]) ** 2
            ))

    def test_landing(self):
        with PhysicsEngineHarness('tests/artificial-collision.json') \
                as physics_engine:
            # This case is the same as simple-collision, but the first entity
            # has the artificial flag set. Thus it should land and stick.
            # As in simple-collision, the collision happens at about t = 42.
            before = physics_engine.get_state(40)
            after = physics_engine.get_state(50)

            assert before[0].artificial
            assert not before[2].artificial

            self.assertTrue(before[0].x > before[2].x)
            self.assertTrue(before[2].vx > 0)
            self.assertAlmostEqual(after[0].vx, after[2].vx)
            self.assertAlmostEqual(after[0].x,
                                   (after[2].x
                                    + after[0].r
                                    + after[2].r))

    def test_longterm_stable_landing(self):
        """Test that landed ships have stable altitude in the long term."""
        savestate = savefile.load_savefile(savefile.full_path('OCESS.json'))
        initial_t = savestate.timestamp
        with PhysicsEngineHarness('OCESS.json') as physics_engine:
            initial = physics_engine.get_state(initial_t + 10)
            physics_engine.handle_requests(
                [common.Request(ident=common.Request.TIME_ACC_SET,
                                 time_acc_set=common.TIME_ACCS[-1].value)],
                requested_t=initial_t + 10)
            final = physics_engine.get_state(initial_t + 100_000)
            self.assertAlmostEqual(
                calc.fastnorm(initial['Earth'].pos - initial['Habitat'].pos),
                initial['Earth'].r + initial['Habitat'].r,
                delta=1)
            self.assertAlmostEqual(
                calc.fastnorm(final['Earth'].pos - final['Habitat'].pos),
                final['Earth'].r + final['Habitat'].r,
                delta=1)

    def test_drag(self):
        """Test that drag is small but noticeable during unpowered flight."""
        atmosphere_save = savefile.load_savefile(savefile.full_path(
            'tests/atmosphere.json'))
        # The habitat starts 1 km in the air, the same speed as the Earth.

        hab = atmosphere_save.craft_entity()
        hab.vy += 10
        atmosphere_save[atmosphere_save.craft] = hab
        drag = calc.fastnorm(calc.drag(atmosphere_save))
        self.assertLess(59, drag)
        self.assertGreater(60, drag)


class EntityTestCase(unittest.TestCase):
    """Tests that state.Entity properly proxies underlying proto."""

    def test_fields(self):
        def test_field(pe: Entity, field: str, val):
            pe.proto.Clear()
            setattr(pe, field, val)
            self.assertEqual(getattr(pe.proto, field), val)

        pe = Entity(protos.Entity())
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
        test_field(pe, 'landed_on', 'other_test')
        test_field(pe, 'broken', True)
        test_field(pe, 'artificial', True)


class PhysicsStateTestCase(unittest.TestCase):
    """Tests state.PhysicsState accessors and setters."""

    proto_state = protos.PhysicalState(
        timestamp=5,
        entities=[
            protos.Entity(
                name='First', mass=100, r=200,
                x=10, y=20, vx=30, vy=40, heading=7, spin=50, fuel=60,
                throttle=70),
            protos.Entity(
                name='Second', mass=101, r=201, artificial=True,
                x=11, y=21, vx=31, vy=41, heading=2, spin=51, fuel=61,
                throttle=71, landed_on='First', broken=True)
        ],
        engineering=protos.EngineeringState(
            components=[protos.EngineeringState.Component()] * N_COMPONENTS,
            coolant_loops=[protos.EngineeringState.CoolantLoop()] * N_COOLANT_LOOPS,
            radiators=[protos.EngineeringState.Radiator()] * N_RADIATORS
        )
    )

    def test_landed_on(self):
        """Test that the special .landed_on field is properly set."""
        ps = PhysicsState(None, self.proto_state)
        self.assertEqual(ps['First'].landed_on, '')
        self.assertEqual(ps['Second'].landed_on, 'First')

    def test_y_vector_init(self):
        """Test that initializing with a y-vector uses y-vector values."""
        # If you change the y-vector ordering, change here too #Y_VECTOR_CHANGESITE

        eng_fields = np.zeros(EngineeringState.N_ENGINEERING_FIELDS)
        component_array = eng_fields[EngineeringState._COMPONENT_START_INDEX:EngineeringState._COMPONENT_END_INDEX]
        for comp_i in range(0, N_COMPONENTS):
            component_array[comp_i + N_COMPONENTS * 0] = True  # connected
            component_array[comp_i + N_COMPONENTS * 1] = 1 + (0.01 * comp_i)  # capacity
            component_array[comp_i + N_COMPONENTS * 2] = 222200 + comp_i  # temperature
            component_array[comp_i + N_COMPONENTS * 3] = comp_i % 2  # coolant_hab_one
            component_array[comp_i + N_COMPONENTS * 4] = True  # coolant_hab_two
            component_array[comp_i + N_COMPONENTS * 5] = False  # coolant_ayse

        coolant_array = eng_fields[EngineeringState._COOLANT_START_INDEX:EngineeringState._COOLANT_END_INDEX]
        for cool_i in range(0, N_COOLANT_LOOPS):
            coolant_array[cool_i + N_COOLANT_LOOPS * 0] = 555500 + cool_i  # coolant_temp
            coolant_array[cool_i + N_COOLANT_LOOPS * 1] = cool_i % 2  # primary_pump_on
            coolant_array[cool_i + N_COOLANT_LOOPS * 2] = True  # secondary_pump_on

        rad_array = eng_fields[EngineeringState._RADIATOR_START_INDEX:EngineeringState._RADIATOR_END_INDEX]
        for rad_i in range(0, N_RADIATORS):
            rad_array[rad_i + N_RADIATORS * 0] = rad_i % 4  # attached_to_coolant_loop
            rad_array[rad_i + N_RADIATORS * 1] = rad_i % 2  # functioning

        y0 = np.concatenate((np.array([
            0x111, 0x222,  # x
            0x333, 0x444,  # y
            0x555, 0x777,  # vx
            0x888, 0x999,  # vy
            0.01, 0.02,  # heading
            0.03, 0.04,  # spin
            0xEEE, 0xFFF,  # fuel
            5, 6,  # throttle
            1, -1,  # only First is landed on Second
            0, 1,  # Second is broken
            common.SRB_EMPTY,
            1  # time_acc
        ]),
            eng_fields
        ))

        ps = PhysicsState(y0, self.proto_state)
        self.assertTrue(np.array_equal(ps.y0(), y0.astype(ps.y0().dtype)))
        self.assertEqual(ps['First'].landed_on, 'Second')

        proto_state = ps.as_proto()
        proto_state.timestamp = 50
        self.assertEqual(proto_state.entities[0].x, 0x111)
        self.assertEqual(proto_state.entities[0].y, 0x333)
        self.assertEqual(proto_state.entities[1].x, 0x222)
        self.assertEqual(proto_state.entities[1].y, 0x444)
        self.assertEqual(proto_state.entities[0].vx, 0x555)
        self.assertEqual(proto_state.entities[0].vy, 0x888)
        self.assertEqual(proto_state.entities[1].vx, 0x777)
        self.assertEqual(proto_state.entities[1].vy, 0x999)
        self.assertEqual(proto_state.entities[0].heading, 0.01)
        self.assertEqual(proto_state.entities[1].heading, 0.02)
        self.assertEqual(proto_state.entities[0].spin, 0.03)
        self.assertEqual(proto_state.entities[1].spin, 0.04)
        self.assertEqual(proto_state.entities[0].fuel, 0xEEE)
        self.assertEqual(proto_state.entities[1].fuel, 0xFFF)
        self.assertEqual(proto_state.entities[0].landed_on, 'Second')
        self.assertEqual(proto_state.entities[1].landed_on, '')
        self.assertEqual(proto_state.timestamp, 50)
        self.assertTrue(proto_state.entities[1].broken)

        for i, component in enumerate(ps.engineering.components):
            self.assertEqual(component.connected, True, msg=i)
            self.assertEqual(component.capacity, 1 + (0.01 * i), msg=i)
            self.assertEqual(component.temperature, 222200 + i, msg=i)
            self.assertEqual(component.coolant_hab_one, bool(i % 2), msg=i)
            self.assertEqual(component.coolant_hab_two, True, msg=i)
            self.assertEqual(component.coolant_ayse, False, msg=i)

        for i, coolant in enumerate(ps.engineering.coolant_loops):
            self.assertEqual(coolant.coolant_temp, 555500 + i, msg=i)
            self.assertEqual(coolant.primary_pump_on, bool(i % 2), msg=i)
            self.assertEqual(coolant.secondary_pump_on, True, msg=i)

        for i, radiator in enumerate(ps.engineering.radiators):
            pass
            self.assertEqual(radiator.attached_to_coolant_loop, i % 4, msg=i)
            self.assertEqual(radiator.functioning, bool(i % 2), msg=i)

    def test_get_set(self):
        """Test __getitem__ and __setitem__."""
        ps = PhysicsState(None, self.proto_state)
        entity = ps[0]
        entity.landed_on = 'Second'
        ps[0] = entity
        self.assertEqual(ps[0].landed_on, 'Second')

    def test_entity_view(self):
        """Test that setting and getting _EntityView attrs propagate."""
        ps = PhysicsState(None, self.proto_state)
        self.assertEqual(ps[0].name, 'First')
        entity = ps[0]
        self.assertTrue(isinstance(entity, _EntityView))

        self.assertEqual(entity.x, 10)
        self.assertEqual(entity.y, 20)
        self.assertEqual(entity.vx, 30)
        self.assertEqual(entity.vy, 40)
        self.assertEqual(entity.spin, 50)
        self.assertEqual(entity.fuel, 60)
        self.assertEqual(entity.landed_on, '')
        self.assertEqual(entity.throttle, 70)

        ps.y0()
        self.assertEqual(entity.heading, 7 % (2 * np.pi))

        ps[0].landed_on = 'Second'
        self.assertEqual(entity.landed_on, 'Second')
        entity.x = 500
        self.assertEqual(ps[0].x, 500)
        entity.pos = np.array([55, 66])
        self.assertEqual(ps['First'].x, 55)
        self.assertEqual(ps['First'].y, 66)


class CalculationsTestCase(unittest.TestCase):
    """Tests instantaneous orbit parameter calculations.

    The file tests/gui-test.json encodes the position of the Earth and the
    ISS, with all possitions offset by a billion metres along the x and y axes.
    https://www.wolframalpha.com/input/?i=International+Space+Station
    describes the orbital parameters of the ISS, all numbers in this test are
    taken from that page."""

    def test_elliptical_orbital_parameters(self):
        # Again, see
        # https://www.wolframalpha.com/input/?i=International+Space+Station
        # For these expected values
        physics_state = savefile.load_savefile(savefile.full_path(
            'tests/gui-test.json'))
        iss = physics_state[0]
        earth = physics_state[1]

        # The semiaxes are relatively close to expected.
        self.assertAlmostEqual(
            calc.semimajor_axis(iss, earth), 6785e3, delta=0.01 * earth.r)

        # The eccentricity is within 1e-6 of the expected.
        self.assertAlmostEqual(
            calc.fastnorm(calc.eccentricity(iss, earth)),
            5.893e-4, delta=1e-3)

        # The apoapsis is relatively close to expected.
        self.assertAlmostEqual(
            calc.apoapsis(iss, earth), 418.3e3, delta=0.01 * earth.r)

        # The periapsis is relatively close to expected.
        self.assertAlmostEqual(
            calc.periapsis(iss, earth), 410.3e3, delta=0.01 * earth.r)

    def test_hyperbolic_orbital_parameters(self):
        # Unlike the elliptical test, this tests our favourite extra-solar
        # visitor to make sure we can calculate Keplerian orbital
        # characteristics from its orbital state vectors! That's right, we're
        # talking about Sedna! The expected values are arrived at through
        # calculation, and also
        # http://orbitsimulator.com/formulas/OrbitalElements.html
        physics_state = savefile.load_savefile(savefile.full_path(
            'tests/sedna.json'))
        sun = physics_state[0]
        oumuamua = physics_state[1]

        expected_semimajor_axis = -71231070.14146987
        self.assertAlmostEqual(
            calc.semimajor_axis(oumuamua, sun), expected_semimajor_axis,
            delta=abs(0.01 * expected_semimajor_axis))

        expected_eccentricity = 1644.477
        self.assertAlmostEqual(
            calc.fastnorm(calc.eccentricity(oumuamua, sun)),
            expected_eccentricity, delta=0.01 * expected_eccentricity)

        expected_periapsis = 1.1714e11  # Through calculation
        self.assertAlmostEqual(
            calc.periapsis(sun, oumuamua) + oumuamua.r, expected_periapsis,
            delta=0.01 * 78989185420.15271)

    def test_speeds(self):
        physics_state = savefile.load_savefile(savefile.full_path(
            'tests/gui-test.json'))
        iss = physics_state[0]
        earth = physics_state[1]

        self.assertAlmostEqual(calc.h_speed(iss, earth), 7665, delta=10)
        self.assertAlmostEqual(calc.v_speed(iss, earth), -0.1, delta=0.1)


class EngineeringViewTestCase(unittest.TestCase):
    """Test that the various accessors of EngineeringState are correct."""

    def test_component_accessors(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        # Test getters work
        self.assertEqual(engineering.components[0].connected, True)
        self.assertAlmostEqual(engineering.components[0].capacity, 0.9, delta=0.1)
        self.assertAlmostEqual(engineering.components[0].temperature, 31.3, delta=0.1)
        self.assertEqual(engineering.components[0].coolant_hab_one, True)
        self.assertAlmostEqual(engineering.coolant_loops[0].coolant_temp, 15.0)
        self.assertAlmostEqual(engineering.components[0].connected_coolant_loops()[0].coolant_temp, 15.0)

        # Test setters work
        engineering.components[1].connected = True
        engineering.components[1].capacity = 0.8
        engineering.components[1].temperature = 12.3
        engineering.components[1].coolant_hab_one = True
        engineering.coolant_loops[0].coolant_temp = 20.0
        self.assertEqual(engineering.components[1].connected, True)
        self.assertAlmostEqual(engineering.components[1].capacity, 0.8)
        self.assertAlmostEqual(engineering.components[1].temperature, 12.3)
        self.assertEqual(engineering.components[1].coolant_hab_one, True)
        self.assertAlmostEqual(engineering.coolant_loops[0].coolant_temp, 20.0)
        self.assertAlmostEqual(engineering.components[1].connected_coolant_loops()[0].coolant_temp, 20.0)

    def test_as_proto(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            state = physics_engine.get_state()
            engineering = state.engineering

        # Change some data
        engineering.components[1].connected = True
        engineering.components[1].capacity = 0.7
        engineering.components[1].temperature = 12.3

        # Check engineering proto
        eng_proto = engineering.as_proto()
        self.assertEqual(eng_proto.components[1].connected, True)
        self.assertAlmostEqual(eng_proto.components[1].capacity, 0.7)
        self.assertAlmostEqual(eng_proto.components[1].temperature, 12.3)

        # Check physicsstate proto
        physics_state_proto = state.as_proto()
        self.assertEqual(physics_state_proto.engineering.components[1].connected, True)
        self.assertAlmostEqual(physics_state_proto.engineering.components[1].capacity, 0.7)
        self.assertAlmostEqual(physics_state_proto.engineering.components[1].temperature, 12.3)

    def test_coolant_accessors(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        # Test getters work
        self.assertAlmostEqual(engineering.coolant_loops[0].coolant_temp, 15.0)
        self.assertEqual(engineering.coolant_loops[0].primary_pump_on, True)
        self.assertEqual(engineering.coolant_loops[0].secondary_pump_on, True)

        # Test setters work
        engineering.coolant_loops[1].coolant_temp = 33.3
        engineering.coolant_loops[1].primary_pump_on = False
        engineering.coolant_loops[1].secondary_pump_on = True
        self.assertAlmostEqual(engineering.coolant_loops[1].coolant_temp, 33.3)
        self.assertEqual(engineering.coolant_loops[1].primary_pump_on, False)
        self.assertEqual(engineering.coolant_loops[1].secondary_pump_on, True)

    def test_radiator_accessors(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        # Test getters work
        self.assertEqual(engineering.radiators[0].attached_to_coolant_loop, 1)
        self.assertEqual(engineering.radiators[0].functioning, True)
        self.assertEqual(engineering.radiators[0].get_coolant_loop().coolant_temp, 15)

        # Test setters work
        engineering.radiators[1].attached_to_coolant_loop = 2
        engineering.radiators[1].functioning = False
        self.assertEqual(engineering.radiators[1].attached_to_coolant_loop, 2)
        self.assertEqual(engineering.radiators[1].functioning, False)
        self.assertEqual(engineering.radiators[1].get_coolant_loop().coolant_temp, 20)

    def test_numpy_arrays_not_copied(self):
        """Test that the internal array representation of EngineeringState is
        just a view into PhysicsState._array_rep, otherwise EngineeringState will
        write new data into the ether and it won't update PhysicsState.y0()."""
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            state = physics_engine.get_state()

        engineering = state.engineering
        engineering.components[0].temperature = 777777.7
        self.assertEqual(engineering._array[2 * N_COMPONENTS], 777777.7)
        self.assertEqual(state.y0()[state.ENGINEERING_START_INDEX + 2 * N_COMPONENTS], 777777.7)

    def test_eng_single_fields(self):
        """Test that non-repeated fields in the EngineeringState can be
           accessed/set properly."""
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        self.assertEqual(engineering.master_alarm, False)
        self.assertEqual(engineering.radiation_alarm, False)
        self.assertEqual(engineering.asteroid_alarm, False)
        self.assertEqual(engineering.hab_reactor_alarm, False)
        self.assertEqual(engineering.ayse_reactor_alarm, False)
        self.assertEqual(engineering.hab_gnomes, False)
        self.assertEqual(engineering.rad_shield_percentage, 5)

        engineering.master_alarm = True
        engineering.radiation_alarm = True
        engineering.asteroid_alarm = True
        engineering.hab_reactor_alarm = True
        engineering.ayse_reactor_alarm = True
        engineering.hab_gnomes = True
        engineering.rad_shield_percentage = 69

        self.assertEqual(engineering.master_alarm, True)
        self.assertEqual(engineering.radiation_alarm, True)
        self.assertEqual(engineering.asteroid_alarm, True)
        self.assertEqual(engineering.hab_reactor_alarm, True)
        self.assertEqual(engineering.ayse_reactor_alarm, True)
        self.assertEqual(engineering.hab_gnomes, True)
        self.assertEqual(engineering.rad_shield_percentage, 69)

    def test_misc_accessors(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            physics_state = physics_engine.get_state()

        self.assertAlmostEqual(physics_state.engineering.habitat_fuel, 100)

        physics_state[HABITAT].fuel = 50.0

        self.assertAlmostEqual(physics_state.engineering.habitat_fuel, 50)

    def test_convenience_accessors(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        self.assertTrue(engineering.components[6].coolant_hab_one)

        connected_loops = engineering.components[6].connected_coolant_loops()

        self.assertEqual(connected_loops[0]._n, 0)
        self.assertEqual(len(connected_loops), 1)

        connected_loops[0].coolant_temp = 69.0

        self.assertAlmostEqual(engineering.coolant_loops[0].coolant_temp, 69.0)

    def test_component_coolant_connection_list(self):
        """
        Test that the CoolantConnectionMatrix is returning the correct size of a matrix
        """
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        connected_loops = engineering.components.CoolantConnectionMatrix()

        self.assertEqual(connected_loops.shape, (3, N_COMPONENTS))

    def test_component_coolant_matrix_math(self):
        """
        Test that the matrix math to be used for something actually works
        """
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        coolant_connection_matrix = engineering.components.CoolantConnectionMatrix()

        self.assertTrue(engineering.components[0].coolant_hab_one)
        self.assertEqual(coolant_connection_matrix[0][0], 1.0)

        self.assertTrue(engineering.components[6].coolant_hab_one)
        self.assertEqual(coolant_connection_matrix[0][6], 1.0)

        self.assertTrue(engineering.components[strings.ION1].coolant_hab_two)
        self.assertEqual(coolant_connection_matrix[1][strings.COMPONENT_NAMES.index(strings.ION1)], 1.0)

    def test_electricals_accessors(self):
        """
        Basic checks for the OhmicVars of all components.
        """
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        electricals = engineering.components.Electricals()

        # Check RADS1 is drawing power
        self.assertEqual(engineering.components[strings.RADS1].connected, True)
        self.assertNotEqual(engineering.components[strings.RADS1].capacity, 0.0)
        self.assertNotEqual(electricals[strings.RADS1].resistance, np.inf)
        self.assertNotEqual(electricals[strings.RADS1].current, 0.0)
        self.assertAlmostEqual(
            electricals[strings.RADS1].voltage, electroconstants.HAB_PRIMARY_BUS.nominal_voltage,
            delta=50  # Voltage is within 50 V of nominal.
        )

        # Check ACC1 is not drawing power, i.e. the opposite of RADS1
        self.assertNotEqual(engineering.components[strings.ACC1].connected, True)
        self.assertEqual(electricals[strings.ACC1].resistance, np.inf)
        self.assertEqual(electricals[strings.ACC1].current, 0.0)


class CoolantTestCase(unittest.TestCase):

    def test_component_coolant_connection_list(self):
        """
        Test that the CoolantConnectionMatrix is returning the correct size of a matrix
        """
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering

        connected_loops = engineering.components.CoolantConnectionMatrix()
        self.assertEqual(connected_loops.shape, (3, N_COMPONENTS))

    def test_component_coolant(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            initial = physics_engine.get_state(1).engineering
            final = physics_engine.get_state(20).engineering

        # Component 25 is ION1, which starts with some temperature.
        self.assertNotEqual(
            initial.components[strings.ION1],
            electroconstants.RESTING_TEMPERATURE[strings.COMPONENT_NAMES.index(strings.ION1)]
        )
        temperature_1 = initial.components[strings.ION1].temperature
        temperature_2 = final.components[strings.ION1].temperature
        self.assertNotEqual(temperature_1, temperature_2)


class ElectrofunctionsTestCase(unittest.TestCase):
    def test_debug_print(self):
        with PhysicsEngineHarness('tests/engineering-test.json') as physics_engine:
            engineering = physics_engine.get_state().engineering
        for bus in engineering.BusElectricals().items():
            log.debug(bus)
        # TODO: Maybe check the main hab bus resistors, get some actual values, and see if we get
        # the right numbers and they're consistent with orbitv?


def test_performance():
    # This just runs for 10 seconds and collects profiling data.
    import time

    with PhysicsEngineHarness('OCESS.json') as physics_engine:
        physics_engine.handle_requests([
            common.Request(ident=common.Request.TIME_ACC_SET,
                            time_acc_set=1000)])

        initial_state = physics_engine.get_state()  # Warm up the simulation
        simtime_to_simulate = initial_state.timestamp + initial_state.time_acc * 1000

        print('Starting profiler...')
        common.start_profiling()

        physics_engine.get_state(simtime_to_simulate)


if __name__ == '__main__':
    print('------------------------------------------------')
    print('Logs are being written to the `logs/` directory.')
    print('If you\'re seeing some strange behaviour, check')
    print('those logs for more info.')
    print('You can also print all logs to the command-line')
    print('by using verbose mode: `python test.py -v`')
    print('')
    print('You can also run one specific test case, e.g.:')
    print('`python test.py PhysicsEngineTestCase.test_basic_movement`')
    print('')
    print('Running OrbitX test suite! Cross your fingers...')
    print('------------------------------------------------')
    logs.make_program_logfile('test')
    if '-v' in sys.argv:
        logs.enable_verbose_logging()

    if 'profile' in sys.argv:
        test_performance()
    else:
        unittest.main()

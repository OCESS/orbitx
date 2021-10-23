"""
Miscellaneous helper functions for physics simulation stuff.

There are no complex classes in this file.
"""

from typing import Tuple, Optional
import logging

import numpy as np
from google.protobuf.text_format import MessageToString

from orbitx import common
from orbitx.physics import calc
from orbitx.data_structures import (
    protos, Entity, Navmode, PhysicsState,
    Request
    )
from orbitx.strings import AYSE, HABITAT, MODULE

log = logging.getLogger()


def _reconcile_entity_dynamics(y: PhysicsState) -> PhysicsState:
    """Idempotent helper that sets velocities and spins of some entities.
    This is in its own function because it has a couple calling points."""
    # Navmode auto-rotation
    if y.navmode != Navmode['Manual']:
        craft = y.craft_entity()
        craft.spin = calc.navmode_spin(y)

    # Keep landed entities glued together
    landed_on = y.LandedOn
    for index in landed_on:
        # If we're landed on something, make sure we move in lockstep.
        lander = y[index]
        ground = y[landed_on[index]]

        if ground.name == AYSE and lander.name == HABITAT:
            # Always put the Habitat at the docking port.
            lander.pos = (
                    ground.pos
                    - calc.heading_vector(ground.heading)
                    * (lander.r + ground.r))
        else:
            norm = lander.pos - ground.pos
            unit_norm = norm / calc.fastnorm(norm)
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
        calc.fastnorm(calc.rotational_speed(e1, e2) - e1.v) >
        common.craft_capabilities[e1.name].hull_strength
    )

    # set right heading for future takeoff
    e2_opposite = e2.heading + np.pi
    e1.pos = e2.pos + (e1.r + e2.r) * calc.heading_vector(e2_opposite)
    e1.heading = e2_opposite % (2 * np.pi)
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
    unit_norm = norm / calc.fastnorm(norm)
    # The unit tangent is perpendicular to the unit normal vector
    unit_tang = np.asarray([-unit_norm[1], unit_norm[0]])

    # Calculate both normal and tangent velocities for both entities
    v1n = np.dot(unit_norm, e1.v)
    v1t = np.dot(unit_tang, e1.v)
    v2n = np.dot(unit_norm, e2.v)
    v2t = np.dot(unit_tang, e2.v)

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
        calc.fastnorm(calc.rotational_speed(e1, e2) - e1.v) >
        common.craft_capabilities[e1.name].hull_strength
    )

    # set right heading for future takeoff
    norm = e1.pos - e2.pos
    e1.heading = np.arctan2(norm[1], norm[0])
    e1.throttle = 0
    e1.spin = e2.spin
    e1.v = calc.rotational_speed(e1, e2)

def _one_request(request: Request, y0: PhysicsState) \
        -> PhysicsState:
    """Interface to set habitat controls.

    Use an argument to change habitat throttle or spinning, and simulation
    will restart with this new information."""
    log.info(f'At simtime={y0.timestamp}, '
             f'Got command {MessageToString(request, as_one_line=True)}')

    if request.ident != Request.TIME_ACC_SET:
        # Reveal the type of y0.craft as str (not None).
        assert y0.craft is not None

    if request.ident == Request.HAB_SPIN_CHANGE:
        if y0.navmode != Navmode['Manual']:
            # We're in autopilot, ignore this command
            return y0
        craft = y0.craft_entity()
        if not craft.landed():
            craft.spin += request.spin_change
    elif request.ident == Request.HAB_THROTTLE_CHANGE:
        y0.craft_entity().throttle += request.throttle_change
    elif request.ident == Request.HAB_THROTTLE_SET:
        y0.craft_entity().throttle = request.throttle_set
    elif request.ident == Request.TIME_ACC_SET:
        assert request.time_acc_set >= 0
        y0.time_acc = request.time_acc_set
    elif request.ident == Request.ENGINEERING_UPDATE:
        # Multiply this value by 100, because OrbitV considers engines at
        # 100% to be 100x the maximum thrust.
        common.craft_capabilities[HABITAT] = \
            common.craft_capabilities[HABITAT]._replace(
                thrust=100 * request.engineering_update.max_thrust)
        hab = y0[HABITAT]
        ayse = y0[AYSE]
        hab.fuel = request.engineering_update.hab_fuel
        ayse.fuel = request.engineering_update.ayse_fuel
        y0[HABITAT] = hab
        y0[AYSE] = ayse

        if request.engineering_update.module_state == \
                Request.DETACHED_MODULE and \
                MODULE not in y0._entity_names and \
                not hab.landed():
            # If the Habitat is freely floating and engineering asks us to
            # detach the Module, spawn in the Module.
            module = Entity(protos.Entity(
                name=MODULE, mass=100, r=10, artificial=True))
            module.pos = (hab.pos - (module.r + hab.r) *
                          calc.heading_vector(hab.heading))
            module.v = calc.rotational_speed(module, hab)

            y0_proto = y0.as_proto()
            y0_proto.entities.extend([module.proto])
            y0 = PhysicsState(None, y0_proto)

    elif request.ident == Request.UNDOCK:
        habitat = y0[HABITAT]

        if habitat.landed_on == AYSE:
            ayse = y0[AYSE]
            habitat.landed_on = ''

            norm = habitat.pos - ayse.pos
            unit_norm = norm / calc.fastnorm(norm)
            habitat.v += unit_norm * common.UNDOCK_PUSH
            habitat.spin = ayse.spin

            y0[HABITAT] = habitat

    elif request.ident == Request.REFERENCE_UPDATE:
        y0.reference = request.reference
    elif request.ident == Request.TARGET_UPDATE:
        y0.target = request.target
    elif request.ident == Request.LOAD_SAVEFILE:
        y0 = common.load_savefile(common.savefile(request.loadfile))
    elif request.ident == Request.NAVMODE_SET:
        y0.navmode = Navmode(request.navmode)
        if y0.navmode == Navmode['Manual']:
            y0.craft_entity().spin = 0
    elif request.ident == Request.PARACHUTE:
        y0.parachute_deployed = request.deploy_parachute
    elif request.ident == Request.IGNITE_SRBS:
        if round(y0.srb_time) == common.SRB_FULL:
            y0.srb_time = common.SRB_BURNTIME
    elif request.ident == Request.TOGGLE_COMPONENT:
        component = y0.engineering.components[request.component_to_toggle]
        component.connected = not component.connected
    elif request.ident == Request.TOGGLE_RADIATOR:
        radiator = y0.engineering.radiators[request.radiator_to_toggle]
        radiator.functioning = not radiator.functioning
    elif request.ident == Request.CONNECT_RADIATOR_TO_LOOP:
        radiator = y0.engineering.radiators[request.radiator_to_loop.rad]
        radiator.attached_to_coolant_loop = request.radiator_to_loop.loop
    elif request.ident == Request.TOGGLE_COMPONENT_COOLANT:
        component = \
            y0.engineering.components[request.component_to_loop.component]
        loop_n = request.component_to_loop.loop
        assert 0 <= loop_n <= 2

        if 0 == loop_n:
            component.coolant_hab_one = not component.coolant_hab_one
        elif 1 == loop_n:
            component.coolant_hab_two = not component.coolant_hab_two
        elif 2 == loop_n:
            component.coolant_ayse = not component.coolant_ayse

    return y0

# -*- coding: utf-8 -*-
"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, TypeVar

import numpy as np
import vpython

# Forward typing declaration is needed for ThreeDeeObj and subclasses
FlightGui = TypeVar('FlightGui')  # noqa: E402

from orbitx import common
from orbitx import calc
from orbitx import state
from orbitx.network import Request
from orbitx.graphics.threedeeobj import ThreeDeeObj
from orbitx.graphics.planet import Planet
from orbitx.graphics.habitat import Habitat
from orbitx.graphics.spacestation import SpaceStation
from orbitx.graphics.star import Star
from orbitx.graphics.sidebar_widgets import Text, Menu
from orbitx.graphics.orbit_projection import OrbitProjection

log = logging.getLogger()

G = 6.674e-11

DEFAULT_TRAILS = False


class FlightGui:  # type: ignore

    def __init__(
        self,
        draw_state: state.PhysicsState,
        texture_path: Path = None,
        no_intro: bool = False
    ) -> None:
        assert len(draw_state) >= 1

        self._state = draw_state
        # create a vpython canvas object
        self._scene: vpython.canvas = self._init_canvas()
        self._show_label: bool = True
        self._show_trails: bool = False
        self._pause: bool = False
        self._origin: state.Entity
        self.pause_label: vpython.label = None
        self.texture_path: Path = (
            Path('data', 'textures') if texture_path is None else texture_path
        )
        self._commands: list = []
        self.pause_label: vpython.label = vpython.label(
            text="Simulation Paused.", visible=False)

        self._3dobjs: Dict[str, ThreeDeeObj] = {}
        # remove vpython ambient lighting
        self._scene.lights = []  # This line shouldn't be removed
        self._wtexts: List[Text] = []

        self._scene.autoscale = False
        self._scene.range = 696000000.0 * 15000  # Sun radius * 15000

        self._set_origin(common.DEFAULT_CENTRE)

        for planet in draw_state:
            obj: ThreeDeeObj
            if planet.name == common.HABITAT:
                obj = Habitat(planet, self.origin(), self.texture_path)
            elif planet.name == common.AYSE:
                obj = SpaceStation(planet, self.origin(), self.texture_path)
            elif planet.name == common.SUN:
                obj = Star(planet, self.origin(), self.texture_path)
            else:
                obj = Planet(planet, self.origin(), self.texture_path)
            self._3dobjs[planet.name] = obj
            obj.make_trail(DEFAULT_TRAILS)

        self._orbit_projection = OrbitProjection(self)
        self._3dobjs[draw_state.reference].draw_landing_graphic(
            draw_state.reference_entity())
        self._3dobjs[draw_state.target].draw_landing_graphic(
            draw_state.target_entity())

        self._set_caption()

        # Add an animation when launching the program
        #   to describe the solar system and the current location
        if not no_intro:
            while self._scene.range > 600000:
                vpython.rate(100)
                self._scene.range = self._scene.range * 0.92
        self.recentre_camera(common.DEFAULT_CENTRE)
    # end of __init__

    def _init_canvas(self) -> vpython.canvas:
        """Set up our vpython canvas and other internal variables"""
        _scene = vpython.canvas(
            title='<title>OrbitX</title>',
            align='right',
            width=800,
            height=800,
            center=vpython.vector(0, 0, 0),
            up=vpython.vector(0.1, 0.1, 1),
            forward=vpython.vector(0, 0, -1),
            autoscale=True
        )
        _scene.autoscale = False
        _scene.bind('keydown', self._handle_keydown)
        # Show all planets in solar system
        _scene.range = 696000000.0 * 15000  # Sun radius * 15000
        return _scene

    def recentre_camera(self, planet_name: str) -> None:
        """Change camera to focus on different object

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of
        scene center being approximately 1e11 (planets position), origin
        entity should be reset every time when making a scene.center update.
        """
        try:
            self._scene.range = self._3dobjs[planet_name].relevant_range()
            self._scene.forward = vpython.vector(0, 0, -1)

            self._scene.camera.follow(self._3dobjs[planet_name]._obj)
            self._set_origin(planet_name)

        except KeyError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')
        except IndexError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')
    # end of recentre_camera

    def ungraceful_shutdown(self):
        """Lets the user know that something bad happened."""
        self._scene.caption += \
            "<style>.error { display: block !important; }</style>"
        print('called')
        time.sleep(0.1)  # Let vpython send out this update

    def shutdown(self):
        """Stops any threads vpython has started. Call on exit."""
        vpython.no_notebook.stop_server()

    def origin(self) -> state.Entity:
        if self._show_trails:
            return self._state.reference_entity()
        else:
            return self._origin

    def pop_commands(self) -> list:
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def handle_request(self, request: Request) -> None:
        """Called by the main loop, basically to update HRT and time acc."""
        if request not in [Request.TIME_ACC_SET,
                           Request.REFERENCE_UPDATE, Request.TARGET_UPDATE]:
            # These are the only ones we care about
            return

        if request.ident == Request.TIME_ACC_SET:
            new_acc_str = f'{int(request.time_acc_set):,}×'
            assert new_acc_str in self._time_acc_menu._menu._choices
            self._time_acc_menu._menu.selected = new_acc_str

        elif request.ident == Request.REFERENCE_UPDATE:
            assert request.reference in self._3dobjs.keys()
            self._reference_menu._menu.selected = request.reference
        elif request.ident == Request.TARGET_UPDATE:
            assert request.target in self._3dobjs.keys()
            self._target_menu._menu.selected = request.target

    def _handle_keydown(self, evt: vpython.event_return) -> None:
        """Called in a non-main thread by vpython when it gets key input."""

        k = evt.key
        if k == 'l':
            self._show_label = not self._show_label
            for name, obj in self._3dobjs.items():
                obj._show_hide_label()
        elif k == 'p':
            self._pause = not self._pause
        elif k == 'a':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=np.radians(10)))
        elif k == 'd':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=-np.radians(10)))
        elif k == 'w':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_CHANGE,
                throttle_change=0.01))
        elif k == 's':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_CHANGE,
                throttle_change=-0.01))
        elif k == 'W':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_CHANGE,
                throttle_change=0.001))
        elif k == 'S':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_CHANGE,
                throttle_change=-0.001))
        elif k == '\n':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_SET,
                throttle_set=1.00))
        elif k == 'backspace':
            self._commands.append(Request(
                ident=Request.HAB_THROTTLE_SET,
                throttle_set=0.00))
        elif k == '.':
            try:
                self._time_acc_menu._menu.index += 1
                self._time_acc_dropdown_hook(self._time_acc_menu._menu)
            except IndexError:
                pass  # We're already at max time acceleration
        elif k == ',':
            if self._time_acc_menu._menu.index != 0:
                self._time_acc_menu._menu.index -= 1
                self._time_acc_dropdown_hook(self._time_acc_menu._menu)
    # end of _handle_keydown

    def draw(self, draw_state: state.PhysicsState) -> None:
        self._state = draw_state

        new_acc_str = f'{int(draw_state.time_acc):,}×'
        if new_acc_str not in self._time_acc_menu._menu._choices:
            raise ValueError(f'"{new_acc_str}" not a valid time acceleration')
        if new_acc_str != self._time_acc_menu._menu.selected:
            self._time_acc_menu._menu.selected = new_acc_str

        # Have to reset origin, reference, and target with new positions
        self._origin = draw_state[self._origin.name]
        if self._pause:
            self._scene.pause("Simulation is paused. \n Press 'p' to continue")

        for planet in draw_state:
            self._3dobjs[planet.name].draw(planet, draw_state, self.origin())

        self._orbit_projection.update(draw_state, self.origin())

        for wtext in self._wtexts:
            wtext.update()

    def _set_reference(self, entity_name: str) -> None:
        try:
            self._commands.append(Request(
                ident=Request.REFERENCE_UPDATE, reference=entity_name))
            self._3dobjs[entity_name].draw_landing_graphic(
                self._state[entity_name])
            if self._show_trails:
                self._clear_trails()
        except IndexError:
            log.error(f'Tried to set non-existent reference "{entity_name}"')

    def _set_target(self, entity_name: str) -> None:
        try:
            self._commands.append(Request(
                ident=Request.TARGET_UPDATE, target=entity_name))
            self._3dobjs[entity_name].draw_landing_graphic(
                self._state[entity_name])
        except IndexError:
            log.error(f'Tried to set non-existent target "{entity_name}"')

    def _set_origin(self, entity_name: str) -> None:
        """Set origin position for rendering universe and reset the trails.

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of
        scene center being approximately 1e11 (planets position), origin
        entity should be reset every time when making a scene.center update.
        """
        if self._show_trails:
            # The user is expecting to see trails relative to the reference.
            # We don't usually have this behaviour because if the reference is
            # far enough from the camera centre, we get graphical glitches.
            entity_name = self._state.reference

        try:
            self._origin = self._state[entity_name]
        except IndexError:
            log.error(f'Tried to set non-existent origin "{entity_name}"')

    def _clear_trails(self) -> None:
        for name, obj in self._3dobjs.items():
            obj.clear_trail()

    def _recentre_dropdown_hook(self, centre_menu: vpython.menu) -> None:
        self._set_origin(centre_menu.selected)
        self.recentre_camera(centre_menu.selected)

    def _time_acc_dropdown_hook(self, time_acc_menu: vpython.menu) -> None:
        time_acc = int(
            time_acc_menu.selected.replace(',', '').replace('×', ''))
        self._commands.append(Request(
            ident=Request.TIME_ACC_SET,
            time_acc_set=time_acc))

    def _trail_checkbox_hook(self, selection: vpython.menu) -> None:
        self._show_trails = selection.checked
        for name, obj in self._3dobjs.items():
            obj.make_trail(selection.checked)

        if not self._show_trails:
            # Turning on trails set our camera origin to be the reference,
            # instead of the camera centre. Revert that when we turn off trails
            self._set_origin(self._centre_menu._menu.selected)

    def _orbits_checkbox_hook(self, selection: vpython.menu) -> None:
        self._orbit_projection.show(selection.checked)

    def rate(self, framerate: int) -> None:
        """Alias for vpython.rate(framerate). Basically sleeps 1/framerate"""
        vpython.rate(framerate)
    # end of rate

    def _set_caption(self) -> None:
        """Set and update the captions."""

        self._scene.caption += """<div class='error'>
        <p class='prose'>&#9888; Sorry, spacesimmer! OrbitX has crashed for
        some reason.</p>

        <p class='prose'>Any information that OrbitX has on the crash has been
        saved to <span class='code'>orbitx/debug.log</span>. If you want to get
        this problem fixed, send <span class='code'>orbitx/debug.log</span> to
        Patrick Melanson along with a description of what was happening in the
        program when it crashed.</p>

        <p>Again, thank you for using OrbitX!</p>
        </div>"""

        self._scene.caption += "<table>\n"
        self._wtexts.append(Text(
            self,
            "Orbit speed",
            lambda: common.format_num(calc.orb_speed(
                self._state.craft_entity(),
                self._state.reference_entity()), " m/s"),
            "Speed required for circular orbit at current altitude",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Periapsis",
            lambda: common.format_num(calc.periapsis(
                self._state.craft_entity(),
                self._state.reference_entity()), " m"),
            "Lowest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Apoapsis",
            lambda: common.format_num(calc.apoapsis(
                self._state.craft_entity(),
                self._state.reference_entity()), " m"),
            "Highest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(Text(
            self,
            # The H in HRT stands for Habitat, even though craft is more
            # general and covers AYSE, but HRT is the familiar triple name and
            # the Hawking III says trans rights.
            "HRT phase θ",
            lambda: common.format_num(calc.phase_angle(
                self._state.craft_entity(),
                self._state.reference_entity(),
                self._state.target_entity()), "°") or
            "Same ref and targ",
            "Angle between Habitat, Reference, and Target",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Throttle",
            lambda: "{:.1%}".format(self._state.craft_entity().throttle),
            "Percentage of habitat's maximum rated engines",
            new_section=True))

        self._wtexts.append(Text(
            self,
            "Engine Acceleration",
            lambda: common.format_num(calc.engine_acceleration(
                self._state.craft_entity()), " m/s/s"),
            "Acceleration due to craft's engine thrust",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Fuel ",
            lambda: common.format_num(self._state.craft_entity(
            ).fuel, " kg"), "Remaining fuel of habitat",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Ref altitude",
            lambda: common.format_num(calc.altitude(
                self._state.craft_entity(),
                self._state.reference_entity()), " m"),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(Text(
            self,
            "Ref speed",
            lambda: common.format_num(calc.speed(
                self._state.craft_entity(),
                self._state.reference_entity()), " m/s"),
            "Speed of habitat above reference surface",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Vertical speed",
            lambda: common.format_num(calc.v_speed(
                self._state.craft_entity(),
                self._state.reference_entity()), " m/s "),
            "Vertical speed of habitat towards/away reference surface",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Horizontal speed",
            lambda: common.format_num(calc.h_speed(
                self._state.craft_entity(),
                self._state.reference_entity()), " m/s "),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Pitch θ",
            lambda: common.format_num(calc.pitch(
                self._state.craft_entity(),
                self._state.reference_entity()), "°"),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Targ altitude",
            lambda: common.format_num(calc.altitude(
                self._state.craft_entity(),
                self._state.target_entity()), " m"),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(Text(
            self,
            "Targ speed",
            lambda: common.format_num(calc.speed(
                self._state.craft_entity(),
                self._state.target_entity()), " m/s"),
            "Speed of habitat above target surface",
            new_section=False))

        self._wtexts.append(Text(
            self,
            "Landing acc",
            lambda: common.format_num(calc.landing_acceleration(
                self._state.craft_entity(),
                self._state.target_entity()), " m/s/s") or
            "no vertical landing",
            "Constant engine acc to land during vertical descent to target",
            new_section=False))

        # TODO add pitch and stopping acceleration fields after symposium
        self._scene.caption += "</table>"

        self._set_menus()

        self._scene.append_to_caption("\n")
        vpython.checkbox(
            bind=self._trail_checkbox_hook,
            checked=DEFAULT_TRAILS, text='Trails')
        self._scene.append_to_caption(
            " <span class='helptext'>&nbspGraphically intensive</span>")
        self._scene.append_to_caption("\n")

        vpython.checkbox(
            bind=self._orbits_checkbox_hook,
            checked=False, text='Orbit Projection')
        self._scene.append_to_caption(
            " <span class='helptext'>Attempt a simple projection of the " +
            "spaceship around the reference</span>")
        self._scene.append_to_caption("\n")

        vpython.button(
            text="Undock", pos=self._scene.caption_anchor, bind=self._undock)
        self._scene.append_to_caption(
            f"<span class='helptext'>Undock from AYSE</span>\t")

        vpython.button(
            text=" Switch ", pos=self._scene.caption_anchor,
            disabled=True, bind=self._switch)
        self._scene.append_to_caption(
            f"<span class='helptext'>Switch constrol to AYSE/Habitat</span>")

        with open(Path('orbitx', 'graphics', 'footer.html')) as footer:
            self._scene.append_to_caption(footer.read())
    # end of _set_caption

    def _set_menus(self) -> None:
        """This creates dropped down menu which is used when set_caption."""

        self._centre_menu = Menu(
            self,
            choices=list(self._3dobjs),
            bind=self._recentre_dropdown_hook,
            selected=common.DEFAULT_CENTRE,
            caption="Centre",
            helptext="Focus of camera"
        )

        self._reference_menu = Menu(
            self,
            choices=list(self._3dobjs),
            bind=lambda selection: self._set_reference(selection.selected),
            # TODO: the reference is already set by default, just use that ref.
            selected=self._state.reference,
            caption="Reference",
            helptext=(
                "Take position, velocity relative to this")
        )

        self._target_menu = Menu(
            self,
            choices=list(self._3dobjs),
            bind=lambda selection: self._set_target(selection.selected),
            selected=self._state.target,
            caption="Target",
            helptext="Entity to land or dock with"
        )

        Menu(
            self,
            choices=['deprt ref'],
            bind=lambda selection: log.error(f"Unimplemented: {selection}"),
            selected='deprt ref',
            caption="NAV mode",
            helptext="Automatically points habitat"
        )._menu.disabled = True

        self._time_acc_menu = Menu(
            self,
            choices=[f'{n:,}×' for n in
                     [1, 5, 10, 50, 100, 1_000, 10_000, 100_000]],
            bind=self._time_acc_dropdown_hook,
            selected='1×',
            caption="Warp",
            helptext="Speed of simulation"
        )
    # end of _set_menus

    def _undock(self):
        self._commands.append(Request(ident=Request.UNDOCK))

    def _switch(self):
        print("switch")
# end of class FlightGui

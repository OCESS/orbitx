# -*- coding: utf-8 -*-
"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import collections
import logging
import signal
from pathlib import Path
from typing import List, Tuple

import numpy as np
import math

from . import common
from . import orbitx_pb2 as protos

import vpython

log = logging.getLogger()

DEFAULT_CENTRE = 'Habitat'
DEFAULT_REFERENCE = 'Earth'
DEFAULT_TARGET = 'Moon'

G = 6.674e-11

PLANET_SHININIESS = 0.3

Point = collections.namedtuple('Point', ['x', 'y', 'z'])


class FlightGui:

    def __init__(
            self,
            physical_state_to_draw: protos.PhysicalState,
            texture_path: str = None,
            no_intro: bool = False
    ) -> None:

        # Set up our vpython canvas and other internal variables
        self._scene = vpython.canvas(
            title='<b>OrbitX</b>',
            align='right',
            width=800,
            height=600,
            center=vpython.vector(0, 0, 0),
            up=vpython.vector(0, 0, 1),
            forward=vpython.vector(0.1, 0.1, -1),
            autoscale=True
        )

        self._show_label: bool = True
        self._show_trails: bool = False
        self._pause: bool = False
        self._scene.autoscale: bool = False
        self._pause_label: vpython.label = None
        self._texture_path: NoneType = texture_path
        self._commands: list = []
        self._spheres: dict = {}
        self._labels: dict = {}
        self._target_landing_graphic: vpython.compound = None
        self._reference_landing_graphic: vpython.compound = None

        self._pause_label = vpython.label(
            text="Simulation Paused.", visible=False)

        self._scene.bind('keydown', self._handle_keydown)
        self._scene.bind('click', self._handle_click)
        # Show all planets in solar system
        self._scene.range: float = 696000000.0 * 15000  # Sun radius * 15000

        if texture_path is None:
            # Look for orbitx/data/textures
            self._texture_path = Path('data', 'textures')

        assert len(physical_state_to_draw.entities) >= 1
        self._last_physical_state = physical_state_to_draw
        self._new_origin(DEFAULT_CENTRE)
        self._new_reference(DEFAULT_REFERENCE)
        self._new_target(DEFAULT_TARGET)

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            self._labels[planet.name] = self._draw_labels(planet)

        self._target_landing_graphic = self._draw_landing_graphic(self._target)
        self._reference_landing_graphic = self._draw_landing_graphic(
            self._reference)

        # self._scene.autoscale: bool = False
        self._set_caption()

        # Add an animation when launching the program
        #   to describe the solar system and the current location
        if not no_intro:
            while self._scene.range > 600000:
                vpython.rate(100)
                self._scene.range = self._scene.range * 0.98
        self.recentre_camera(DEFAULT_CENTRE)
    # end of __self__

    def shutdown(self) -> None:
        """Stops any threads vpython has started. Call on exit."""
        if not vpython._isnotebook and \
                vpython.__version__ == '7.4.7':
            # We're not running in a jupyter notebook environment. In
            # vpython 7.4.7, that means an HTTPServer and a WebSocketServer
            # are running, each in their own thread. From comments in
            # vpython.py at about line 370:
            # "The situation with non-notebook use is similar, but the http
            # server is threaded, in order to serve glowcomm.html, jpg texture
            # files, and font files, and the  websocket is also threaded."
            # This is fixed in the 2019 release of vpython, 7.5.0

            # Again, double underscore names will get name mangled unless we
            # bypass name mangling with getattr.
            getattr(vpython.no_notebook, '__server').shutdown()
            getattr(vpython.no_notebook, '__interact_loop').stop()
    # end of shutdown

    def _orb_speed(self, planet_name: str) -> float:
        """The orbital speed of an astronomical body or object.

        Equation referenced from https://en.wikipedia.org/wiki/Orbital_speed"""
        reference = common.find_entity(planet_name, self._last_physical_state)
        return vpython.sqrt((G * reference.mass) / reference.r)
    # end of _orb_speed

    def _periapsis(self, planet_name: str) -> float:
        reference = common.find_entity(planet_name, self._last_physical_state)
        habitat = common.find_entity(
            self._habitat.name, self._last_physical_state)
        # calculate and return the periapsis
        return 100
    # end of _periapsis

    def _apoapsis(self, planet_name: str) -> float:
        reference = common.find_entity(planet_name, self._last_physical_state)
        habitat = common.find_entity(
            self._habitat.name, self._last_physical_state)
        # calculate and return the apoapsis
        return 100
    # end of _apoapsis

    def _altitude(
        self,
        planet_name: str,
        planet_name2: str = 'Habitat'
    ) -> float:
        """Caculate distance between ref_planet and Habitat
        returns: the number of metres"""

        planet = common.find_entity(planet_name, self._last_physical_state)
        planet2 = common.find_entity(planet_name2, self._last_physical_state)
        return math.hypot(
            planet.x - planet2.x,
            planet.y - planet2.y
        ) - planet.r - planet2.r
    # end of _altitude

    def _speed(self, planet_name: str, planet_name2: str = 'Habitat') -> float:
        """Caculate speed between ref_planet and Habitat"""
        planet = common.find_entity(planet_name, self._last_physical_state)
        planet2 = common.find_entity(planet_name2, self._last_physical_state)
        return vpython.mag(vpython.vector(
            planet.vx - planet2.vx,
            planet.vy - planet2.vy,
            0
        ))
    # end of _speed

    def _v_speed(self, planet_name: str) -> float:
        """Centripetal velocity of the habitat relative to planet_name.

        Returns a negative number of m/s when the habitat is falling,
        and positive when the habitat is rising."""
        reference = common.find_entity(planet_name, self._last_physical_state)
        habitat = common.find_entity(
            self._habitat.name, self._last_physical_state)
        return 100
    # end of _v_speed

    def _h_speed(self, planet_name: str) -> float:
        """Tangential velocity of the habitat relative to planet_name.

        Always returns a positive number of m/s, of how fast the habitat is
        moving side-to-side relative to the reference surface."""
        reference = common.find_entity(planet_name, self._last_physical_state)
        habitat = common.find_entity(
            self._habitat.name, self._last_physical_state)
        return 100
    # end of _h_speed

    def _posn(self, entity: protos.Entity) -> vpython.vector:
        """Translates into the frame of reference of the origin."""

        return vpython.vector(
            entity.x - self._origin.x,
            entity.y - self._origin.y,
            0)
    # end of _posn

    def _unit_velocity(self, entity: protos.Entity) -> vpython.vector:
        """Provides entity velocity relative to reference."""
        return vpython.vector(
            entity.vx - self._reference.vx,
            entity.vy - self._reference.vy,
            0).norm()
    # end of _unit_velocity

    def _new_reference(self, entity_name: str) -> None:
        try:
            self._reference = common.find_entity(
                entity_name, self._last_physical_state)
        except IndexError:
            log.error(f'Tried to set non-existent reference "{entity_name}"')
    # end of _new_reference

    def _new_target(self, entity_name: str) -> None:
        try:
            self._target = common.find_entity(
                entity_name, self._last_physical_state)
        except IndexError:
            log.error(f'Tried to set non-existent target "{entity_name}"')
        # end of _new_target

    def _new_origin(self, entity_name: str) -> None:
        """Set origin position for rendering universe and reset the trails.

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of
        scene center being approximately 1e11 (planets position), origin
        entity should be reset every time when making a scene.center update.
        """
        if self._show_trails:
            # The user is expecting to see trails relative to the reference.
            # We don't usually have this behaviour because if the reference is
            # far enough from the camera centre, we get graphical glitches.
            entity_name = self._reference.name

        try:
            self._origin = common.find_entity(
                entity_name, self._last_physical_state)
        except IndexError:
            log.error(f'Tried to set non-existent origin "{entity_name}"')
        # end of _new_origin

    def _clear_trails(self) -> None:
        for sphere in self._spheres.values():
            if sphere.name == 'Habitat':
                self._habitat_trail.clear()
            else:
                sphere.clear_trail()
    # end of _clear_trails

    def _show_hide_label(self) -> None:
        if self._show_label:
            for key, label in self._labels.items():
                label.visible = True
        else:
            for key, label in self._labels.items():
                label.visible = False
    # end of _show_hide_label

    def pop_commands(self) -> list:
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands
    # end of pop_commands

    def _handle_keydown(self, evt: vpython.event_return) -> None:
        """Input key handler"""

        k = evt.key
        if k == 'l':
            self._show_label = not self._show_label
            self._show_hide_label()
        elif k == 'p':
            self._pause = not self._pause
        elif k == 'a':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_SPIN_CHANGE,
                arg=np.radians(10)))
        elif k == 'd':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_SPIN_CHANGE,
                arg=-np.radians(10)))
        elif k == 'w':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=0.01))
        elif k == 's':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=-0.01))
        elif k == 'W':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=0.001))
        elif k == 'S':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=-0.001))
        elif k == '\n':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_SET,
                arg=1.00))
        elif k == 'backspace':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_SET,
                arg=0.00))

        # elif (k == 'e'):
        #    self._scene.center = self._spheres['Earth'].pos
        #
        # elif (k == 's'):
        #    self._scene.center = self._spheres['Sun'].pos
        #
        # elif (k == 't'):
        #    self.cur_caption = (self.cur_caption + 1) % 4
        #    self.set_caption()

    # end of _handle_keydown

    def _handle_click(self, evt: vpython.event_return) -> None:
        # global obj, clicked
        try:
            obj = self._scene.mouse.pick
            if obj is not None:
                self.update_caption(obj)

        except AttributeError:
            pass
        # clicked = True

    # end of _handle_click

    # TODO: 1)Update with correct physics values
    def _set_caption(self) -> None:
        """Set and update the captions."""

        # There's a bit of magic here. Normally, vpython.wtext will make a
        # <div> in the HTML and automaticall update it when the .text field is
        # updated in this python code. But if you want to insert a wtext in the
        # middle of a field, the following first attempt won't work:
        #     scene.append_to_caption('<table>')
        #     vpython.wtext(text='widget text')
        #     scene.append_to_caption('</table>')
        # because adding the wtext will also close the <table> tag.
        # But you can't make a wtext that contains HTML DOM tags either,
        # because every time the text changes several times a second, any open
        # dropdown menus will be closed.
        # So we have to insert a <div> where vpython expects it, manually.
        # We take advantage of the fact that manually modifying scene.caption
        # will remove the <div> that represents a wtext. Then we add the <div>
        # back, along with the id="x" that identifies the div, used by vpython.
        #
        # TL;DR the div_id variable is a bit magic, if you make a new wtext
        # before this, increment div_id by one..
        self._scene.caption += "<table>\n"
        self._wtexts = []
        div_id = 1
        for caption, text_gen_func, helptext, new_section in [
            ("Orbit speed",
             lambda: f"{self._orb_speed(self._reference.name):,.7g} m/s",
             "Speed required for circular orbit at current altitude",
             False),
            ("Periapsis",
             lambda: f"{self._periapsis(self._reference.name):,.7g} m",
             "Lowest altitude in naïve orbit around reference",
             False),
            ("Apoapsis",
             lambda: f"{self._apoapsis(self._reference.name):,.7g} m",
             "Highest altitude in naïve orbit around reference",
             False),
            ("Ref alt",
             lambda: f"{self._altitude(self._reference.name):,.7g} m",
             "Altitude of habitat above reference surface",
             True),
            ("Ref speed",
             lambda: f"{self._speed(self._reference.name):,.7g} m/s",
             "Speed of habitat above reference surface",
             False),
            ("Vertical speed",
             lambda: f"{self._v_speed(self._reference.name):,.7g} m/s ",
             "Vertical speed of habitat towards/away reference surface",
             False),
            ("Horizontal speed",
             lambda: f"{self._h_speed(self._reference.name):,.7g} m/s ",
             "Horizontal speed of habitat across reference surface",
             False),
            ("Targ alt",
             lambda: f"{self._altitude(self._target.name):,.7g} m",
             "Altitude of habitat above reference surface",
             True),
            ("Targ speed",
             lambda: f"{self._speed(self._target.name):,.7g} m/s",
             "Altitude of habitat above reference surface",
             False),
            ("Throttle",
             lambda: f"{self._habitat.throttle:.1%}",
             "Percentage of habitat's maximum rated engines",
             True)
        ]:
            self._wtexts.append(vpython.wtext(text=text_gen_func()))
            self._wtexts[-1].text_func = text_gen_func
            self._scene.caption += f"""<tr>
                <td {"class='newsection'" if new_section else ""}>
                    {caption}
                </td>
                <td class="num{" newsection" if new_section else ""}">
                    <div id="{div_id}">{self._wtexts[-1].text}</div>
                </td>
                <td class="helptext{" newsection" if new_section else ""}">
                    {helptext}
                </td>
                </tr>\n"""
            div_id += 1
        self._scene.caption += "</table>"

        self._set_menus()
        self._scene.append_to_caption(HELP_CHECKBOX)
        self._scene.append_to_caption(" Help text")
        self._scene.append_to_caption(INPUT_CHEATSHEET)

        self._scene.append_to_caption(VPYTHON_CSS)
        self._scene.append_to_caption(VPYTHON_JS)
    # end of _set_caption

    # TODO: create bind functions for target, ref, and NAV MODE
    def _set_menus(self) -> None:
        """This creates dropped down menu which is used when set_caption."""

        def build_menu(
            *,
            choices: list = None,
            bind=None,
            selected: str = None,
            caption: str = None,
            helptext: str = None
        ) -> vpython.menu:

            menu = vpython.menu(
                choices=choices,
                pos=self._scene.caption_anchor,
                bind=bind,
                selected=selected)
            self._scene.append_to_caption(f"&nbsp;<b>{caption}</b>&nbsp;")
            self._scene.append_to_caption(
                f"<span class='helptext'>{helptext}</span>")
            self._scene.append_to_caption("\n")
            return menu
        # end of build_menu

        self._centre_menu = build_menu(
            choices=list(self._spheres),
            bind=self._recentre_dropdown_hook,
            selected=DEFAULT_CENTRE,
            caption="Centre",
            helptext="Focus of camera"
        )

        build_menu(
            choices=list(self._spheres),
            bind=lambda selection: self._new_reference(selection.selected),
            selected=DEFAULT_REFERENCE,
            caption="Reference",
            helptext=(
                "Take position, velocity relative to this.")
        )

        build_menu(
            choices=list(self._spheres),
            bind=lambda selection: self._new_target(selection.selected),
            selected=DEFAULT_TARGET,
            caption="Target",
            helptext="For use by NAV mode"
        )

        build_menu(
            choices=['deprt ref'],
            bind=lambda selection: self._set_navmode(selection.selected),
            selected='deprt ref',
            caption="NAV mode",
            helptext="Automatically points habitat"
        )

        self._time_acc_menu = build_menu(
            choices=[f'{n:,}×' for n in
                     [1, 5, 10, 50, 100, 1_000, 10_000, 100_000]],
            bind=self._time_acc_dropdown_hook,
            selected=1,
            caption="Warp",
            helptext="Speed of simulation"
        )

        self._scene.append_to_caption("\n")
        vpython.checkbox(
            bind=self._trail_checkbox_hook, checked=False, text='Trails')
        self._scene.append_to_caption(
            " <span class='helptext'>Graphically intensive</span>")
    # end of _set_menus

    def draw(self, physical_state_to_draw: protos.PhysicalState) -> None:
        self._last_physical_state = physical_state_to_draw
        # Have to reset origin, reference, and target with new positions
        self._origin = common.find_entity(
            self._origin.name, physical_state_to_draw)
        self._target = common.find_entity(
            self._target.name, physical_state_to_draw)
        self._reference = common.find_entity(
            self._reference.name, physical_state_to_draw)

        self._update_landing_graphic(
            self._reference, self._reference_landing_graphic)
        self._update_landing_graphic(
            self._target, self._target_landing_graphic)

        if self._pause:
            self._scene.pause("Simulation is paused. \n Press 'p' to continue")
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)
            if self._show_label:
                self._update_label(planet)

        for wtext in self._wtexts:
            # Update text of all text widgets.
            wtext.text = wtext.text_func()
    # end of draw

    def _draw_sphere(self, planet: protos.Entity) -> vpython.sphere:
        texture = self._texture_path / (planet.name + '.jpg')

        if planet.name == "Habitat":
            # TODO: 1) ARROW

            body = vpython.cylinder(
                pos=vpython.vector(0, 0, 0),
                axis=vpython.vector(-5, 0, 0),
                radius=7)
            head = vpython.cone(pos=vpython.vector(
                0, 0, 0), axis=vpython.vector(3, 0, 0), radius=7)
            wing = vpython.triangle(
                v0=vpython.vertex(pos=vpython.vector(0, 0, 0)),
                v1=vpython.vertex(pos=vpython.vector(-5, 30, 0)),
                v2=vpython.vertex(pos=vpython.vector(-5, -30, 0)))
            wing2 = vpython.triangle(
                v0=vpython.vertex(pos=vpython.vector(0, 0, 0)),
                v1=vpython.vertex(pos=vpython.vector(-5, 0, 30)),
                v2=vpython.vertex(pos=vpython.vector(-5, 0, -30)))

            obj = vpython.compound([body, head, wing, wing2])
            obj.texture = vpython.textures.metal
            obj.pos = self._posn(planet)
            obj.axis = self._ang_pos(planet.heading)
            obj.radius = planet.r / 2
            obj.shininess = 0.1
            obj.length = planet.r * 2

            obj.arrow = self._unit_velocity(planet)
            self._habitat = planet
            vpython.attach_arrow(obj, 'arrow')  # scale=planet.r * 1.5)
            self._habitat_trail = vpython.attach_trail(obj, retain=100)
            if not self._show_trails:
                self._habitat_trail.stop()
                self._habitat_trail.clear()

        else:
            # Note the radius is slightly too small. This is so that the sphere
            # doesn't intersect with the landing graphic.
            obj = vpython.sphere(
                pos=self._posn(planet),
                axis=self._ang_pos(planet.heading),
                up=vpython.vector(0, 0, 1),
                radius=planet.r * 0.95,
                make_trail=self._show_trails,
                retain=10000,
                shininess=PLANET_SHININIESS
            )

        obj.name = planet.name  # For convenient accessing later

        if planet.name == 'Sun':  # The sun is special!
            obj.emissive = True  # The sun glows!
            self._scene.lights = []
            self._lights = [vpython.local_light(pos=obj.pos)]

        if texture.is_file():
            obj.texture = str(texture)
        else:
            log.debug(f'Could not find texture {texture}')
        return obj
    # end of _draw_sphere

    def _draw_labels(self, planet: protos.Entity) -> vpython.label:
        label = vpython.label(
            visible=True, pos=self._posn(planet),
            xoffset=0, yoffset=10, height=16,
            border=4, font='sans')

        label.text_function = lambda entity: entity.name
        if planet.name == 'Habitat':
            label.text_function = lambda entity: (
                f'{entity.name}\n'
                f'Fuel: {abs(round(entity.fuel, 1))} kg\n'
                f'Heading: {round(np.degrees(entity.heading))}\xb0'
            )
        label.text = label.text_function(planet)
        return label
    # end of _draw_labels

    def _draw_landing_graphic(self, entity: protos.Entity) -> vpython.compound:
        """Draw something that simulates a flat surface at near zoom levels.

        Only draws the landing graphic on the target and reference."""
        # Iterate over a list of Point 3-tuples, each representing the
        # vertices of a triangle in the sphere segment.
        vpython_tris = []
        for tri in _build_sphere_segment_vertices(entity.r):
            vpython_verts = [vpython.vertex(pos=vpython.vector(*coord))
                             for coord in tri]
            vpython_tris.append(vpython.triangle(vs=vpython_verts))
        return vpython.compound(
            vpython_tris, pos=self._posn(entity), up=vpython.vector(0, 0, 1))
    # end of _draw_landing_graphic

    def _update_sphere(self, planet: protos.Entity) -> None:
        sphere = self._spheres[planet.name]
        sphere.pos = self._posn(planet)
        sphere.axis = self._ang_pos(planet.heading)
        if planet.name == 'Habitat':
            sphere.arrow = self._unit_velocity(planet)
            self._habitat = planet
    # end of _update_sphere

    def _update_label(self, planet: protos.Entity) -> None:
        label = self._labels[planet.name]
        label.text = label.text_function(planet)
        label.pos = self._posn(planet)
    # end of _update_label

    def _update_landing_graphic(self,
                                entity: protos.Entity,
                                landing_graphic: vpython.compound) -> None:
        """Rotate the landing graphic to always be facing the Habitat.

        The landing graphic has to be on the surface of the planet,
        but also the part of the planet closest to the habitat."""
        axis = vpython.vector(
            self._habitat.x - entity.x,
            self._habitat.y - entity.y,
            0
        ).norm()

        landing_graphic.axis = vpython.vector(axis.y, -axis.x, 0)
        landing_graphic.pos = (
            self._posn(entity) + axis * (entity.r - landing_graphic.width / 2)
        )
    # end of _update_landing_graphic

    def _recentre_dropdown_hook(self, selection: vpython.menu) -> None:
        self._new_origin(selection.selected)
        self.recentre_camera(selection.selected)
        self._clear_trails()
    # end of _recentre_dropdown_hook

    def _time_acc_dropdown_hook(self, selection: vpython.menu) -> None:
        time_acc = int(selection.selected.replace(',', '').replace('×', ''))
        self._commands.append(protos.Command(
            ident=protos.Command.TIME_ACC_SET,
            arg=time_acc))
    # end of _time_acc_dropdown_hook

    def _trail_checkbox_hook(self, selection: vpython.menu) -> None:
        self._show_trails = selection.checked
        for sphere in self._spheres.values():
            if sphere.name == 'Habitat':
                if selection.checked:
                    self._habitat_trail.start()
                else:
                    self._habitat_trail.stop()
                    self._habitat_trail.clear()
            else:
                sphere.make_trail = selection.checked
                if not selection.checked:
                    sphere.clear_trail()

        if not self._show_trails:
            # Turning on trails set our camera origin to be the reference,
            # instead of the camera centre. Revert that when we turn off trails
            self._new_origin(self._centre_menu.selected)
    # end of _trail_checkbox_hook

    def notify_time_acc_change(self, new_acc: int) -> None:
        new_acc_str = f'{new_acc:,}×'
        if new_acc_str == self._time_acc_menu.selected:
            return
        if new_acc_str not in self._time_acc_menu._choices:
            log.error(f'"{new_acc_str}" not a valid time acceleration')
            return
        self._time_acc_menu.selected = new_acc_str
    # end of notify_time_acc_change

    def recentre_camera(self, planet_name: str) -> None:
        """Change camera to focus on different object

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of
        scene center being approximately 1e11 (planets position), origin
        entity should be reset every time when making a scene.center update.
        """
        try:
            if planet_name == "Sun":
                self._scene.range = self._spheres["Sun"].radius * 15000
            else:
                self._scene.range = self._spheres[planet_name].radius * 2

            self._scene.camera.follow(self._spheres[planet_name])
            self._new_origin(planet_name)

        except KeyError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')
        except IndexError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')
    # end of recentre_camera

    def _ang_pos(self, angle: float) -> vpython.vector:
        return vpython.vector(np.cos(angle), np.sin(angle), 0)
    # end of _ang_pos

    def rate(self, framerate: int) -> None:
        """Alias for vpython.rate(framerate). Basically sleeps 1/framerate"""
        vpython.rate(framerate)
    # end of rate


VPYTHON_CSS = """<style>
table {
    margin-top: 1em;
    margin-bottom: 1em;
}
th {
    text-align: left;
}
.newsection {
    padding-top: 1em;
}
.num {
    font-family: monospace;
    font-weight: bold;
}
select {
    width: 100px;
}
input {
    width: 100px !important;
    height: unset !important;
}
.helptext {
    font-size: 75%;
}
</style>
<style title="disable_helptext">
.helptext {
    display: none;
}
</style>"""

VPYTHON_JS = """<script>
function show_hide_help() {
    // If helptext is enabled, we have to "disable disabling it."
    styleSheets = document.styleSheets;
    for (i = 0; i < styleSheets.length; ++i) {
        console.log(styleSheets[i].title)
        if (styleSheets[i].title == "disable_helptext") {
            styleSheets[i].disabled =
                document.getElementById("helptext_checkbox").checked
        }
    }
}

// Keep inputs deselected, so that keyboard input doesn't interfere with them.
for (var inp of document.querySelectorAll("input,select")) {
    inp.onchange = function(){this.blur()};
}
</script>"""

HELP_CHECKBOX = """
<input type="checkbox" id="helptext_checkbox" onClick="show_hide_help()">"""

# TODO: there's room for automating tables here.
INPUT_CHEATSHEET = """
<table class="helptext">
    <caption>Input Cheatsheet</caption>
    <tr>
        <th>Input</th>
        <th>Action</th>
    </tr>
    <tr>
        <td>Scroll, or ALT/OPTION-drag</td>
        <td>Zoom View</td>
    </tr>
    <tr>
        <td>Ctrl-Click</td>
        <td>Rotate View</td>
    </tr>
    <tr>
        <td>W/S</td>
        <td>Throttle Up/Down (press shift for fine control)</td>
    </tr>
    <tr>
        <td>Enter</td>
        <td>Set engines to 100%</td>
    </tr>
    <tr>
        <td>Backspace</td>
        <td>Set engines to 0%</td>
    </tr>
    <tr>
        <td>A/D</td>
        <td>Rotate Habitat</td>
    </tr>
    <tr>
        <td>L</td>
        <td>Toggle labels</td>
    </tr>
    <!-- re-enable this when we've fixed pausing
    <tr>
        <td>P</td>
        <td>Pause simulation</td>
    </tr>-->
</table>
"""


def _build_sphere_segment_vertices(
        radius: float,
        refine_steps=1,
        size=5000) -> List[Tuple[Point, Point, Point]]:
    """Returns a segment of a sphere, which has a specified radius.
    The return is a list of xyz-tuples, each representing a vertex."""
    # This code inspired by:
    # http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html
    # Thanks, Andreas Kahler.
    # TODO: limit the number of vertices generated to 65536 (the max in a
    # vpython compound object).

    # We set the 'middle' of the surface we're constructing to be (0, 0, r).
    # Think of this as a point on the surface of the sphere centred on (0,0,0)
    # with radius r.
    # Then, we construct four equilateral triangles that will all meet at
    # this point. Each triangle is `size` metres long.

    # The values of 100 are placeholders, and get replaced by cos(theta) * r
    tris = np.array([
        (Point(0, 1, 100), Point(1, 0, 100), Point(0, 0, 100)),
        (Point(1, 0, 100), Point(0, -1, 100), Point(0, 0, 100)),
        (Point(0, -1, 100), Point(-1, 0, 100), Point(0, 0, 100)),
        (Point(-1, 0, 100), Point(0, 1, 100), Point(0, 0, 100))
    ])
    # Each Point gets coerced to a length-3 numpy array

    # Set the z of each xyz-tuple to be radius, and everything else to be
    # the coordinates on the radius-sphere times -1, 0, or 1.
    theta = np.arctan(size / radius)
    tris = np.where(
        [True, True, False],
        radius * np.sin(theta) * tris,
        radius * np.cos(theta))

    def midpoint(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        # Find the midpoint between the xyz-tuples left and right, but also
        # on the surface of a sphere (so not just a simple average).
        midpoint = (left + right) / 2
        midpoint_radial_dist = np.linalg.norm(midpoint)
        return radius * midpoint / midpoint_radial_dist

    for _ in range(0, refine_steps):
        new_tris = np.ndarray(shape=(0, 3, 3))
        for tri in tris:
            # A tri is a 3-tuple of xyz-tuples.
            a = midpoint(tri[0], tri[1])
            b = midpoint(tri[1], tri[2])
            c = midpoint(tri[2], tri[0])

            # Turn one triangle into a triforce projected onto a sphere.
            new_tris = np.append(new_tris, [
                (tri[0], a, c),
                (tri[1], b, a),
                (tri[2], c, b),
                (a, b, c)  # The centre triangle of the triforce
            ], axis=0)
        tris = new_tris

    return tris

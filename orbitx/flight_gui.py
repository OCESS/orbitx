# -*- coding: utf-8 -*-
"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import logging
import signal
from pathlib import Path

import numpy as np

from . import common
from . import orbitx_pb2 as protos

log = logging.getLogger()

DEFAULT_CENTRE = 'Habitat'
DEFAULT_REFERENCE = 'Earth'
G = 6.674e-11


class FlightGui:

    def __init__(self, physical_state_to_draw, texture_path=None):
        ctrl_c_handler = signal.getsignal(signal.SIGINT)
        # Note that this might actually start an HTTP server!
        import vpython
        self._vpython = vpython

        # vpython installs "os._exit(0)" signal handlers. Very not good for us.
        # Reset the signal handler to default behaviour.
        signal.signal(signal.SIGINT, ctrl_c_handler)

        # os._exit(0) is in one other place, let's take that out too.
        # Unfortunately, now that vpython isn't calling os._exit, we have to
        # notify someone when the GUI closed.
        # Note to access vpython double underscore variables, we have to
        # bypass normal name mangling by using getattr.
        def callback(*_):
            getattr(self._vpython.no_notebook, '__interact_loop').stop()
            self.closed = True
        self.closed = False
        getattr(self._vpython.no_notebook, '__factory').protocol.onClose = \
            callback

        # Set up our vpython canvas and other internal variables
        self._scene = vpython.canvas(
            title='<b>OrbitX\n</b>',
            align='right',
            width=1000,
            height=600,
            center=vpython.vector(0, 0, 0),
            autoscale=True,
            caption="\n"
        )

        self._commands = []

        self._show_label = True
        self._pause = False
        self.pause_label = vpython.label(
            text="Simulation Paused.", visible=False)

        self._scene.bind('keydown', self._handle_keydown)
        self._scene.bind('click', self._handle_click)

        self._spheres = {}
        self._labels = {}

        self._texture_path = texture_path
        if texture_path is None:
            # If we're in src/ look for src/../textures/
            self._texture_path = Path('data', 'textures')
        # stars = str(self._texture_path / 'Stars.jpg')
        # vpython.sphere(radius=9999999999999, texture=stars)

        assert len(physical_state_to_draw.entities) >= 1
        self._last_physical_state = physical_state_to_draw
        self._origin = physical_state_to_draw.entities[0]
        self._set_origin(DEFAULT_REFERENCE)

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            self._labels[planet.name] = self._draw_labels(planet)
            if planet.name == DEFAULT_CENTRE:
                self.recentre_camera(DEFAULT_CENTRE)
            if planet.name == DEFAULT_REFERENCE:
                self._hab_ref = self._calc_distance(DEFAULT_REFERENCE)
                self._orbital_speed = self._calc_orb_speed(planet)
        self._scene.autoscale = False
        self._set_caption()

    def shutdown(self):
        """Stops any threads vpython has started. Call on exit."""
        if not self._vpython._isnotebook:
            # We're not running in a jupyter notebook environment. As of
            # vpython 7.4.7, that means an HTTPServer and a WebSocketServer
            # are running, each in their own thread. From comments in
            # vpython.py at about line 370:
            # "The situation with non-notebook use is similar, but the http
            # server is threaded, in order to serve glowcomm.html, jpg texture
            # files, and font files, and the  websocket is also threaded."

            # Again, double underscore names will get name mangled unless we
            # bypass name mangling with getattr.
            getattr(self._vpython.no_notebook, '__server').shutdown()
            getattr(self._vpython.no_notebook, '__interact_loop').stop()

    def _calc_orb_speed(self, ref_entity):
        """The orbital speed of an astronomical body or object.

        Equation referenced from https://en.wikipedia.org/wiki/Orbital_speed"""
        return self._vpython.sqrt((G * ref_entity.mass) / ref_entity.r)

    def _calc_distance(self, planet_name, planet_name2='Habitat'):
        """Caculate distance between ref_planet and Habitat"""

        planet = self._spheres[planet_name]
        planet2 = self._spheres[planet_name2]
        x = planet.pos.x - planet2.pos.x
        y = planet.pos.y - planet2.pos.y
        z = np.math.sqrt(((x * x) + (y * y)))
        return z

    def _posn(self, entity):
        """Provides the vector of the entity position with regard to the origin planet position."""
        return self._vpython.vector(
            entity.x - self._origin.x,
            entity.y - self._origin.y,
            0)

    def _unit_velocity(self, entity):
        """Provides entity velocity relative to origin."""
        return self._vpython.vector(
            entity.vx - self._origin.vx,
            entity.vy - self._origin.vy,
            0).norm()

    def _set_origin(self, entity_name):
        """Set origin position for rendering universe and reset the trails.

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of scene center
        being approximately 1e11 (planets position), origin entity should be reset every time
        when making a scene.center update.
        """
        try:
            self._origin = common.find_entity(
                entity_name, self._last_physical_state)
        except IndexError:
            log.error(f'Tried to set non-existent origin "{entity_name}"')

    def _clear_trails(self):
        for sphere in self._spheres.values():
            sphere.clear_trail()

    def _show_hide_label(self):
        if self._show_label:
            for key, label in self._labels.items():
                label.visible = True
        else:
            for key, label in self._labels.items():
                label.visible = False

    def pop_commands(self):
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def _handle_keydown(self, evt):
        """Input key handler"""

        k = evt.key
        if k == 'l':
            self._show_label = not self._show_label
            self._show_hide_label()
        elif k == 'p':
            self._pause = not self._pause
        elif k == 'q':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_SPIN_CHANGE,
                arg=np.radians(10)))
        elif k == 'e':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_SPIN_CHANGE,
                arg=-np.radians(10)))
        elif k == 'w':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=1))
        elif k == 's':
            self._commands.append(protos.Command(
                ident=protos.Command.HAB_THROTTLE_CHANGE,
                arg=-1))

        # elif (k == 'e'):
        #    self._scene.center = self._spheres['Earth'].pos
        #
        # elif (k == 's'):
        #    self._scene.center = self._spheres['Sun'].pos
        #
        # elif (k == 't'):
        #    self.cur_caption = (self.cur_caption + 1) % 4
        #    self.set_caption()

    def _handle_click(self, evt):
        # global obj, clicked
        try:
            obj = self._scene.mouse.pick
            if obj is not None:
                self.update_caption(obj)

        except AttributeError:
            pass
        # clicked = True

    # TODO: 1)Update with correct physics values
    def _set_caption(self):
        """Set and update the captions."""
        self._scene.caption = "\n"
        self._scene.append_to_caption(VPYTHON_CSS)
        self._scene.append_to_caption("<b>ref Vo: </b>")
        self._rv = self._vpython.wtext(
            text='{0:.2f}\n'.format(self._orbital_speed))
        self._scene.append_to_caption("<b>Ref distance: </b>")
        self._hr = self._vpython.wtext(text='{0:.2f}\n'.format(self._hab_ref))
        self._scene.append_to_caption("<b>Targ distance: </b>")
        self._tr = self._vpython.wtext(text='{0:.2f}\n'.format(self._hab_ref))
        self._scene.append_to_caption("<b>Throttle: </b>")
        self._thr = self._vpython.wtext(
            text='{0:.2f}\n'.format(self._habitat.throttle))
        self._scene.append_to_caption("\n")
        #self._scene.append_to_caption("Acc: XXX" + "\n")
        #self._scene.append_to_caption("Vcen: XXX" + "\n")
        #self._scene.append_to_caption("Vtan: XXX" + "\n")
        # self._scene.append_to_caption("\n")
        self._set_menus()
        self._scene.append_to_caption(INPUT_CHEATSHEET)

    # TODO: create bind functions for target, ref, and NAV MODE
    def _set_menus(self):
        """This creates dropped down menu which is used when set_caption."""
        self._scene.append_to_caption(
            "<b>Center: </b>")
        center = self._vpython.menu(
            choices=list(self._spheres),
            pos=self._scene.caption_anchor,
            bind=self._recentre_dropdown_hook,
            selected=DEFAULT_CENTRE
        )
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Target: </b>")
        target = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'AYSE'],
            pos=self._scene.caption_anchor, bind=self._recentre_dropdown_hook, selected='AYSE')
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Ref:      </b>")
        ref = self._vpython.menu(
            choices=list(self._spheres),
            pos=self._scene.caption_anchor,
            bind=self._reference_dropdown_hook,
            selected=DEFAULT_REFERENCE
        )
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption("<b>Nav:     </b>")
        NAVmode = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'deprt ref'],
            pos=self._scene.caption_anchor, bind=self._recentre_dropdown_hook, selected='deprt ref')
        self._scene.append_to_caption("\n")

        self._scene.append_to_caption("<b>Warp:  </b>")
        time_acc = self._vpython.menu(
            choices=[f'{n:,}×' for n in
                     [1, 5, 10, 50, 100, 1_000, 10_000, 100_000]],
            pos=self._scene.caption_anchor, bind=self._time_acc_dropdown_hook)
        self._scene.append_to_caption("\n")

    def draw(self, physical_state_to_draw):
        self._last_physical_state = physical_state_to_draw
        # Have to reset origin every update
        self._set_origin(self._origin.name)
        if self._pause:
            self._scene.pause("Simulation is paused. \n Press 'p' to continue")
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)
            if self._show_label:
                self._update_label(planet)
            if self._origin.name == planet.name:  # Caption Updates
                self._hab_ref = self._calc_distance(self._origin.name)
                self._hr.text = '{0:.2f}\n'.format(self._hab_ref)
                self._orbital_speed = self._calc_orb_speed(planet)
                self._rv.text = '{0:.2f}\n'.format(self._orbital_speed)

        self._thr.text = '{0:.2f}\n'.format(self._habitat.throttle)

    def _draw_labels(self, planet):
        label = self._vpython.label(
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

    def _draw_sphere(self, planet):
        texture = self._texture_path / (planet.name + '.jpg')

        if planet.name == "Habitat":
            # Todo: habitat object should be seperately defined from planets
            obj = self._vpython.cone(
                pos=self._posn(planet),
                axis=self._ang_pos(planet.heading),
                radius=planet.r / 2,
                make_trail=True,
                shininess=0.1
            )
            obj.length = planet.r
            obj.arrow = self._unit_velocity(planet)
            self._habitat = planet
            self._vpython.attach_arrow(obj, 'arrow', scale=planet.r * 1.5)
        else:
            obj = self._vpython.sphere(
                pos=self._posn(planet),
                axis=self._ang_pos(planet.heading),
                up=self._vpython.vector(0, 0, 1),
                radius=planet.r,
                make_trail=True,
                shininess=0.1
            )

        if planet.name == 'Sun':  # The sun is special!
            obj.emissive = True  # The sun glows!
            self._scene.lights = []
            self._lights = [self._vpython.local_light(pos=obj.pos)]

        if texture.is_file():
            obj.texture = str(texture)
        else:
            log.debug(f'Could not find texture {texture}')

        obj.name = planet.name  # For convenient accessing later

        return obj

    def _update_sphere(self, planet):
        sphere = self._spheres[planet.name]
        sphere.pos = self._posn(planet)
        sphere.axis = self._ang_pos(planet.heading)
        if planet.name == 'Habitat':
            sphere.length = planet.r
            sphere.arrow = self._unit_velocity(planet)
            self._habitat = planet

    def _update_label(self, planet):
        label = self._labels[planet.name]
        label.text = label.text_function(planet)
        label.pos = self._posn(planet)

    def _recentre_dropdown_hook(self, selection):
        self.recentre_camera(selection.selected)

    def _reference_dropdown_hook(self, selection):
        self._set_origin(selection.selected)
        self._clear_trails()

    def _time_acc_dropdown_hook(self, selection):
        time_acc = int(selection.selected.replace(',', '').replace('×', ''))
        self._commands.append(protos.Command(
            ident=protos.Command.TIME_ACC_CHANGE,
            arg=time_acc))

    def recentre_camera(self, planet_name):
        """Change camera to focus on different object"""
        try:
            if planet_name == "Sun":
                self._scene.range = self._spheres["Sun"].radius * 15000
            else:
                self._scene.range = self._spheres[planet_name].radius * 10

            self._scene.camera.follow(self._spheres[planet_name])

        except KeyError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')

    def _ang_pos(self, angle):
        return self._vpython.vector(np.cos(angle), np.sin(angle), 0)

    def rate(self, framerate):
        """Alias for vpython.rate(framerate). Basically sleeps 1/framerate"""
        self._vpython.rate(framerate)


VPYTHON_CSS = """
<style>
table {
    width: 250px;
}
th {
    text-align: left;
}
</style>
"""

# TODO: there's room for automating tables here.
INPUT_CHEATSHEET = """
<table>
    <caption>Input Cheatsheet</caption>
    <tr>
        <th>Input</th>
        <th>Action</th>
    </tr>
    <tr>
        <td>Scroll</td>
        <td>Zoom View</td>
    </tr>
    <tr>
        <td>Ctrl-Click</td>
        <td>Rotate View</td>
    </tr>
    <tr>
        <td>W/S</td>
        <td>Throttle Up/Down</td>
    </tr>
    <tr>
        <td>Q/E</td>
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

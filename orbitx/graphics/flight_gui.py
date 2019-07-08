# -*- coding: utf-8 -*-
"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import google
import numpy as np
import vpython

from orbitx import common
from orbitx import calc
from orbitx import state
from orbitx.network import Request
from orbitx.graphics.threedeeobj import ThreeDeeObj
from orbitx.graphics.planet import Planet
from orbitx.graphics.habitat import Habitat
from orbitx.graphics.science_mod import ScienceModule
from orbitx.graphics.spacestation import SpaceStation
from orbitx.graphics.star import Star
from orbitx.graphics.sidebar_widgets import Button, Checkbox, Menu, Text
from orbitx.graphics.orbit_projection import OrbitProjection

log = logging.getLogger()

DEFAULT_TRAILS = False

class MiscCommand(Enum):
    UNSELECTED = 'Command'
    UNDOCK = 'Undock'
    IGNITE_SRBS = 'Ignite SRBs'
    DEPLOY_PARACHUTE = 'Deploy Parachute'


class FlightGui:

    def __init__(
        self,
        draw_state: state.PhysicsState,
        *,
        running_as_mirror: bool
    ) -> None:
        assert len(draw_state) >= 1

        self._state = draw_state
        # create a vpython canvas, onto which all 3D and HTML drawing happens.
        self._scene = self._init_canvas(running_as_mirror)

        self._show_label: bool = True
        self._show_trails: bool = DEFAULT_TRAILS
        self._pause: bool = False
        self._origin: state.Entity
        self.texture_path: Path = Path('data', 'textures')
        self._commands: List[Request] = []
        self._pause_label = vpython.label(
            text="Simulation paused; saving and loading enabled.\n"
                 "When finished, unpause by clicking the 'Pause' checkbox.",
            xoffset=0, yoffset=200, line=False, height=25, border=20,
            opacity=1, visible=False)

        self._3dobjs: Dict[str, ThreeDeeObj] = {}
        # remove vpython ambient lighting
        self._scene.lights = []  # This line shouldn't be removed
        self._wtexts: List[Text] = []

        self._set_origin(common.DEFAULT_CENTRE)

        for entity in draw_state:
            self._3dobjs[entity.name] = self._build_threedeeobj(entity)

        self._orbit_projection = OrbitProjection()
        self._3dobjs[draw_state.reference].draw_landing_graphic(
            draw_state.reference_entity())
        self._3dobjs[draw_state.target].draw_landing_graphic(
            draw_state.target_entity())

        self._sidebar = Sidebar(self, running_as_mirror)
        self._scene.bind('keydown', self._handle_keydown)

        # Add an animation when launching the program to describe the solar
        # system and the current location
        while self._scene.range > 600000:
            vpython.rate(100)
            self._scene.range = self._scene.range * 0.92
        self.recentre_camera(common.DEFAULT_CENTRE)
    # end of __init__

    def _init_canvas(self, running_as_mirror) -> vpython.canvas:
        """Set up our vpython canvas and other internal variables"""
        _scene = vpython.canvas(
            title='<title>OrbitX ' +
                  ("Mirror" if running_as_mirror else "Lead") +
                  '</title>',
            align='right',
            width=900,
            height=750,
            center=vpython.vector(0, 0, 0),
            up=common.DEFAULT_UP,
            forward=common.DEFAULT_FORWARD,
            autoscale=True
        )
        _scene.autoscale = False
        # Show all planets in solar system
        _scene.range = 696000000.0 * 15000  # Sun radius * 15000
        return _scene

    def _build_threedeeobj(self, entity: state.Entity) -> ThreeDeeObj:
        obj: ThreeDeeObj
        if entity.name == common.HABITAT:
            obj = Habitat(entity, self.origin(), self.texture_path)
        elif entity.name == common.AYSE:
            obj = SpaceStation(entity, self.origin(), self.texture_path)
        elif entity.name == common.SUN:
            obj = Star(entity, self.origin(), self.texture_path)
        elif entity.name == common.MODULE:
            obj = ScienceModule(entity, self.origin(), self.texture_path)
        else:
            obj = Planet(entity, self.origin(), self.texture_path)
        obj.make_trail(self._show_trails)
        return obj

    def recentre_camera(self, planet_name: str) -> None:
        """Change camera to focus on different object

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of
        scene center being approximately 1e11 (planets position), origin
        entity should be reset every time when making a scene.center update.
        """
        try:
            self._scene.range = self._3dobjs[planet_name].relevant_range()
            self._scene.forward = common.DEFAULT_FORWARD
            self._scene.up = common.DEFAULT_UP

            self._scene.camera.follow(self._3dobjs[planet_name]._obj)
            self._set_origin(planet_name)

        except KeyError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')
        except IndexError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')

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

    def _handle_keydown(self, evt: vpython.event_return) -> None:
        """Called in a non-main thread by vpython when it gets key input."""
        if self._pause:
            # The user could be entering in things in the text fields, so just
            # wait until they're not paused.
            return
        if self.lead_server_communication_requested():
            # We shouldn't be generating any commands, ignore this.
            return

        k = evt.key
        if k == 'l':
            self._show_label = not self._show_label
            for name, obj in self._3dobjs.items():
                obj._show_hide_label()
        elif k == 'p':
            self.set_pause(True)
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
                self._sidebar.time_acc_menu._menu.index += 1
                self._time_acc_dropdown_hook(self._sidebar.time_acc_menu._menu)
            except IndexError:
                pass  # We're already at max time acceleration
        elif k == ',':
            if self._sidebar.time_acc_menu._menu.index != 0:
                self._sidebar.time_acc_menu._menu.index -= 1
                self._time_acc_dropdown_hook(self._sidebar.time_acc_menu._menu)
    # end of _handle_keydown

    def draw(self, draw_state: state.PhysicsState) -> None:
        self._state = draw_state

        new_acc_str = f'{int(draw_state.time_acc):,}×'
        if draw_state.time_acc == 0:
            pass
        elif new_acc_str not in self._sidebar.time_acc_menu._menu._choices:
            raise ValueError(f'"{new_acc_str}" not a valid time acceleration')
        else:
            self._sidebar.time_acc_menu._menu.selected = new_acc_str

        # Have to reset origin, reference, and target with new positions
        self._origin = draw_state[self._origin.name]

        try:
            for entity in draw_state:
                self._3dobjs[entity.name].draw(
                    entity, draw_state, self.origin())
        except KeyError as e:
            # If we find an entity that doesn't have an associated 3dobj, try
            # once to make a corresponding 3dobj. Note, if we get another
            # KeyError in this block, we won't catch the new KeyError.
            missing_entity = draw_state[e.args[0]]
            self._3dobjs[missing_entity.name] = \
                self._build_threedeeobj(missing_entity)
            for entity in draw_state:
                self._3dobjs[entity.name].draw(
                    entity, draw_state, self.origin())

        self._orbit_projection.update(draw_state, self.origin())

        self._sidebar.update(draw_state)

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

    def _recentre_dropdown_hook(self, centre_menu: vpython.menu):
        if centre_menu.selected not in self._3dobjs:
            # The requested entity doesn't exist yet.
            centre_menu.selected = self._origin.name
            return

        self._set_origin(centre_menu.selected)
        self.recentre_camera(centre_menu.selected)

    def _reference_dropdown_hook(self, reference_menu: vpython.menu):
        if reference_menu.selected not in self._3dobjs:
            # The requested entity doesn't exist yet.
            reference_menu.selected = self._origin.name
            return

        self._set_reference(reference_menu.selected)

    def _target_dropdown_hook(self, target_menu: vpython.menu):
        if target_menu.selected not in self._3dobjs:
            # The requested entity doesn't exist yet.
            target_menu.selected = self._origin.name
            return

        self._set_target(target_menu.selected)

    def _time_acc_dropdown_hook(self, time_acc_menu: vpython.menu):
        time_acc = int(
            time_acc_menu.selected.replace(',', '').replace('×', ''))
        self._commands.append(Request(
            ident=Request.TIME_ACC_SET,
            time_acc_set=time_acc))

    def _trail_checkbox_hook(self, selection: vpython.menu):
        self._show_trails = selection.checked
        for name, obj in self._3dobjs.items():
            obj.make_trail(selection.checked)

        if not self._show_trails:
            # Turning on trails set our camera origin to be the reference,
            # instead of the camera centre. Revert that when we turn off trails
            self._set_origin(self._sidebar.centre_menu._menu.selected)

    def _orbits_checkbox_hook(self, selection: vpython.menu) -> None:
        self._orbit_projection.show(selection.checked)

    def rate(self, framerate: int) -> None:
        """Alias for vpython.rate(framerate). Basically sleeps 1/framerate"""
        vpython.rate(framerate)

    def set_pause(self, pause: bool):
        """Toggles whether the FlightGui considers itself paused."""
        self._pause = pause
        self._pause_label.visible = self._pause
        # TODO: wait until https://github.com/vpython/vpython-jupyter/issues/2
        # is resolved before re-enabling the next two lines.
        # self._sidebar._save_box.disabled = not self._pause
        # self._sidebar._load_box.disabled = not self._pause
        if self._pause:
            self._commands.append(Request(
                ident=Request.TIME_ACC_SET, time_acc_set=0))
        else:
            # If we're unpausing, use the selected time acc value.
            self._time_acc_dropdown_hook(self._sidebar.time_acc_menu._menu)

    def _save_hook(self, textbox: vpython.winput):
        try:
            common.write_savefile(self._state, common.savefile(textbox.text))
            textbox.text = 'File saved!'
        except OSError:
            log.exception('Caught exception during file saving')
            textbox.text = 'Error writing file!'

    def _load_hook(self, textbox: vpython.winput):
        try:
            self._commands.append(Request(
                ident=Request.LOAD_SAVEFILE, loadfile=textbox.text))
            textbox.text = 'File loaded!'
        except OSError:
            # TODO: these exceptions will never happen.
            log.exception('Exception during file loading')
            textbox.text = 'File not found!'
        except (google.protobuf.json_format.ParseError,
                json.decoder.JSONDecodeError):
            log.exception('Exception parsing loadfile')
            textbox.text = 'File undreadable!'

    def _navmode_hook(self, menu: vpython.menu):
        self._commands.append(Request(
            ident=Request.NAVMODE_SET,
            navmode=state.Navmode[menu.selected].value))

    def _misc_command_hook(self, menu: vpython.menu):
        if menu.selected == MiscCommand.UNDOCK.value:
            self._commands.append(Request(ident=Request.UNDOCK))

    def lead_server_communication_requested(self) -> bool:
        # This should only be called when this FlightGui is the frontend of a
        # mirror server. This will probably throw an AttributeError otherwise.
        if self._sidebar.follow_lead_checkbox is None:
            # We're not even running in mirror mode you absolute cheese
            return False
        return self._sidebar.follow_lead_checkbox._checkbox.checked
# end of class FlightGui


class Sidebar:
    def __init__(self, flight_gui: FlightGui, running_as_mirror: bool):
        """Create the sidebar caption."""
        self._parent = flight_gui

        self._create_wtexts()

        Checkbox(lambda checkbox: self._parent.set_pause(checkbox.checked),
                 False, "Pause",
                 "Pause simulation. Can only save/load when paused.")
        self.trails_checkbox = Checkbox(
            self._parent._trail_checkbox_hook,
            DEFAULT_TRAILS, 'Trails',
            "Graphically intensive")
        self.orbits_checkbox = Checkbox(
            self._parent._orbits_checkbox_hook,
            False, 'Orbit',
            "Simple projection of hab around reference. "
            "Hyperbola not accurate sorry :(")
        vpython.canvas.get_selected().append_to_caption("<br/>")

        self._create_menus()

        # If you change the order of these, note that the placeholder text
        # is set in footer.html
        self._save_box = vpython.winput(
            bind=self._parent._save_hook, type='string')
        # self._save_box.disabled = True
        vpython.canvas.get_selected().append_to_caption("\n")
        self._load_box = vpython.winput(
            bind=self._parent._load_hook, type='string')
        # self._load_box.disabled = True
        vpython.canvas.get_selected().append_to_caption("\n")
        vpython.canvas.get_selected().append_to_caption(
            "<span class='helptext'>Filename to save/load under data/saves/</span>")
        vpython.canvas.get_selected().append_to_caption("\n")
        vpython.canvas.get_selected().append_to_caption("<br/>")

        self.follow_lead_checkbox: Optional[Checkbox]
        if running_as_mirror:
            self.follow_lead_checkbox = Checkbox(
                lambda checkbox: self._disable_inputs(checkbox.checked),
                True, 'Follow lead server',
                "Check to keep this mirror program in sync with the "
                "mirror://[host]:[port] OrbitX lead server specified at "
                "startup"
            )
        else:
            self.follow_lead_checkbox = None

        common.remove_vpython_css()

        with open(Path('orbitx', 'graphics', 'footer.html')) as footer:
            vpython.canvas.get_selected().append_to_caption(footer.read())

    def _disable_inputs(self, disabled: bool):
        """Enable or disable all inputs, except for networking checkbox."""
        # TODO: wait until https://github.com/vpython/vpython-jupyter/issues/2
        # for input_form in [
        #     self.centre_menu, self.reference_menu, self.target_menu,
        #         self.navmode_menu, self.time_acc_menu, self.undock_button]:
        #     # input_form.disabled = disabled
        #     pass

    def _create_wtexts(self):
        vpython.canvas.get_selected().caption += "<table>\n"
        self._wtexts: List[Text] = []

        self._wtexts.append(Text(
            "Simulation time",
            lambda state: datetime.fromtimestamp(
                state.timestamp, common.TIMEZONE).strftime('%x %X'),
            "Current time in simulation",
            new_section=False))
        self._wtexts.append(Text(
            "Orbit speed",
            lambda state: common.format_num(calc.orb_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s"),
            "Speed required for circular orbit at current altitude",
            new_section=False))

        self._wtexts.append(Text(
            "Periapsis",
            lambda state: common.format_num(calc.periapsis(
                state.craft_entity(),
                state.reference_entity()), " m"),
            "Lowest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(Text(
            "Apoapsis",
            lambda state: common.format_num(calc.apoapsis(
                state.craft_entity(),
                state.reference_entity()), " m"),
            "Highest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(Text(
            # The H in HRT stands for Habitat, even though craft is more
            # general and covers AYSE, but HRT is the familiar triple name and
            # the Hawking III says trans rights.
            "HRT phase θ",
            lambda state: common.format_num(calc.phase_angle(
                state.craft_entity(),
                state.reference_entity(),
                state.target_entity()), "°") or
            "Same ref and targ",
            "Angle between Habitat, Reference, and Target",
            new_section=False))

        self._wtexts.append(Text(
            "Throttle",
            lambda state: "{:.1%}".format(state.craft_entity().throttle),
            "Percentage of habitat's maximum rated engines",
            new_section=True))

        self._wtexts.append(Text(
            "Engine Acceleration",
            lambda state: common.format_num(calc.engine_acceleration(
                state.craft_entity()), " m/s/s"),
            "Acceleration due to craft's engine thrust",
            new_section=False))

        self._wtexts.append(Text(
            "Drag",
            lambda state: common.format_num(np.linalg.norm(calc.drag(state)),
                                            " m/s/s"),
            "Atmospheric drag acting on the craft",
            new_section=False))

        self._wtexts.append(Text(
            "Fuel ",
            lambda state: common.format_num(state.craft_entity(
            ).fuel, " kg"), "Remaining fuel of habitat",
            new_section=False))

        self._wtexts.append(Text(
            "Ref altitude",
            lambda state: common.format_num(calc.altitude(
                state.craft_entity(),
                state.reference_entity()), " m"),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(Text(
            "Ref speed",
            lambda state: common.format_num(calc.speed(
                state.craft_entity(),
                state.reference_entity()), " m/s"),
            "Speed of habitat above reference surface",
            new_section=False))

        self._wtexts.append(Text(
            "Vertical speed",
            lambda state: common.format_num(calc.v_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s "),
            "Vertical speed of habitat towards/away reference surface",
            new_section=False))

        self._wtexts.append(Text(
            "Horizontal speed",
            lambda state: common.format_num(calc.h_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s "),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(Text(
            "Pitch θ",
            lambda state: common.format_num(np.degrees(calc.pitch(
                state.craft_entity(),
                state.reference_entity())) % 360, "°"),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(Text(
            "Targ altitude",
            lambda state: common.format_num(calc.altitude(
                state.craft_entity(),
                state.target_entity()), " m"),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(Text(
            "Targ speed",
            lambda state: common.format_num(calc.speed(
                state.craft_entity(),
                state.target_entity()), " m/s"),
            "Speed of habitat above target surface",
            new_section=False))

        self._wtexts.append(Text(
            "Landing acc",
            lambda state: common.format_num(calc.landing_acceleration(
                state.craft_entity(),
                state.target_entity()), " m/s/s") or
            "no vertical landing",
            "Constant engine acc to land during vertical descent to target",
            new_section=False))

        vpython.canvas.get_selected().caption += "</table>"
    # end of _create_wtexts

    def _create_menus(self):
        # We can't change the choices in each vpython menu after creation, but
        # the Module (and in the future maybe other objects) can be created.
        # Have them in the choices list at the beginning, and handle when they
        # are selected without the corresponding entity existing yet.
        entity_names = list(self._parent._3dobjs) + [common.MODULE]

        self.centre_menu = Menu(
            choices=entity_names,
            selected=common.DEFAULT_CENTRE,
            bind=self._parent._recentre_dropdown_hook,
            caption="Centre",
            helptext="Focus of camera"
        )
        self.centre_menu._menu.selected = common.DEFAULT_CENTRE

        self.reference_menu = Menu(
            choices=entity_names,
            selected=common.DEFAULT_REFERENCE,
            bind=self._parent._reference_dropdown_hook,
            caption="Reference",
            helptext="Take position, velocity relative to this"
        )

        self.target_menu = Menu(
            choices=entity_names,
            selected=common.DEFAULT_TARGET,
            bind=self._parent._target_dropdown_hook,
            caption="Target",
            helptext="Entity to land or dock with"
        )

        self.navmode_menu = Menu(
            choices=[item.name for item in state.Navmode],
            selected=state.Navmode(0).name,
            bind=self._parent._navmode_hook,
            caption="NAV mode",
            helptext="Automatically points habitat"
        )

        self.time_acc_menu = Menu(
            choices=[f'{n:,}×' for n in
                     [1, 5, 10, 50, 100, 1_000, 10_000, 100_000]],
            selected='1×',
            bind=self._parent._time_acc_dropdown_hook,
            caption="Warp",
            helptext="Speed of simulation"
        )

        self._misc_menu = Menu(
            choices=[command.value for command in MiscCommand],
            selected=MiscCommand.UNSELECTED.value,
            bind=self._parent._misc_command_hook,
            caption="Command",
            helptext="Select elements in this menu to issue other commands"
        )
    # end of _create_menus

    def update(self, draw_state: state.PhysicsState):
        self.reference_menu._menu.selected = draw_state.reference
        self.target_menu._menu.selected = draw_state.target
        self.navmode_menu._menu.selected = draw_state.navmode.name
        for wtext in self._wtexts:
            wtext.update(draw_state)

        # TODO: wait until https://github.com/vpython/vpython-jupyter/issues/2
        # self.undock_button._button.disabled = not (
            # draw_state[common.HABITAT].landed_on == common.AYSE)

# -*- coding: utf-8 -*-
"""
Defines FlightGui, a class that provides a main loop for flight.

Call FlightGui.draw() in the main loop to update positions in the GUI.
Call FlightGui.pop_commands() to collect user input.
"""

import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

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
from orbitx.graphics.vpython_widgets import Checkbox, Menu, TableText
from orbitx.graphics.orbit_projection import OrbitProjection

log = logging.getLogger()

DEFAULT_TRAILS = False

TIME_ACC_TO_STR = {time_acc.value: time_acc.desc
                   for time_acc in common.TIME_ACCS}
STR_TO_TIME_ACC = {v: k for k, v in TIME_ACC_TO_STR.items()}


class MiscCommand(Enum):
    UNSELECTED = 'Select'
    UNDOCK = 'Undock'
    IGNITE_SRBS = 'Ignite SRBs'
    DEPLOY_PARACHUTE = 'Toggle Parachute'


class FlightGui:

    def __init__(
        self,
        draw_state: state.PhysicsState,
        *,
        title: str,
        running_as_mirror: bool
    ) -> None:
        assert len(draw_state) >= 1

        self._state = draw_state
        # create a vpython canvas, onto which all 3D and HTML drawing happens.
        self._scene = self._init_canvas(title, running_as_mirror)

        self._show_label: bool = True
        self._show_trails: bool = DEFAULT_TRAILS
        self._paused: bool = False
        self._removed_saveload_hint: bool = False
        self._origin: state.Entity
        self.texture_path: Path = Path('data', 'textures')
        self._commands: List[Request] = []
        self._paused_label = vpython.label(
            text="Simulation paused; saving and loading enabled.\n"
                 "When finished, unpause by setting a time acceleration.",
            xoffset=0, yoffset=200, line=False, height=25, border=20,
            opacity=1, visible=False)

        self._3dobjs: Dict[str, ThreeDeeObj] = {}
        # remove vpython ambient lighting
        self._scene.lights = []  # This line shouldn't be removed

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

    def _init_canvas(self, title: str, running_as_mirror: bool) \
            -> vpython.canvas:
        """Set up our vpython canvas and other internal variables"""
        _scene = vpython.canvas(
            title=f'<title>{title}</title>',
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

    def pop_commands(self) -> List[Request]:
        """Take gathered user input and send it off."""
        old_commands = self._commands
        self._commands = []
        return old_commands

    def _handle_keydown(self, evt: vpython.event_return) -> None:
        """Called in a non-main thread by vpython when it gets key input."""
        if self._paused:
            # The user could be entering in things in the text fields, so just
            # wait until they're not paused.
            return
        if self.requesting_read_from_physics_server():
            # We shouldn't be generating any commands, ignore this.
            return

        k = evt.key
        if k == 'l':
            self._show_label = not self._show_label
            for name, obj in self._3dobjs.items():
                obj._show_hide_label()
        elif k == 'a':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=common.SPIN_CHANGE))
        elif k == 'd':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=-common.SPIN_CHANGE))
        elif k == 'A':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=common.FINE_SPIN_CHANGE))
        elif k == 'D':
            self._commands.append(Request(
                ident=Request.HAB_SPIN_CHANGE,
                spin_change=-common.FINE_SPIN_CHANGE))
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
            if self._sidebar.time_acc_menu._menu.index != 1:
                self._sidebar.time_acc_menu._menu.index -= 1
                self._time_acc_dropdown_hook(self._sidebar.time_acc_menu._menu)
        elif k == 'p':
            # Pause
            self._sidebar.time_acc_menu._menu.index = 0
            self._time_acc_dropdown_hook(self._sidebar.time_acc_menu._menu)
    # end of _handle_keydown

    def draw(self, draw_state: state.PhysicsState) -> None:
        self._state = draw_state

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
        time_acc = STR_TO_TIME_ACC[time_acc_menu.selected]
        # Insert this TIME_ACC_SET command at the beginning of the list,
        # so that we process it as quickly as possible. This isn't necessary,
        # but can get us out of a stuck simulation faster.
        self._commands.insert(0, Request(
            ident=Request.TIME_ACC_SET,
            time_acc_set=time_acc))

        if self._paused and time_acc != 0:
            # We are unpausing.
            self.pause(False)
        if not self._paused and time_acc == 0:
            # We are pausing.
            self.pause(True)

    def trail_checkbox_hook(self, selection: vpython.menu):
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

    def pause(self, pause: bool):
        """Sets whether the FlightGui considers itself paused.
        This doesn't effect physics simulation at all."""
        self._paused = pause
        self._paused_label.visible = self._paused
        self._sidebar._save_box.disabled = not self._paused
        self._sidebar._load_box.disabled = not self._paused
        if pause and not self._removed_saveload_hint:
            # We should remove the 'Pause sim to save and load' hint.
            vpython.canvas.get_selected().append_to_caption(
                "<script>remove_saveload_hint();</script>")
            self._removed_saveload_hint = True

    def _save_hook(self, textbox: vpython.winput):
        try:
            common.write_savefile(self._state, common.savefile(textbox.text))
            textbox.text = 'File saved!'
        except OSError:
            log.exception('Caught exception during file saving')
            textbox.text = 'Error writing file!'

    def _load_hook(self, textbox: vpython.winput):
        full_path = common.savefile(textbox.text)
        if full_path.is_file():
            self._commands.append(Request(
                ident=Request.LOAD_SAVEFILE, loadfile=textbox.text))
            textbox.text = 'File loaded!'
            # The file we loaded will have a non-zero time acc, unpause.
            self.pause(False)
            # Re-centre on the habitat.
            self._sidebar.centre_menu._menu.selected = common.HABITAT
            self._recentre_dropdown_hook(self._sidebar.centre_menu._menu)
        else:
            log.warning(f'Ignored non-existent loadfile: {full_path}')
            textbox.text = 'File not found!'

    def _navmode_hook(self, menu: vpython.menu):
        self._commands.append(Request(
            ident=Request.NAVMODE_SET,
            navmode=state.Navmode[menu.selected].value))

    def _misc_command_hook(self, menu: vpython.menu):
        if menu.selected == MiscCommand.UNDOCK.value:
            self._commands.append(Request(ident=Request.UNDOCK))
        elif menu.selected == MiscCommand.DEPLOY_PARACHUTE.value:
            self._commands.append(Request(
                ident=Request.PARACHUTE,
                deploy_parachute=not self._state.parachute_deployed))
        elif menu.selected == MiscCommand.IGNITE_SRBS.value:
            self._commands.append(Request(ident=Request.IGNITE_SRBS))
        menu.selected = MiscCommand.UNSELECTED.value

    def requesting_read_from_physics_server(self) -> bool:
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

        self.trails_checkbox = Checkbox(
            self._parent.trail_checkbox_hook,
            DEFAULT_TRAILS, 'Trails',
            "Graphically intensive")
        self.orbits_checkbox = Checkbox(
            self._parent._orbits_checkbox_hook,
            False, 'Orbit',
            "Simple projection of hab around reference.")
        vpython.canvas.get_selected().append_to_caption("<br/>")

        self._create_menus()

        # If you change the order of these, note that the placeholder text
        # is set in flight_gui_footer.html
        self._save_box = vpython.winput(
            bind=self._parent._save_hook, type='string')
        self._save_box.disabled = True
        vpython.canvas.get_selected().append_to_caption("\n")
        self._load_box = vpython.winput(
            bind=self._parent._load_hook, type='string')
        self._load_box.disabled = True
        vpython.canvas.get_selected().append_to_caption("\n")
        vpython.canvas.get_selected().append_to_caption(
            "<span class='helptext'>"
            "Filename to save/load under data/saves/</span>")
        vpython.canvas.get_selected().append_to_caption("\n")
        vpython.canvas.get_selected().append_to_caption("<br/>")

        self.follow_lead_checkbox: Optional[Checkbox]
        if running_as_mirror:
            start_off_following = True
            self.follow_lead_checkbox = Checkbox(
                lambda checkbox: self._disable_inputs(checkbox.checked),
                start_off_following, 'Follow physics server',
                "Check to keep this mirror program in sync with the "
                "mirror://[host]:[port] OrbitX physics server specified at "
                "startup"
            )
            self._disable_inputs(start_off_following)
        else:
            self.follow_lead_checkbox = None

        common.remove_vpython_css()
        common.include_vpython_footer_file(
            Path('orbitx', 'graphics', 'flight_gui_footer.html'))

    def _disable_inputs(self, disabled: bool):
        """Enable or disable all inputs, except for networking checkbox."""
        for menu in [
            self.centre_menu, self.reference_menu, self.target_menu,
                self.navmode_menu, self.time_acc_menu, self.misc_menu]:
            menu._menu.disabled = disabled
        for checkbox in [self.trails_checkbox, self.orbits_checkbox]:
            checkbox._checkbox.disabled = disabled

    def _create_wtexts(self):
        vpython.canvas.get_selected().caption += "<table>\n"
        self._wtexts: List[TableText] = []

        self._wtexts.append(TableText(
            "Simulation time",
            lambda state: datetime.fromtimestamp(
                state.timestamp, common.TIMEZONE).strftime('%x %X'),
            "Current time in simulation",
            new_section=False))
        self._wtexts.append(TableText(
            "Orbit speed",
            lambda state: common.format_num(calc.orb_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s"),
            "Speed required for circular orbit at current altitude",
            new_section=False))

        self._wtexts.append(TableText(
            "Periapsis",
            lambda state: common.format_num(calc.periapsis(
                state.craft_entity(),
                state.reference_entity()) / 1000, " km", decimals=3),
            "Lowest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(TableText(
            "Apoapsis",
            lambda state: common.format_num(calc.apoapsis(
                state.craft_entity(),
                state.reference_entity()) / 1000, " km", decimals=3),
            "Highest altitude in naïve orbit around reference",
            new_section=False))

        self._wtexts.append(TableText(
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

        self._wtexts.append(TableText(
            "Throttle",
            lambda state: "{:.1%}".format(state.craft_entity().throttle),
            "Percentage of habitat's maximum rated engines",
            new_section=True))

        self._wtexts.append(TableText(
            "Engine Acceleration",
            lambda state:
                common.format_num(calc.engine_acceleration(state), " m/s/s") +
                (' [SRB]' if state.srb_time > 0 else ''),
            "Acceleration due to craft's engine thrust",
            new_section=False))

        self._wtexts.append(TableText(
            "Drag",
            lambda state: common.format_num(np.linalg.norm(calc.drag(state)),
                                            " m/s/s"),
            "Atmospheric drag acting on the craft",
            new_section=False))

        self._wtexts.append(TableText(
            "Fuel",
            lambda state: common.format_num(
                state.craft_entity().fuel, " kg"),
            "Remaining fuel of craft",
            new_section=False))

        def rotation_formatter(state: state.PhysicsState) -> str:
            deg_spin = round(np.degrees(state.craft_entity().spin), ndigits=1)
            if deg_spin < 0:
                return f"{-deg_spin} °/s cw"
            elif deg_spin > 0:
                return f"{deg_spin} °/s ccw"
            else:
                return f"{deg_spin} °/s"
        self._wtexts.append(TableText(
            "Rotation",
            rotation_formatter,
            "Rotation speed of craft",
            new_section=False))

        self._wtexts.append(TableText(
            "Ref altitude",
            lambda state: common.format_num(calc.altitude(
                state.craft_entity(),
                state.reference_entity()) / 1000, " km", decimals=3),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(TableText(
            "Ref speed",
            lambda state: common.format_num(calc.speed(
                state.craft_entity(),
                state.reference_entity()), " m/s"),
            "Speed of habitat above reference surface",
            new_section=False))

        self._wtexts.append(TableText(
            "Vertical speed",
            lambda state: common.format_num(calc.v_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s "),
            "Vertical speed of habitat towards/away reference surface",
            new_section=False))

        self._wtexts.append(TableText(
            "Horizontal speed",
            lambda state: common.format_num(calc.h_speed(
                state.craft_entity(),
                state.reference_entity()), " m/s "),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(TableText(
            "Pitch θ",
            lambda state: common.format_num(np.degrees(calc.pitch(
                state.craft_entity(),
                state.reference_entity())) % 360, "°"),
            "Horizontal speed of habitat across reference surface",
            new_section=False))

        self._wtexts.append(TableText(
            "Targ altitude",
            lambda state: common.format_num(calc.altitude(
                state.craft_entity(),
                state.target_entity()) / 1000, " km", decimals=3),
            "Altitude of habitat above reference surface",
            new_section=True))

        self._wtexts.append(TableText(
            "Targ speed",
            lambda state: common.format_num(calc.speed(
                state.craft_entity(),
                state.target_entity()), " m/s"),
            "Speed of habitat above target surface",
            new_section=False))

        self._wtexts.append(TableText(
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

        # This div used by flight_gui_footer.html to locate the pause menu.
        vpython.canvas.get_selected().append_to_caption(
            '<div id="pause_anchor"></div>')
        self.time_acc_menu = Menu(
            choices=list(TIME_ACC_TO_STR.values()),
            selected=TIME_ACC_TO_STR[1],
            bind=self._parent._time_acc_dropdown_hook,
            caption="Warp",
            helptext="Speed of simulation"
        )

        self.misc_menu = Menu(
            choices=[command.value for command in MiscCommand],
            selected=MiscCommand.UNSELECTED.value,
            bind=self._parent._misc_command_hook,
            caption="Command",
            helptext="Several miscellaneous commands"
        )
    # end of _create_menus

    def update(self, draw_state: state.PhysicsState):
        self.reference_menu._menu.selected = draw_state.reference
        self.target_menu._menu.selected = draw_state.target
        self.navmode_menu._menu.selected = draw_state.navmode.name

        time_acc = int(draw_state.time_acc)
        new_acc_str = TIME_ACC_TO_STR[time_acc]
        if new_acc_str not in self.time_acc_menu._menu._choices:
            raise ValueError(f'"{new_acc_str}" not a valid time acceleration')
        else:
            self.time_acc_menu._menu.selected = new_acc_str

        if self._parent._paused and time_acc != 0:
            # We are unpausing.
            self._parent.pause(False)
        if not self._parent._paused and time_acc == 0:
            # We are pausing.
            self._parent.pause(True)

        for wtext in self._wtexts:
            wtext.update(draw_state)

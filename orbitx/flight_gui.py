"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import logging
from pathlib import Path

log = logging.getLogger()


class FlightGui:

    def __init__(self, physical_state_to_draw, texture_path=None):
        # Note that this might actually start an HTTP server!
        import vpython
        self._vpython = vpython

        self._scene = vpython.canvas(
            title='<b>OrbitX\n</b>',
            align='right',
            width=1000,
            height=600,
            center=vpython.vector(0, 0, 0),
            autoscale=True
        )

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
        self._physical_state_to_draw = physical_state_to_draw
        self._set_origin("Habitat")  # Initial origin value would be Habitat

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            self._labels[planet.name] = self._draw_labels(planet)
            if planet.name == 'Habitat':
                self._habitat_arrow = self._draw_habitat_arrow(planet)
                self.recentre_camera("Habitat")  # Original view is set to the habitat object
        self._scene.autoscale = False
        self._set_caption()

    def _posn(self, entity):
        """Provides the vector of the entity position with regard to the origin planet position."""

        return self._vpython.vector(
                entity.x - self._origin.x,
                entity.y - self._origin.y,0)

    def _set_origin(self, entity_name):
        """Set origin position for rendering universe and reset the trails.

        Because GPU(Graphics Processing Unit) cannot deal with extreme case of scene center
        being approximately 1e11 (planets position), origin entity should be reset every time
        when making a scene.center update.
        """
        try:
            self._origin = [entity
                            for entity in self._physical_state_to_draw.entities
                            if entity.name == entity_name][0]
        except IndexError:
            # Couldn't find the Habitat, default to the first entity
            self._origin = self._physical_state_to_draw.entities[0]

        for k, v in self._spheres.items():
            v.clear_trail()


    def _show_hide_label(self):
        if self._show_label:
            for key, label in self._labels.items():
                label.visible = True
        else:
            for key, label in self._labels.items():
                label.visible = False

    def _handle_keydown(self, evt):
        """Input key handler"""
        # global _show_label, _pause
        k = evt.key
        if (k == 'l'):
            self._show_label = not self._show_label
            self._show_hide_label()
        elif (k == 'p'):
            self._pause = not self._pause

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

    def _get_objname(self, obj):
        """Given object it finds the name of the planet"""
        for k, v in self._spheres.items():
            if v == obj:
                obj_name = k
        return obj_name

    # TODO: 1)Update with correct physics values
    def _set_caption(self):
        """Set and update the captions."""
        self._scene.caption = "\n"
        self._scene.append_to_caption("ref Vo: XXX" + "\n")
        self._scene.append_to_caption("V hab-ref: XXX" + "\n")
        self._scene.append_to_caption("Vtarg-ref: XXX" + "\n")
        self._scene.append_to_caption("Engine: XXX" + "\n")
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption("Acc: XXX" + "\n")
        self._scene.append_to_caption("Vcen: XXX" + "\n")
        self._scene.append_to_caption("Vtan: XXX" + "\n")
        self._scene.append_to_caption("\n")
        self._set_menus()

    # TODO: create bind functions for target, ref, and NAV MODE
    def _set_menus(self):
        """This creates dropped down menu which is used when set_caption."""
        self._scene.append_to_caption(
            "<b>Center: </b>")
        center = self._vpython.menu(choices=list(self._spheres),
                                    pos=self._scene.caption_anchor, bind=self._recentre_dropdown_hook, selected='Sun')
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
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'AYSE'],
            pos=self._scene.caption_anchor, bind=self._recentre_dropdown_hook, selected='AYSE')
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Nav:     </b>")
        NAVmode = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'deprt ref'],
            pos=self._scene.caption_anchor, bind=self._recentre_dropdown_hook, selected='deprt ref')
        self._scene.append_to_caption("\n")

    def draw(self, physical_state_to_draw):
        if self._pause:
            self._scene.pause("Simulation is paused. \n Press 'p' to continue")
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)
            if self._show_label:
                self._update_label(planet)
            if planet.name == "Habitat":
                self._update_habitat_arrow(planet)

    def _draw_habitat_arrow(self, planet):
        """Create an arrow that restore the habitat direction information"""
        return self._vpython.arrow(
            pos=(
                self._posn(planet)
            ),
            axis=self._vpython.vector(planet.vx/240, planet.vy/240, 0),
            shaftwidth= planet.r,
            headwidth= planet.r,
            color = self._vpython.color.green
        )

    def _update_habitat_arrow(self, planet):
        """Update the position of the arrow """
        pos_vector = self._posn(planet)
        self._habitat_arrow.pos = self._vpython.vector(pos_vector.x-planet.vx/400, pos_vector.y-planet.vy/400, 0)

        #self._habitat_arrow.pos = (
        #    self._posn(planet)
        #)
        self._habitat_arrow.axis = self._vpython.vector(
            planet.vx/180, planet.vy/180, 0)

    def _draw_labels(self, planet):
        label = self._vpython.label(
            visible=True, pos=self._posn(planet),
            text=planet.name, xoffset=0, yoffset=10, height=16,
            border=4, font='sans')

        if planet.name == 'Habitat':
            label.text += f'\nFuel: {planet.fuel}'

        return label

    def _draw_sphere(self, planet):
        texture = self._texture_path / (planet.name + '.jpg')

        if planet.name == "Habitat":
            # Todo: habitat object should be seperately defined from planets
            obj = self._vpython.sphere(
                pos=self._posn(planet),
                axis=self._vpython.vector(
                    planet.vx, planet.vy, 0),
                radius=planet.r,
                length=2 * planet.r,
                make_trail=True,
                shininess=0.1,
                opacity =0
            )
        else:
            obj = self._vpython.sphere(
                pos=self._posn(planet),
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

        return obj

    def _update_sphere(self, planet):
        self._spheres[planet.name].pos = self._posn(planet)

    def _update_label(self, planet):
        if planet.name == "Habitat":
            self._labels["Habitat"].text = "Habitat\n" + \
                "Fuel: " + str(planet.fuel)
        self._labels[planet.name].pos = self._posn(planet)

    def _recentre_dropdown_hook(self, selection):
        self._set_origin(selection.selected)
        self.recentre_camera(selection.selected)

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

    def rate(self, framerate):
        self._vpython.rate(framerate)

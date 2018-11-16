"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import logging
import os

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

        self.show_label = True
        self.pause = False
        self.pause_label = vpython.label(text="Simulation Paused.", visible=False)

        self._scene.bind('keydown', self._handle_keydown)
        self._scene.bind('click', self._handle_click)
        self._set_caption()

        self._spheres = {}
        self._labels = {}

        self._texture_path = texture_path
        if texture_path is None:
            # If we're in src/ look for src/../textures/
            self._texture_path = 'textures'
        #stars = os.path.join(self._texture_path, 'Stars.jpg')
        #vpython.sphere(radius=9999999999999, texture='textures/Stars.jpg')

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            self._labels[planet.name] = self._draw_labels(planet)
            if planet.name == 'Sun':  # The sun is special!
                self._scene.camera.follow(
                    self._spheres[planet.name])  # thanks Copernicus
                self._spheres[planet.name].emissive = True  # The sun glows!
                self._scene.lights = []
                self._lights = [self._vpython.local_light(
                    pos=self._vpython.vector(planet.x, planet.y, 0)
                )]

    def _show_hide_label(self):
        if self.show_label:
            for key, label in self._labels.items():
                label.visible=True
        else:
            for key, label in self._labels.items():
                label.visible=False

    def _handle_keydown(self, evt):
        """Input key handler"""
        #global show_label, pause
        k = evt.key
        if (k == 'l'):
            self.show_label = not self.show_label
            self._show_hide_label()
        elif (k == 'p'):
            self.pause = not self.pause


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
            if obj != None:
                self.update_caption(obj)

        except AttributeError:
            pass
        # clicked = True

    def get_objname(self, obj):
        """Given object it finds the name of the planet"""

        for k, v in self._spheres.items():
            if v == obj:
                obj_name = k
        return obj_name

    def _update_center(self, m):
        """Change camera to focus on different object"""
        value = m.selected
        print(value)
        self._scene.center = self._spheres[value].pos

    #TODO: 1)Update with correct physics values
    def _set_caption(self):
        """Set and update the captions"""

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

    #TODO: create bind functions for target, ref, and NAV MODE
    def _set_menus(self):
        """This creates dropped down menu which is used when set_caption"""

        self._scene.append_to_caption(
            "<b>Center: </b>")
        center = self._vpython.menu(choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune','Pluto'],
                                    pos=self._scene.caption_anchor,bind=self.recentre_camera, selected='Sun')
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Target: </b>")
        target = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto','AYSE'],
            pos=self._scene.caption_anchor, bind=self._update_center, selected='AYSE')
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Ref:      </b>")
        ref = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'AYSE'],
            pos=self._scene.caption_anchor, bind=self._update_center, selected='AYSE')
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption(
            "<b>Nav:     </b>")
        NAVmode = self._vpython.menu(
            choices=['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
                     'Neptune', 'Pluto', 'deprt ref' ],
            pos=self._scene.caption_anchor, bind=self._update_center, selected='deprt ref')
        self._scene.append_to_caption("\n")


    def draw(self, physical_state_to_draw):
        if self.pause:
            self._scene.pause("Simulation is paused. \n Press 'p' to continue")
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)
            if self.show_label:
                self._update_label(planet)

    def _draw_labels(self, planet):
        return self._vpython.label(visible=True, pos=self._vpython.vector(planet.x, planet.y, 0), text=planet.name, xoffset=0, yoffset=10, hiehgt=16,
                                   border=4, font='sans')

    def _draw_sphere(self, planet):
        texture = os.path.join(self._texture_path, planet.name + '.jpg')
        if os.path.isfile(texture):
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, planet.y, 0),
                radius=planet.r,
                make_trail=True,
                shininess=0.1,
                texture=texture
            )
        else:
            log.debug(f'Could not find texture {texture}')
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, planet.y, 0),
                radius=planet.r,
                shininess=0.1,
                make_trail=True
            )

    def _update_sphere(self, planet):
        self._spheres[planet.name].pos = self._vpython.vector(
            planet.x, planet.y, 0)

    def _update_label(self, planet):
        self._labels[planet.name].pos = self._vpython.vector(
            planet.x, planet.y, 0)

    def recentre_camera(self, planet):
        planet_name = planet.selected

        try:
            self._scene.center = self._spheres[planet_name].pos
            self._scene.camera.follow(self._spheres[planet_name])
        except KeyError:
            log.error(f'Unrecognized planet to follow: "{planet_name}"')

"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import os


class FlightGui:

    cur_caption = 0
    caption_obj = ["Sun", "AYSE", "AYSE", "deprt ref"]

    def set_caption(self):
        if self.cur_caption == 0:
            self._scene.caption = "\n"
            self._scene.append_to_caption("ref Vo: ")
            self._scene.append_to_caption("\n")
            self._scene.append_to_caption("<b>center:</b>", self.caption_obj[0], "\n")
            self._scene.append_to_caption("target:", self.caption_obj[1], "\n")
            self._scene.append_to_caption("ref:", self.caption_obj[2], "\n")
            self._scene.append_to_caption("NAVmode:", self.caption_obj[3], "\n")
        elif self.cur_caption == 1:
            self._scene.caption = "\n"
            self._scene.append_to_caption("center:", self.caption_obj[0], "\n")
            self._scene.append_to_caption("<b>target:</b>", self.caption_obj[1], "\n")
            self._scene.append_to_caption("ref:", self.caption_obj[2], "\n")
            self._scene.append_to_caption("NAVmode:", self.caption_obj[3], "\n")
        elif self.cur_caption == 2:
            self._scene.caption = "\n"
            self._scene.append_to_caption("center:", self.caption_obj[0], "\n")
            self._scene.append_to_caption("target:", self.caption_obj[1], "\n")
            self._scene.append_to_caption("<b>ref:</b>", self.caption_obj[2], "\n")
            self._scene.append_to_caption("NAVmode:", self.caption_obj[3], "\n")
        elif self.cur_caption == 3:
            self._scene.caption = "\n"
            self._scene.append_to_caption("center:", self.caption_obj[0], "\n")
            self._scene.append_to_caption("target:", self.caption_obj[1], "\n")
            self._scene.append_to_caption("ref:", self.caption_obj[2], "\n")
            self._scene.append_to_caption("<b>NAVmode:</b>", self.caption_obj[3], "\n")

    def _handle_keydown(self, evt):
        global show_label, pause
        #print('Got keydown', evt)
        k = evt.key
        if (k == 'l'):
            show_label = not show_label
        elif (k == 'p'):
            pause = not pause
        elif (k == 'e'):
            self._scene.center = self._spheres['Earth'].pos
            #show = label_earth.visible
            #label_earth.visible = not show
            #label_earth.pos = earth.pos
        elif (k == 's'):
            self._scene.center = self._spheres['Sun'].pos
            #show = label_sun.visible
            #label_sun.visible = not show
            #label_sun.pos = sun.pos
        elif (k == 't'):
            self.cur_caption = (self.cur_caption + 1) % 4
            self.set_caption()

    def get_objname(self, obj):
        for k, v in self._spheres.items():
            if v == obj:
                obj_name = k;
        return obj_name

    def update_caption(self, obj):
        obj_name = self.get_objname(obj)
        if self.cur_caption == 0:
            # action: update the camera center
            self.scene.center = obj.pos
            self.caption_obj[0] = obj_name
            self.set_caption()
        if self.cur_caption == 1:
            #action required
            self.caption_obj[1] = obj_name
            self.set_caption()

        if self.cur_caption == 2:
            #action required
            self.caption_obj[2] = obj_name
            self.set_caption()

        if self.cur_caption == 3:
            #action required
            self.caption_obj[3] = obj_name
            self.set_caption()

    def _handle_click(self, evt):
        #print('Got click', evt)
        # global obj, clicked
        try:
            obj = self._scene.mouse.pick
            if obj != None:
                self.update_caption(obj)

        except AttributeError:
            pass
        #clicked = True

    def __init__(self, physical_state_to_draw, texture_path=None):
        import vpython  # Note that this might actually start an HTTP server!
        self._vpython = vpython
        self._scene = vpython.canvas(
            title='Space Simulator',
            align='right',
            width=1000,
            height=600,
            center=vpython.vector(0, 0, 0),
            autoscale=True
        )

        self._scene.bind('keydown', self._handle_keydown)
        self._scene.bind('click', self._handle_click)
        self.set_caption()

        self._spheres = {}
        self._labels = {}

        self._texture_path = texture_path
        if texture_path is None:
            # If we're in src/ look for src/../textures/
            self._texture_path = 'textures'

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            self._labels[planet.name] = self._draw_labels(planet)
            if planet.name == 'Sun':
                self._scene.camera.follow(self._spheres[planet.name])

    def draw(self, physical_state_to_draw):
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)

    def rate(self, framerate):
        self._vpython.rate(framerate)

    def _draw_labels(self, planet):
        return self._vpython.label(visible=True, pos=self._vpython.vector(planet.x, 0, planet.y), text=planet.name, xoffset=0, yoffset=50, hiehgt=16,
                          border=4, font='sans')

    def _draw_sphere(self, planet):
        texture = os.path.join(self._texture_path, planet.name + '.jpg')
        if os.path.isfile(texture):
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, planet.y, 0),
                radius=planet.r,
                make_trail=True,
                texture=texture
            )
        else:
            print('Could not find texture', texture)
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, planet.y, 0),
                radius=planet.r,
                make_trail=True
            )

    def _update_sphere(self, planet):

        self._spheres[planet.name].pos = self._vpython.vector(
            planet.x, planet.y, 0)


    def recentre_camera(self, planet_name):
        try:
            self._scene.camera.follow(self._spheres[planet_name])
        except KeyError:
            print('Unrecognized planet to follow:', planet_name)


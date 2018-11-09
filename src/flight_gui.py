"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import os


class FlightGui:
    def _handle_keydown(self, evt):
        global show_label, pause
        print('Got keydown', evt)
        k = evt.key
        if (k == 'l'):
            show_label = not show_label
        elif (k == 'p'):
            pause = not pause


    def _handle_click(self, evt):
        print('Got click', evt)

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
        self._scene.caption = ""
        self._scene.append_to_caption("\n")
        self._scene.append_to_caption("center:", "\n")
        self._scene.append_to_caption("target:", "\n")
        self._scene.append_to_caption("ref:", "\n")
        self._scene.append_to_caption("NAVmode", "\n")



        self._spheres = {}

        self._texture_path = texture_path
        if texture_path is None:
            # If we're in src/ look for src/../textures/
            self._texture_path = 'textures'

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)
            if planet.name == 'Sun':
                self._scene.camera.follow(self._spheres[planet.name])

    def draw(self, physical_state_to_draw):
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)
            self._scene.caption = ""
            self._scene.append_to_caption("\n")
            self._scene.append_to_caption("center:", "XXX", "\n")
            self._scene.append_to_caption("target:", "\n")
            self._scene.append_to_caption("ref:", "\n")
            self._scene.append_to_caption("NAVmode", "\n")

    def rate(self, framerate):
        self._vpython.rate(framerate)


    def _draw_sphere(self, planet):
        texture = os.path.join(self._texture_path, planet.name + '.jpg')
        if os.path.isfile(texture):
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, 0, planet.y),
                radius=planet.r,
                make_trail=True,
                texture=texture
            )
        else:
            print('Could not find texture', texture)
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, 0, planet.y),
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


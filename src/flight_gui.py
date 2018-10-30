"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import threading
import os


class FlightGui:
    def __init__(self, physical_state_to_draw, texture_path=None):
        import vpython  # Note that this might actually start an HTTP server!
        self._vpython = vpython
        self._scene = vpython.canvas(
            title='Space Simulator',
            align='left',
            width=600,
            height=600,
            center=vpython.vector(0, 0, 0)
            )

        self._spheres = {}

        self._texture_path = texture_path
        if texture_path is None:
            # If we're in src/ look for src/../textures/
            self._texture_path = 'textures'

        for planet in physical_state_to_draw.entities:
            self._spheres[planet.name] = self._draw_sphere(planet)

    def draw(self, physical_state_to_draw):
        for planet in physical_state_to_draw.entities:
            self._update_sphere(planet)

    def wait(self, framerate):
        self._vpython.rate(framerate)

    def _draw_sphere(self, planet):
        texture = os.path.join(self._texture_path, planet.name + '.jpg')
        print(texture)
        if os.path.isfile(texture):
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, 0, planet.y),
                radius=planet.r,
                make_trail=True,
                texture=texture
                )
        else:
            return self._vpython.sphere(
                pos=self._vpython.vector(planet.x, 0, planet.y),
                radius=planet.r,
                make_trail=True
                )

    def _update_sphere(self, planet):
        self._spheres[planet.name].pos = self._vpython.vector(
            planet.x, planet.y, 0)

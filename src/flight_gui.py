"""
Class that provides a main loop for flight.

The main loop drawsa GUI and collects input.
"""
import threading

class FlightGui:
    def __init__(self, physical_state, texture_path='textures/'):
        import vpython # Note that this might actually start an HTTP server!
        self._vpython = vpython
        self._scene = vpython.canvas(
            title='Space Simulator',
            align='left',
            width=600,
            height=600,
            center=vpython.vector(0,0,0)
        )

        self._spheres = []
        self._first_draw = True

    def draw(self, physical_state_to_draw):
        for planet in physical_state_to_draw.entities:
            if self._first_draw:
                self._spheres.append(self._draw_sphere(planet))
            else:
                self._update_sphere(self._spheres[0], planet) # TODO: hack

        self._first_draw = False

    def wait(self, framerate):
        self._vpython.rate(framerate)

    def _draw_sphere(self, planet):
        return self._vpython.sphere(
            pos=self._vpython.vector(planet.x, 0, planet.y),
            radius=planet.r,
            make_trail=True
        )

    def _update_sphere(self, sphere, planet):
        sphere.pos = self._vpython.vector(planet.x, planet.y, 0)

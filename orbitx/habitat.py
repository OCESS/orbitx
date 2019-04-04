import vpython

from orbitx import calc
from orbitx import common
from orbitx import state
from orbitx.displayable import Displayable
from orbitx.flight_gui import FlightGui


class Habitat(Displayable):
    def __init__(self, entity: state.Entity, flight_gui: FlightGui,
                 scene: vpython.canvas, minimap: vpython.canvas) -> None:
        super(Habitat, self).__init__(entity, flight_gui)
        self._habitat_trail: vpython.trail = None
        self._ref_arrow: vpython.arrow = None
        self._velocity_arrow: vpython.arrow = None
        self._obj = self.__create_habitat(scene, minimap)
        self._draw_labels()
    # end of __init__

    def hab_object(self, scene: vpython.canvas) -> vpython.compound:
        # Change which scene we're drawing a new habitat in
        def vector(x: float, y: float, z: float) -> vpython.vector:
            return vpython.vector(x, y, z)

        def vertex(x: float, y: float, z: float) -> vpython.vector:
            return vpython.vertex(pos=vector(x, y, z))

        old_scene = vpython.canvas.get_selected()
        scene.select()

        body = vpython.cylinder(
            pos=vector(0, 0, 0), axis=vector(-5, 0, 0), radius=7)
        head = vpython.cone(
            pos=vector(0, 0, 0), axis=vector(3, 0, 0), radius=7)
        wing = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 30, 0), v2=vertex(-5, -30, 0))
        wing2 = vpython.triangle(
            v0=vertex(0, 0, 0), v1=vertex(-5, 0, 30), v2=vertex(-5, 0, -30))

        hab = vpython.compound([body, head, wing, wing2])
        hab.texture = vpython.textures.metal
        hab.axis = calc.angle_to_vpy(self._entity.heading)
        hab.radius = self._entity.r / 2
        hab.shininess = 0.1
        hab.length = self._entity.r * 2
        hab.height = self._entity.r
        hab.color = vpython.color.cyan
        old_scene.select()
        return hab
    # end of hab_object

    def __create_habitat(self, scene: vpython.canvas,
                         minimap: vpython.canvas) -> vpython.compound:
        """
                create a vpython compound object that represents our habitat.
        """
        habitat = self.hab_object(scene)
        habitat.pos = self._entity.screen_pos(self.flight_gui.origin())
        self._habitat = self._entity
        self._habitat_trail = vpython.attach_trail(habitat, retain=100)
        self._habitat_trail.stop()
        self._habitat_trail.clear()

        self._small_habitat = self.hab_object(minimap)
        self._ref_arrow = vpython.arrow(
            canvas=minimap, color=vpython.color.gray(0.5))
        self._velocity_arrow = vpython.arrow(
            canvas=minimap, color=vpython.color.red)
        habitat.texture = self._texture
        return habitat
    # end of __create_habitat

    def draw_landing_graphic(self, entity: state.Entity) -> None:
        # Habitats don't have landing graphics
        pass

    def _draw_labels(self) -> None:
        self._label = self._create_label()
        self._label.text_function = lambda entity: (
            f'{entity.name}\n'
            f'Fuel: {common.format_num(entity.fuel)} kg'
        )
        self._label.text = self._label.text_function(self._entity)
    # end of _draw_labels

    def draw(self, entity: state.Entity):
        self._update_obj(entity)
        same = self.flight_gui.reference() == entity
        default = vpython.vector(0, 0, -1)

        ref_arrow_axis = (
            entity.screen_pos(self.flight_gui.reference()).norm() *
            self._entity.r * -1.2
        )
        v = self._entity.v - self.flight_gui.reference().v
        velocity_arrow_axis = \
            vpython.vector(v[0], v[1], 0).norm() * self._entity.r

        self._ref_arrow.axis = default if same else ref_arrow_axis
        self._velocity_arrow.axis = default if same else velocity_arrow_axis
        self._small_habitat.axis = self._obj.axis
    # end of draw

    def clear_trail(self) -> None:
        self._habitat_trail.clear()

    def make_trail(self, trails: bool) -> None:
        self.clear_trail()
        if trails:
            self._habitat_trail.start()
        else:
            self._habitat_trail.stop()
# end of class Habitat

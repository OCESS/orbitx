from . import orbitx_pb2 as protos  # physics module
from pathlib import Path
from orbitx.displayable import Displayable
import vpython
import orbitx.calculator as calc
import orbitx.common as common


class Habitat(Displayable):
    def __init__(self, entity: protos.Entity, texture_path: Path,
                 scene: vpython.canvas, minimap: vpython.canvas) -> None:
        super(Habitat, self).__init__(entity, texture_path)
        self._habitat_trail = None
        self._ref_arrow = None
        self._velocity_arrow = None
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
        hab.axis = calc.ang_pos(self._entity.heading)
        hab.radius = self._entity.r / 2
        hab.shininess = 0.1
        hab.length = self._entity.r * 2
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
        habitat.pos = calc.posn(self._entity)
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

    def draw_landing_graphic(self, entity: protos.Entity) -> None:
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

    def draw(self, entity: protos.Entity):
        self._update_obj(entity)
        same = calc.reference() == calc.habitat()
        default = vpython.vector(0, 0, -1)
        ref_arrow_axis = calc.posn(
            calc.reference()).norm() * self._entity.r * 1.2
        velocity_arrow_axis = calc.unit_velocity(
            self._entity).norm() * self._entity.r

        self._ref_arrow.axis = default if same else ref_arrow_axis
        self._velocity_arrow.axis = default if same else velocity_arrow_axis
        self._small_habitat.axis = self._obj.axis
    # end of draw

    def clear_trail(self) -> None:
        self._habitat_trail.clear()
    # end of clear_trail

    def trail_option(self, stop: bool = False) -> None:
        if stop:
            self._habitat_trail.start()
        else:
            self._habitat_trail.stop()
            self._habitat_trail.clear()
# end of class Habitat

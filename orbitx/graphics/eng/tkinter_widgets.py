"""
Custom TKinter Widgets, reuseable across different Engineering views.

Every widget should inherit from Redrawable.
"""

from ABC import ABCMeta, abstractmethod
from typing import List

from orbitx.data_structures import EngineeringState


class Redrawable(metaclass=ABCMeta):
    """Inherit all custom widgets from this. Automatically registers instantiated
    objects that inherit from this, which makes life easier."""

    # Contains all instantiated Redrawables. Loop over this to redraw them all.
    all_instantiated_widgets: List['Redrawable'] = []

    @abstractmethod
    def redraw(self, state: EngineeringState) -> None:
        """Ensures that inherited classes must define a redraw function."""
        pass

    def __init_subclass__(cls, **kwargs):
        """Automatically registers an instantiated subclass."""
        super().__init_subclass__(**kwargs)
        cls.all_instantiated_widgets.append(cls)

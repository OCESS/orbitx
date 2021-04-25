"""
Custom TKinter Widgets, reuseable across different Engineering views.

Every widget should inherit from Redrawable.
"""

from abc import ABCMeta, abstractmethod
from typing import List

from orbitx.data_structures import EngineeringState


class Redrawable(metaclass=ABCMeta):
    """Inherit all custom widgets from this. Automatically registers instantiated
    objects that inherit from this, which makes life easier.

    Usage:

        class MyWidget(Redrawable):
            def __init__(self, blah, blooh, blah):
                [your widget code here]
                self._changeable_field_or_whatever = tk.StringVar()

            def redraw(self, state: EngineeringState):
                # If you forget to define this method, Python will give you an error.
                # Just an example of using a tkinter StringVar
                self._changeable_field_or_whatever.set(state.habitat_fuel)

        MyWidget(arguments)
        # That's it! main_window.py will automatically call redraw() on your widget!
    """

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

import tkinter as tk

from typing import Callable

from orbitx.graphics.eng.tkinter_style import Style
from typing import Union, Optional
from orbitx.network import Request
from orbitx import strings
from orbitx.data_structures.engineering import EngineeringState
from orbitx.programs import hab_eng


# TODO: this is too much. Just use abc.abstractmethod smh.
class EngWidget():
    """Inherit from this interface to be able to loop over all widgets calling
    widget.redraw(state)"""

    # Function takes an EngineeringState and sets various tkinter properties.
    _redraw_function: Callable[[tk.Widget, EngineeringState], None]

    def set_redrawer(self,
                     redrawer: Callable[[tk.Widget, EngineeringState], None]):
        # set_redrawer should only be called once.
        assert not hasattr(self, '_redraw_function')
        self._redraw_function = redrawer

    def redraw(self, state: EngineeringState):
        if hasattr(self, '_redraw_function'):
            self._redraw_function(self, state)
        else:
            # By default, don't change the widget. We can change this to an
            # error once we've defined redraw functions for all widgets.
            pass


class ENGLabel(tk.Label, EngWidget):
    """
    Use to display a label that also has a value, which may take a unit.
    E.g. ENGLabel(parent, text='FUEL', value=1000, unit='kg'
    """

    def __init__(self, parent: tk.Widget, text: str, value: Union[int, str],
                 unit: Optional[str] = None, style=Style('default')):
        super().__init__(parent)
        self.text = text
        self.value = value
        self.unit = unit

        self.configure(anchor=tk.W, justify=tk.LEFT)

        self.update_value()
        self.update_style(style)

    def text_decorator(self) -> str:
        if self.unit is not None:
            return self.text + ' ' + str(self.value) + ' ' + self.unit
        else:
            return self.text + ' ' + str(self.value)

    def update_value(self):
        self.configure(text=self.text_decorator())

    def update_style(self, style):
        self.configure(bg=style.bg,
                       fg=style.text,
                       font=style.normal)


class ENGLabelFrame(tk.LabelFrame, EngWidget):
    """A subdivision of the GUI using ENG styling.
    E.g. master = ENGLabelFrame(parent, text='Master Control')
    """

    def __init__(self, parent: tk.Widget, text: str, style=Style('default')):
        font = style.normal
        super().__init__(parent, text=text, font=font, fg=style.text, bg=style.bg)


class ENGScale(tk.Scale, EngWidget):
    """A slider."""

    def __init__(self, parent, label: ENGLabel, style=Style('default')):
        super().__init__(parent)

        self.label = label

        self.configure(from_=0,
                       to_=100,
                       resolution=5,
                       orient=tk.HORIZONTAL,
                       bg=style.bg,
                       fg=style.text,
                       troughcolor=style.bg,
                       showvalue=0,
                       command=self.update_slider_label
                       )

    def update_slider_label(self, val):
        self.label.value = val
        self.label.update_value()
        print(self.label.value)


class Indicator(tk.Button, EngWidget):
    """
    Represents an indicator light/toggle push-button switch.
    E.g. radar = Indicator(parent, v, text='RAD')
    """

    def __init__(self, parent: tk.Widget, style=Style('default'),
                 command_on_press: Request = None, command_on_unpress: Request = None,
                 *args, **kwargs):
        """
        parent: The tkinter widget under which this Indicator is grouped
        style: an optional style override, e.g. cw.Style('flat')
        command_on_press: a network.Request that will be sent to the physics server when this Indicator is activated
        command_on_unpress: as above, but when this Indicator is unpressed (defaults to the value of command_on_press)
        """
        super().__init__(parent, *args, **kwargs)

        # Allows for button width, height to be specified in px
        self.px_img = tk.PhotoImage(width=1, height=1)

        self.configure(image=self.px_img,
                       compound='c',
                       width=50,
                       height=50,
                       command=self.on_press,
                       font=style.normal,
                       )

        self.style = style
        self.pressed = False

        self._command_on_press = command_on_press
        if command_on_unpress is None:
            self._command_on_unpress = command_on_press

        self.invoke()

    def on_press(self):
        if self.pressed and self._command_on_press is not None:
            hab_eng.push_command(self._command_on_press)
        elif self._command_on_unpress is not None:
            hab_eng.push_command(self._command_on_unpress)

    def update(self, pressed):
        self.pressed = pressed
        if self.pressed:
            self.configure(relief=tk.SUNKEN, bg=self.style.ind_off)
        else:
            self.configure(relief=tk.RAISED, bg=self.style.ind_on)


class OneTimeButton(tk.Button, EngWidget):
    """
    A button, which can only be pressed once.
    """

    def __init__(self, parent, style=Style('default'), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Allows for button width, height to be specified in px
        self.px_img = tk.PhotoImage(width=1, height=1)

        self.configure(image=self.px_img,
                       compound='c',
                       width=100,
                       height=40,
                       font=style.normal,
                       relief=tk.RIDGE,
                       bg=style.otb_unused,
                       command=self.press
                       )
        self.bind('<Button-1>', lambda x: self.press())

        self.value = 0
        self.style = style

    def press(self):
        self.value = 1
        self.configure(state=tk.DISABLED,
                       relief=tk.FLAT,
                       bg=self.style.otb_used,
                       fg=self.style.otb_unused
                       )


class Alert(tk.Button, EngWidget):
    """
    Stays flat and gray until alerted. Then it flashes, until clicked.
    When clicked, the button should be flat, deactivated, and red, and
    stop flashing, but stay red until the issue causing the alert is cleared.

    Optional invisible tag sets the text to the same colour as the background.
    """

    def __init__(self, parent, invis: bool = False, counter: int = None,
                 style=Style('default'), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.style = style

        # Allows for button width, height to be specified in px
        self.px_img = tk.PhotoImage(width=1, height=1)
        self.configure(image=self.px_img,
                       compound='c',
                       width=80,
                       height=35,
                       font=style.normal,
                       state=tk.DISABLED,
                       command=self.quiet
                       )
        self.alerted = 0
        self.normal_state()

        # Invis doesn't seem to work?
        if invis:
            self.configure(disabledforeground=self.style.bg)

        if counter is not None:
            self.counter = counter

        # Duty Cycle = 0.8 means activated for 80% of the period
        self.flash_period = 450    # ms
        self.duty_cycle = 0.7

    def alert(self):
        self.alerted = 1
        # print('ALERT')
        self.alerted_state()

    def alerted_state(self):
        # print('Alerted State')
        self.configure(relief=tk.RAISED,
                       bg=self.style.alert_bg,
                       fg=self.style.alert_text,
                       state=tk.NORMAL)
        if self.alerted:
            self.event = self.after(int(self.duty_cycle * self.flash_period),
                                    lambda: self.normal_state())

    def normal_state(self):
        # print('Normal State', self.value==True)
        self.configure(relief=tk.FLAT,
                       bg=self.style.bg,
                       fg=self.style.text
                       )
        if self.alerted:
            self.event = self.after(int((1-self.duty_cycle)*self.flash_period),
                                    lambda: self.alerted_state())

    def quiet(self):
        # Stop flashing, but stay alerted
        self.after_cancel(self.event)
        self.alerted = False
        self.alerted_state()
        self.configure(state=tk.DISABLED, relief=tk.GROOVE)

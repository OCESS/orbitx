import tkinter as tk
from orbitx.graphics.eng.tkinter_style import Style
from typing import Union, Optional


class ENGLabel(tk.Label):
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


class ENGLabelFrame(tk.LabelFrame):
    """A subdivision of the GUI using ENG styling.
    E.g. master = ENGLabelFrame(parent, text='Master Control')
    """

    def __init__(self, parent: tk.Widget, text: str, style=Style('default')):
        font = style.normal
        super().__init__(parent, text=text, font=font, fg=style.text, bg=style.bg)


class Indicator(tk.Button):
    """
    Represents an indicator light/toggle push-button switch.
    E.g. radar = Indicator(parent, text='RAD')
    """

    def __init__(self, parent, style=Style('default'), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Allows for button width, height to be specified in px
        self.px_img = tk.PhotoImage(width=1, height=1)

        self.configure(image=self.px_img,
                       compound='c',
                       width=50,
                       height=50,
                       command=self.press,
                       font=style.normal
                       )

        self.style = style
        self.value = 1    # Will be set to 0, on next line
        self.invoke()

    def press(self):
        if self.value == 0:
            self.value = 1
            self.configure(relief=tk.RAISED, bg=self.style.ind_on)
        else:
            self.value = 0
            self.configure(relief=tk.SUNKEN, bg=self.style.ind_off)


class OneTimeButton(tk.Button):
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


class Alert(tk.Button):
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


class ENGScale(tk.Scale):
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
        self.label.update()

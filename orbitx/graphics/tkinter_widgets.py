import tkinter as tk
from typing import Union, Optional

STYLE_DEFAULT = 'default'
STYLE_FLAT = 'flat'


class Style:

    def __init__(self, style='default'):
        if style == 'flat':
            self.flat()
        else:
            self.default()

    def default(self):
        self.bg = '#1a1a1a'
        self.text = '#4d4dff'

        # Buttons
        self.ind_off = '#b3b3b3'  # Indicator inactive
        self.ind_on = '#009933'  # Indicator active
        self.otb_unused = self.ind_off
        self.otb_used = '#4d4d4d'  # OneTimeButton, used

        # Alerts
        self.alert_bg = '#cc0000'  # Alert flash
        self.alert_text = '#d9d9d9'  # Alert flash text

        # Electrical Grid
        self.sw_off = '#4d4d4d'
        self.sw_on = '#e0dc11'
        self.temp_nom = '#45e011'
        self.temp_med = '#e09411'
        self.temp_hi = '#e01c11'

        # Fonts
        self.large = ('Arial', 14)
        self.normal = ('Arial', 12)
        self.small = ('Arial', 10)

    def flat(self):
        # https://flatuicolors.com/palette/defo

        self.bg = '#2c3e50'    # Midnight Blue
        self.text = '#bdc3c7'   # Sliver

        # Buttons
        self.ind_off = '#bdc3c7'  # Indicator inactive; Silver
        self.ind_on = '#27ae60'  # Indicator active; Nephritis
        self.otb_unused = '#bdc3c7'    # Silver
        self.otb_used = '#7f8c8d'  # OneTimeButton, used; Asbestos

        # Alerts
        self.alert_bg = '#c0392b'  # Alert flash; Pomegranate
        self.alert_text = '#ecf0f1'  # Alert flash text; Clouds

        # Electrical Grid
        self.sw_off = '#34495e'    # Wet Asphalt
        self.sw_on = '#f1c40f'    # Sunflower
        self.temp_nom = '#16a085'   # Green Sea
        self.temp_med = '#e67e22'   # Carrot
        self.temp_hi = '#e74c3c'    # Alizarin

        # Fonts
        self.large = ('Arial', 14)
        self.normal = ('Arial', 12)
        self.small = ('Arial', 10)


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

    def press(self, style=Style('default')):
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

    def __init__(self, parent, command=None, style=Style('default'), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Allows for button width, height to be specified in px
        self.px_img = tk.PhotoImage(width=1, height=1)

        self.configure(image=self.px_img,
                       compound='c',
                       width=100,
                       height=40,
                       font=style.normal,
                       relief=tk.RIDGE,
                       bg=style.otb_unused
                       )

        self.value = 0

    def update_style(self, style=Style('default')):
        self.configure(state=tk.DISABLED,
                       relief=tk.FLAT,
                       bg=style.otb_used,
                       fg=style.otb_unused
                       )


class Alert(tk.Button):
    """
    Stays flat and gray until alerted. Then it flashes, until clicked.
    When clicked, the button should be flat, deactivated, and red, and
    stop flashing, but stay red until the issue causing the alert is cleared.

    Optional invisible tag sets the text to the same colour as the background.

    TODO Invisible doesn't work
    TODO Sometimes, when you quiet the alert, it goes back to normal_state
    save the id of the after call id=after()
    then after_cancel(id)
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

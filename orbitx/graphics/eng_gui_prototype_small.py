# This is a small tkinter app that showcases all of the widgets
# from tkinter_widgets.py

import tkinter as tk
import orbitx.graphics.tkinter_widgets as cw

# Main widget dictionary holds all objects in the gui
widgets = {}

# Python garbage collection deletes ImageTk images, unless you save them
images = {}

style = cw.Style('flat')


class MainApplication(tk.Tk):
    """The main application window in which lives the HabPage, and potentially
    other future pages.
    Creates the file menu
    """

    def __init__(self):
        super().__init__()

        tk.Tk.wm_title(self, "tkinter widget demo")
        self.geometry("400x300")

        # Initialise main page
        self.page = HabPage(self)
        self.page.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


class HabPage(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=style.bg)

        frame = cw.ENGLabelFrame(self, text="Frame", style=style)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # A couple of alarms
        widgets['a_asteroid'] = cw.Alert(frame, text='ASTEROID', style=style)
        widgets['a_radiation'] = cw.Alert(frame, text='RADIATION', style=style)

        # A couple of IndicatorButtons
        widgets['INS'] = cw.Indicator(frame, text='INS', style=style)
        widgets['LOS'] = cw.Indicator(frame, text='RAD', style=style)

        # A couple of OneTimeButtons
        widgets['SRB'] = cw.OneTimeButton(frame, text='SRB', style=style)
        widgets['CHUTE'] = cw.OneTimeButton(frame, text='CHUTE', style=style)

        # A couple of labels
        widgets['habr_temp'] = cw.ENGLabel(frame, text='TEMP',
                                           value=0, unit='℃',    # U+2103
                                           style=style)
        widgets['cl1_pump'] = cw.ENGLabel(frame, text='PUMP',
                                           value=0, unit='%', style=style)

        # Display label
        widgets['event_display'] = tk.Label(frame, text='Waiting',
                                            bg=style.bg, fg=style.text,
                                            font=style.large)

        # Place widgets in the grid
        widgets['a_asteroid'].grid(row=0, column=0, padx=5, pady=5)
        widgets['a_radiation'].grid(row=1, column=0, padx=5, pady=5)
        widgets['INS'].grid(row=0, column=1, padx=5, pady=5)
        widgets['LOS'].grid(row=1, column=1, padx=5, pady=5)
        widgets['SRB'].grid(row=0, column=2, padx=5, pady=5)
        widgets['CHUTE'].grid(row=1, column=2, padx=5, pady=5)
        widgets['habr_temp'].grid(row=0, column=3, padx=5, pady=5)
        widgets['cl1_pump'].grid(row=1, column=3, padx=5, pady=5)
        widgets['event_display'].grid(row=3, column=0, padx=5, pady=40,
                                      columnspan=4)

        # Keybindings
        def keybinds(event):
            print('HANDLER!')
            event_params = (event.type, event.widget, event.x, event.y,
                            event.x_root, event.y_root, event.char,
                            event.keysym, event.keycode)
            event_str = ' '.join(event_params)
            print(event_str)
            widgets['event_display'].configure(text=event_str)

        widgets['INS'].bind_all('<Key>', lambda e: keybinds(e))
        widgets['event_display'].bind('<Button-1>', lambda e: keybinds(e))
        widgets['SRB'].bind_all('s', lambda e: widgets['SRB'].invoke())


# MAIN
app = MainApplication()    # Essential. Do not remove.
widgets['a_asteroid'].alert()
app.mainloop()    # Essential. Do not remove.

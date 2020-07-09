import tkinter as tk
import orbitx.graphics.tkinter_widgets as cw
from PIL import Image, ImageTk


# Main widget dictionary holds all objects in the gui
widgets = {}

# Python garbage collection deletes ImageTk images, unless you save them
images = {}

# Radiator States
ISOLATED = 'ISOL'
BROKEN = 'BRKN'
STOWED = 'STWD'
LOOP1 = 'HLP1'
LOOP2 = 'HLP2'
LOOP3 = 'ALP3'
BOTH = 'BOTH'


class MainApplication(tk.Tk):
    """The main application window in which lives the HabPage, and potentially
    other future pages.
    Creates the file menu
    """

    def __init__(self):
        super().__init__()

        tk.Tk.wm_title(self, "OrbitX Engineering")
        self.geometry("1000x900")

        # Create menubar
        menubar = self._create_menu()
        tk.Tk.config(self, menu=menubar)

        # Initialise main page
        self.page = HabPage(self)
        self.page.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def _create_menu(self):
        menubar = tk.Menu(self)

        file = tk.Menu(menubar, tearoff=0)
        # file.add_command(label="Item1")
        file.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=file)

        return menubar


class HabPage(tk.Frame):
    """1. Create a page in which lives all of the HabPage GUI
    2. Divide the page into a left and right pane. The right
    pane is divided into top, middle, bottom
    3. Create and render everything in each of the panes.
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Divide the page into two columns
        self.left_frame = tk.Frame(self, bg=cw.BLACK)

        # If Red, Blue, Yellow, or Gray are showing through
        # something has gone wrong
        right_frame = tk.Frame(self, bg="red")
        self.right_frame_top = tk.Frame(right_frame, bg="blue")
        self.right_frame_mid = tk.Frame(right_frame, bg="yellow")
        self.right_frame_bot = tk.Frame(right_frame, bg="gray")

        # Pack the two columns
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.right_frame_mid.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.right_frame_bot.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.left_frame.pack_configure()

        # Add objects to the columns
        self._render_left()
        self._render_right_top()
        self._render_right_mid()
        self._render_right_bot()

    def _render_left(self):
        # Master
        master = cw.ENGLabelFrame(self.left_frame, text="Master")
        master.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['master_freeze'] = cw.Indicator(master,
                                                text='Freeze\nControls')
        widgets['master_freeze'].configure(width=60, height=60)

        widgets['a_master'] = cw.Alert(master, text='MASTER\nALARM',
                                       font=cw.LARGE_FONT)
        widgets['a_master'].configure(width=100, height=100)

        widgets['a_asteroid'] = cw.Alert(master, text='ASTEROID')
        widgets['a_radiation'] = cw.Alert(master, text='RADIATION')
        widgets['a_hab_gnomes'] = cw.Alert(master, text='HAB\nGNOMES')

        widgets['master_freeze'].grid(row=0, column=0)
        widgets['a_master'].grid(row=0, column=1, rowspan=2)
        widgets['a_asteroid'].grid(row=2, column=0, padx=5, pady=5)
        widgets['a_radiation'].grid(row=2, column=1, padx=5, pady=5)
        widgets['a_hab_gnomes'].grid(row=3, column=0, pady=5)

        # Engines
        engines = cw.ENGLabelFrame(self.left_frame, text="Engines")
        engines.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['h_INJ1'] = cw.Indicator(engines, text="INJ-1")
        widgets['h_INJ2'] = cw.Indicator(engines, text="INJ-2")
        widgets["fuel"] = cw.ENGLabel(engines, text='FUEL', value=0, unit='kg')
        widgets['h_br'] = cw.ENGLabel(engines, text='BURN RATE',
                                      value=0, unit='kg/hr')

        widgets['h_INJ1'].grid(row=0, column=0)
        widgets['h_INJ2'].grid(row=1, column=0)
        widgets['fuel'].grid(row=0, column=1, sticky=tk.W)
        widgets['h_br'].grid(row=1, column=1, sticky=tk.W)

        # Engines > Fuel Management

        fuelmanager = cw.ENGLabelFrame(engines, text="")
        fuelmanager.grid(row=2, column=0, columnspan=2, pady=5)

        widgets['a_fuel_connected'] = cw.Alert(fuelmanager, text='TETHERED')
        widgets['h_load'] = cw.Indicator(fuelmanager, text="LOAD")
        widgets['h_dump'] = cw.Indicator(fuelmanager, text="DUMP")

        widgets['a_fuel_connected'].grid(row=0, column=0, padx=10)
        widgets['h_dump'].grid(row=0, column=1)
        widgets['h_load'].grid(row=0, column=2)

        # Subsystems
        subsystems = tk.LabelFrame(
            self.left_frame, text="Subsystems",
            bg=cw.BLACK, fg=cw.BLUE, font=cw.NORMAL_FONT)
        subsystems.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['INS'] = cw.Indicator(subsystems, text='INS')
        widgets['RADAR'] = cw.Indicator(subsystems, text='RAD')
        widgets['LOS'] = cw.Indicator(subsystems, text='LOS')
        widgets['GNC'] = cw.Indicator(subsystems, text='GNC')
        widgets['a_ATMO'] = cw.Alert(subsystems, text='IN ATMO')
        widgets['CHUTE'] = cw.OneTimeButton(subsystems, text='CHUTE')
        widgets['a_SRBTIME'] = cw.Alert(subsystems, text='120s', invis=True)
        widgets['SRB'] = cw.OneTimeButton(subsystems, text='SRB')

        widgets['INS'].grid(row=0, column=0)
        widgets['RADAR'].grid(row=1, column=0)
        widgets['LOS'].grid(row=2, column=0)
        widgets['GNC'].grid(row=3, column=0)
        widgets['a_ATMO'].grid(row=0, column=1)
        widgets['CHUTE'].grid(row=1, column=1)
        widgets['SRB'].grid(row=2, column=1)
        widgets['a_SRBTIME'].grid(row=3, column=1)

        subsystems.grid_columnconfigure(0, weight=1, minsize=50)
        subsystems.grid_columnconfigure(1, weight=1, minsize=60)

    def _render_right_top(self):
#        # Electrical Grid
#        hegrid = cw.ENGLabelFrame(self.right_frame_top,
#                                  text="Habitat Electrical Grid")
#        hegrid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
#        widgets['he_grid'] = tk.Canvas(hegrid, width=750, height=350)
#        widgets['he_grid'].pack()

        # Method 1
        # Draw all objects on a canvas including the switches
        method1 = cw.ENGLabelFrame(self.right_frame_top,
                                  text="Method 1")
        method1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        widgets['m1_he_grid'] = tk.Canvas(method1, width=375, height=350)
        widgets['m1_he_grid'].pack(padx=5, pady=5)

        # Method 2
        # Draw the unactive parts as an image, and superimpose buttons
        # and labels
        method2 = cw.ENGLabelFrame(self.right_frame_top,
                                  text="Method 2")
        method2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        images['ECS_bg'] = ImageTk.PhotoImage(Image.open(
            "../../data/textures/eng_mockup.PNG").resize((375, 95)))
        widgets['m2_he_grid'] = tk.Label(method2, image=images['ECS_bg'],
                                         width=375, height=95)
        widgets['m2_he_grid'].pack(padx=5, pady=5)

        sw_width = 15
        sw_height = 23
        images['sw_open'] = ImageTk.PhotoImage(Image.open(
            "../../data/textures/eng_switch_open.PNG").resize((sw_width, sw_height)))

        images['sw_closed'] = ImageTk.PhotoImage(Image.open(
            "../../data/textures/eng_switch_closed.PNG").resize((sw_width, sw_height)))

        def switch(event):
            event.widget.configure(image=images['sw_closed'])

        widgets['sw_ln1'] = tk.Button(widgets['m2_he_grid'],
                                      width=sw_width, height=sw_height,
                                      image=images['sw_open'],
                                      relief=tk.FLAT,
                                      bd=0,
                                      bg=cw.BLACK)
        widgets['sw_ln1'].place(x=125, y=35)

        widgets['sw_ln1'].bind('<Button-1>', switch)
        widgets['sw_ln1'].bind_all('a', switch)

        def get_pos(event):
            position_display.configure(
                text='x = ' + str(event.x) + '  '
                     'y = ' + str(event.y))

        widgets['m2_he_grid'].bind('<Button-1>', get_pos)

        position_display = tk.Label(method2)
        position_display.pack()

    def _render_right_mid(self):
        # Coolant Loops
        loops = cw.ENGLabelFrame(self.right_frame_mid, text="")
        loops.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for cl in range(2):
            prefix = 'hl{}_'.format(cl+1)
            loop = cw.ENGLabelFrame(loops, text='Coolant Loop {}'.format(cl+1))
            loop.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            widgets[prefix + 'pump'] = cw.ENGLabel(loop, text='PUMP',
                                                   value=96, unit='%')
            widgets[prefix + 'pump_sldr'] = cw.ENGScale(
                loop, widgets[prefix + 'pump'])
            widgets[prefix + 'temp'] = cw.ENGLabel(
                loop, text='TEMP', value=47, unit='*C')

            widgets[prefix + 'pump'].grid(row=0, column=0)
            widgets[prefix + 'pump_sldr'].grid(row=0, column=1,
                                               rowspan=2, columnspan=2)
            widgets[prefix + 'temp'].grid(row=1, column=0, pady=5)

            for i in range(2):
                for j in range(3):
                    rad = 'R{}'.format(i * 3 + j + 1)
                    widgets[prefix + rad] = cw.Indicator(loop, text=rad)
                    widgets[prefix + rad].grid(row=i+2, column=j, sticky=tk.E)

        # Radiators
        radiators = cw.ENGLabelFrame(self.right_frame_mid, text="Radiators")
        radiators.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        for i in range(6):
            rad = 'R{}'.format(i+1)

            widgets['r_' + rad + '_isol'] = tk.Button(
                radiators, text=ISOLATED, width=10, bg=cw.GRAY,
                command=lambda v=(i+1): rad_isol(v))
            if i < 3:
                widgets['r_' + rad] = cw.ENGLabel(
                    radiators, text=rad, value=STOWED)
                widgets['r_' + rad + '_stow'] = tk.Button(
                    radiators, text=STOWED, width=10, bg=cw.GRAY,
                    command=lambda v=(i+1): rad_stow(v))
            else:
                widgets['r_' + rad] = cw.ENGLabel(radiators,
                                                  text=rad, value=ISOLATED)

            widgets['r_' + rad].grid(row=i, column=0, padx=15)
            widgets['r_' + rad + '_isol'].grid(row=i, column=1, padx=5, pady=5)
            if i < 3:
                widgets['r_' + rad + '_stow'].grid(row=i, column=2, padx=5)

        all_buttons = cw.ENGLabelFrame(radiators, text='')
        all_buttons.grid(row=3, column=2, rowspan=3, ipadx=5, ipady=5)

        widgets['r_stow_all'] = tk.Button(
            all_buttons, text='STOW-A', width=8, height=2, bg=cw.GRAY,
            command=lambda: [rad_stow(v+1) for v in range(3)])
        widgets['r_isol_all'] = tk.Button(
            all_buttons, text='ISOL-A', width=8, height=2, bg=cw.GRAY,
            command=lambda: [rad_isol(v+1) for v in range(6)])

        widgets['r_stow_all'].pack(pady=5)
        widgets['r_isol_all'].pack()

        def rad_isol(v):
            if widgets['r_R{}'.format(v)] != BROKEN:
                widgets['r_R{}'.format(v)].value = ISOLATED
                widgets['r_R{}'.format(v)].update()
                for m in [1, 2]:
                    widgets['hl{}_R{}'.format(m, v)].value = 1
                    widgets['hl{}_R{}'.format(m, v)].press()
            else:
                pass

        def rad_stow(v):
            if widgets['r_R{}'.format(v)] != BROKEN:
                widgets['r_R{}'.format(v)].value = STOWED
                widgets['r_R{}'.format(v)].update()
                for m in [1, 2]:
                    widgets['hl{}_R{}'.format(m, v)].value = 1
                    widgets['hl{}_R{}'.format(m, v)].press()
            else:
                pass

    def _render_right_bot(self):
        # Hab Reactor
        hreactor = cw.ENGLabelFrame(self.right_frame_bot,
                                    text="Habitat Reactor")
        hreactor.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        widgets['hr_INJ-1'] = cw.Indicator(hreactor, text="R-INJ-1")
        widgets['hr_INJ-2'] = cw.Indicator(hreactor, text="R-INJ-2")
        widgets['hr_heater'] = cw.Indicator(hreactor, text="HEAT")
        widgets["hr_curr"] = cw.ENGLabel(hreactor, text='CURR',
                                         value=0, unit='A')
        widgets['hr_temp'] = cw.ENGLabel(hreactor, text='TEMP',
                                         value=81, unit='*C')
        widgets['a_hr_overtemp'] = cw.Alert(hreactor, text="OVERTEMP")

        widgets['hr_INJ-1'].grid(row=0, column=0, padx=10)
        widgets['hr_INJ-2'].grid(row=1, column=0)
        widgets['hr_heater'].grid(row=2, column=0)
        widgets["hr_curr"].grid(row=0, column=1, sticky=tk.W)
        widgets['hr_temp'].grid(row=1, column=1, sticky=tk.W)
        widgets['a_hr_overtemp'].grid(row=2, column=1)

        graph_frame = tk.Frame(hreactor)
        graph_width = 400
        widgets['hr_graph'] = tk.Canvas(graph_frame,
                                        width=graph_width, height=200)
        graph_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
        widgets['hr_graph'].pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        hreactor.grid_columnconfigure(0, weight=1, minsize=60)
        hreactor.grid_columnconfigure(1, weight=1, minsize=70)
        hreactor.grid_columnconfigure(2, weight=3, minsize=graph_width)

        hrconfinement = cw.ENGLabelFrame(self.right_frame_bot,
                                         text="Reactor Confinement")
        hrconfinement.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        widgets['hr_RCON-1'] = cw.Indicator(hrconfinement, text="RCON-1")
        widgets['hr_RCON-2'] = cw.Indicator(hrconfinement, text="RCON-2")
        widgets["hr_RCON-1_temp"] = cw.ENGLabel(hrconfinement, text='TEMP',
                                                value=84, unit='*C')
        widgets['hr_RCON-2_temp'] = cw.ENGLabel(hrconfinement, text='TEMP',
                                                value=80, unit='*C')
        widgets['hr_BATT'] = cw.ENGLabel(hrconfinement, text='BATT',
                                         value=2000, unit='As')
        widgets['a_hr_lowBatt'] = cw.Alert(hrconfinement, text='LOW BATT')

        widgets['hr_RCON-1'].grid(row=0, column=0)
        widgets['hr_RCON-2'].grid(row=1, column=0)
        widgets["hr_RCON-1_temp"].grid(row=0, column=1)
        widgets['hr_RCON-2_temp'].grid(row=1, column=1)
        widgets['hr_BATT'].grid(row=2, column=0, columnspan=2, pady=10)
        widgets['a_hr_lowBatt'].grid(row=3, column=0, columnspan=2)

        hrconfinement.grid_columnconfigure(0, weight=1, minsize=60)
        hrconfinement.grid_columnconfigure(1, weight=1, minsize=70)


# MAIN LOOP
app = MainApplication()    # Essential. Do not remove.

# Testing
#widgets['a_ATMO'].after(1200, widgets['a_ATMO'].alert())
#widgets['a_master'].alert()
#widgets['a_hab_gnomes'].alert()
# /Testing

app.mainloop()    # Essential. Do not remove.

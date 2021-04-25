import tkinter as tk
import tkinter.ttk
import orbitx.graphics.eng.deprecated_tkinter_widgets as cw
from orbitx.graphics.eng.coolant_window import coolantPage
from orbitx.graphics.eng.grid_window import GridPage
from orbitx.data_structures import PhysicsState
from orbitx.network import Request
from PIL import Image, ImageTk
from orbitx import strings

DIMENSIONS = "1280x1024"

# Main widget dictionary holds all objects in the gui
widgets = {}

# Python garbage collection deletes ImageTk images, unless you save them
images = {}

# Gavin's testing variables
testing = [0]*12
slider_values = [0]*2
pump_value = 0*[2]

# Radiator States
ISOLATED = 'ISOL'
BROKEN = 'BRKN'
STOWED = 'STWD'
LOOP1 = 'HLP1'
LOOP2 = 'HLP2'
LOOP3 = 'ALP3'
BOTH = 'BOTH'

style = cw.Style('flat')


class MainApplication(tk.Tk):
    """The main application window in which lives the HabPage, and potentially
    other future pages.
    """

    def __init__(self):
        super().__init__()

        tk.Tk.wm_title(self, "OrbitX Engineering")
        self.geometry(DIMENSIONS)

        # Create tabbed view
        self._tab_control = tk.ttk.Notebook(self)

        # Initialise main page
        self._main_tab = HabPage(self._tab_control)
        self._coolant_tab = coolantPage(self._tab_control)
        self._tab_control.add(self._main_tab, text='Main tab')

        # Add coolant tab
        self._coolant_tab = coolantPage(self._tab_control)
        self._tab_control.add(self._coolant_tab, text='Coolant tab')

        # Initialise electrical grid page
        self._grid_tab = GridPage(self._tab_control)
        self._tab_control.add(self._grid_tab, text='Electrical Grid')

        self._tab_control.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        # Testing
        widgets['a_ATMO'].after(1200, widgets['a_ATMO'].alert())
        widgets['a_master'].alert()
        widgets['a_hab_gnomes'].alert()
        # /Testing
        self._main_tab.update()
        print(self._main_tab.winfo_width(), self._main_tab.winfo_height())

    def redraw(self, state: PhysicsState):
        engineering = state.engineering
        for widget in widgets.values():
            widget.redraw(engineering)
        self._grid_tab.blah.redraw(engineering)  # TODO: replace with a general solution for grid widgets
        self._grid_tab.blooh.redraw(engineering)

    def _create_menu(self):
        menubar = tk.Menu(self)

        file = tk.Menu(menubar, tearoff=0)
        # file.add_command(label="Item1")
        file.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=file)

        return menubar

class coolantPage(tk.Frame):
    """
    An alternate tab for coolants and radiators
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.left_frame = tk.Frame(self, bg=style.bg)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_frame.pack_configure()
        self._render_coolants()
        self._render_radiators()

    def _render_coolants(self):

        loops = cw.ENGLabelFrame(self.left_frame, text="", style=style)
        loops.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for cl in range(2):
            prefix = 'hl{}_'.format(cl + 1)
            loop = cw.ENGLabelFrame(loops, text='Coolant Loop {}'.format(cl + 1),
                                    style=style)
            loop.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            widgets[prefix + 'pump'] = cw.ENGLabel(loop, text='PUMP',
                                                   value=0, unit='%',
                                                   style=style)
            widgets[prefix + 'pump_sldr'] = cw.ENGScale(
                loop, widgets[prefix + 'pump'], style=style)

            widgets[prefix + 'temp'] = cw.ENGLabel(
                loop, text='TEMP', value=47, unit='*C', style=style)

            widgets[prefix + 'pump'].grid(row=0, column=0)
            widgets[prefix + 'pump_sldr'].grid(row=0, column=1,
                                               rowspan=2, columnspan=2)
            widgets[prefix + 'temp'].grid(row=1, column=0, pady=5)

            for i in range(2):
                for j in range(3):
                    indicator_num = i * 3 + j + 1
                    rad_label = f'R{indicator_num}'

                    widgets[prefix + rad_label] = cw.Indicator(
                        loop, text=rad_label, style=style,
                        command_on_press=Request(ident=Request.TOGGLE_RADIATOR,
                                                 radiator_to_toggle=indicator_num - 1))
                    widgets[prefix + rad_label].grid(row=i + 2, column=j, sticky=tk.E)
                    widgets[prefix + rad_label].set_redrawer(
                        lambda widget, state, n=indicator_num: widget.update(
                            state.radiators[n - 1].functioning
                        ))

    def _render_radiators(self):

        radiators = cw.ENGLabelFrame(self.left_frame, text="Radiators",
                                     style=style)
        radiators.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        for i in range(6):
            rad = 'R{}'.format(i + 1)

            widgets['r_' + rad + '_isol'] = cw.Indicator(
                radiators, text=ISOLATED, width=10, bg=style.ind_off,
                command=lambda v=(i + 1): rad_isol(v))
            if i < 3:
                widgets['r_' + rad] = cw.ENGLabel(
                    radiators, text=rad, value=STOWED, style=style)
                widgets['r_' + rad + '_stow'] = cw.Indicator(
                    radiators, text=STOWED, width=10, bg=style.ind_off,
                    command=lambda v=(i + 1): rad_stow(v))
            else:
                widgets['r_' + rad] = cw.ENGLabel(radiators,
                                                  text=rad, value=ISOLATED,
                                                  style=style)

            widgets['r_' + rad].grid(row=i, column=0, padx=15)
            widgets['r_' + rad + '_isol'].grid(row=i % 3, column=int(1 + i / 3), padx=5, pady=5)
            if i < 3:
                widgets['r_' + rad + '_stow'].grid(row=i, column=3, padx=5)

        all_buttons = cw.ENGLabelFrame(radiators, text='', style=style)
        all_buttons.grid(row=3, column=2, rowspan=3, ipadx=5, ipady=5)

        #        widgets['r_stow_all'] = tk.Button(
        #            all_buttons, text='STOW-A', width=8, height=2, bg=style.ind_off,
        #            command=lambda: [rad_stow(v+1) for v in range(3)])
        #        widgets['r_isol_all'] = tk.Button(
        #            all_buttons, text='ISOL-A', width=8, height=2, bg=style.ind_off,
        #            command=lambda: [rad_isol(v+1) for v in range(6)])
        #
        #        widgets['r_stow_all'].pack(pady=5)
        #        widgets['r_isol_all'].pack()

        def rad_isol(v):
            # TODO: move this code to the physics server, where it belongs.
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


class coolantPage(tk.Frame):
    """
    An alternate tab for coolants and radiators
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.left_frame = tk.Frame(self, bg=style.bg)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_frame.pack_configure()
        self._render_coolants()
        self._render_radiators()

    def _render_coolants(self):

        loops = cw.ENGLabelFrame(self.left_frame, text="", style=style)
        loops.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for cl in range(2):
            prefix = 'hl{}_'.format(cl + 1)
            loop = cw.ENGLabelFrame(loops, text='Coolant Loop {}'.format(cl + 1),
                                    style=style)
            loop.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            widgets[prefix + 'pump'] = cw.ENGLabel(loop, text='PUMP',
                                                   value=0, unit='%',
                                                   style=style)
            widgets[prefix + 'pump_sldr'] = cw.ENGScale(
                loop, widgets[prefix + 'pump'], style=style)

            widgets[prefix + 'temp'] = cw.ENGLabel(
                loop, text='TEMP', value=47, unit='*C', style=style)

            widgets[prefix + 'pump'].grid(row=0, column=0)
            widgets[prefix + 'pump_sldr'].grid(row=0, column=1,
                                               rowspan=2, columnspan=2)
            widgets[prefix + 'temp'].grid(row=1, column=0, pady=5)

            for i in range(2):
                for j in range(3):
                    indicator_num = i * 3 + j + 1
                    rad_label = f'R{indicator_num}'

                    widgets[prefix + rad_label] = cw.Indicator(
                        loop, text=rad_label, style=style,
                        command_on_press=Request(ident=Request.TOGGLE_RADIATOR,
                                                 radiator_to_toggle=indicator_num - 1))
                    widgets[prefix + rad_label].grid(row=i + 2, column=j, sticky=tk.E)
                    widgets[prefix + rad_label].set_redrawer(
                        lambda widget, state, n=indicator_num: widget.update(
                            state.radiators[n - 1].functioning
                        ))

    def _render_radiators(self):

        radiators = cw.ENGLabelFrame(self.left_frame, text="Radiators",
                                     style=style)
        radiators.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        for i in range(6):
            rad = 'R{}'.format(i + 1)

            widgets['r_' + rad + '_isol'] = cw.Indicator(
                radiators, text=ISOLATED, width=10, bg=style.ind_off,
                command=lambda v=(i + 1): rad_isol(v))
            if i < 3:
                widgets['r_' + rad] = cw.ENGLabel(
                    radiators, text=rad, value=STOWED, style=style)
                widgets['r_' + rad + '_stow'] = cw.Indicator(
                    radiators, text=STOWED, width=10, bg=style.ind_off,
                    command=lambda v=(i + 1): rad_stow(v))
            else:
                widgets['r_' + rad] = cw.ENGLabel(radiators,
                                                  text=rad, value=ISOLATED,
                                                  style=style)

            widgets['r_' + rad].grid(row=i, column=0, padx=15)
            widgets['r_' + rad + '_isol'].grid(row=i % 3, column=int(1 + i / 3), padx=5, pady=5)
            if i < 3:
                widgets['r_' + rad + '_stow'].grid(row=i, column=3, padx=5)

        all_buttons = cw.ENGLabelFrame(radiators, text='', style=style)
        all_buttons.grid(row=3, column=2, rowspan=3, ipadx=5, ipady=5)

        #        widgets['r_stow_all'] = tk.Button(
        #            all_buttons, text='STOW-A', width=8, height=2, bg=style.ind_off,
        #            command=lambda: [rad_stow(v+1) for v in range(3)])
        #        widgets['r_isol_all'] = tk.Button(
        #            all_buttons, text='ISOL-A', width=8, height=2, bg=style.ind_off,
        #            command=lambda: [rad_isol(v+1) for v in range(6)])
        #
        #        widgets['r_stow_all'].pack(pady=5)
        #        widgets['r_isol_all'].pack()

        def rad_isol(v):
            # TODO: move this code to the physics server, where it belongs.
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


class HabPage(tk.Frame):
    """1. Create a page in which lives all of the HabPage GUI
    2. Divide the page into a left and right pane. The right
    pane is divided into top, middle, bottom
    3. Create and render everything in each of the panes.
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Divide the page into two columns
        self.left_frame = tk.Frame(self, bg=style.bg)

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
        self._render_master()
        self._render_engines()
        self._render_subsystems()
        self._electrical_grid()

#        self._render_right_top()
        self._render_hab_reactors()
        self._render_reactor_confinement()

    def _render_master(self):

        master = cw.ENGLabelFrame(self.left_frame, text="Master", style=style)
        master.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['master_freeze'] = cw.Indicator(master,
                                                text='Freeze\nControls',
                                                style=style)
        widgets['master_freeze'].configure(width=60, height=60)

        widgets['a_master'] = cw.Alert(master, text='MASTER\nALARM',
                                       font=style.large, style=style)

        widgets['a_master'].configure(width=100, height=100)

        widgets['a_asteroid'] = cw.Alert(master, text='ASTEROID',
                                         style=style)
        widgets['a_radiation'] = cw.Alert(master, text='RADIATION',
                                          style=style)
        widgets['a_hab_gnomes'] = cw.Alert(master, text='HAB\nGNOMES',
                                           style=style)

        widgets['master_freeze'].grid(row=0, column=0)
        widgets['a_master'].grid(row=0, column=1, rowspan=2)
        widgets['a_asteroid'].grid(row=2, column=0, padx=5, pady=5)
        widgets['a_radiation'].grid(row=2, column=1, padx=5, pady=5)
        widgets['a_hab_gnomes'].grid(row=3, column=0, pady=5)

    def _render_engines(self):

        engines = cw.ENGLabelFrame(self.left_frame, text="Engines",
                                   style=style)
        engines.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['h_INJ1'] = cw.Indicator(engines, text="INJ-1", style=style)
        widgets['h_INJ2'] = cw.Indicator(engines, text="INJ-2", style=style)
        widgets["fuel"] = cw.ENGLabel(engines, text='FUEL', value=0, unit='kg',
                                      style=style)
        widgets['h_br'] = cw.ENGLabel(engines, text='BURN RATE',
                                      value=0, unit='kg/hr', style=style)

        widgets['h_INJ1'].grid(row=0, column=0)

        widgets['h_INJ1'].set_redrawer(
            lambda injector_widget, state:
            injector_widget.update(state.components[strings.INJ1].connected)
        )

        widgets['h_INJ2'].grid(row=1, column=0)
        widgets['fuel'].grid(row=0, column=1, sticky=tk.W)
        widgets['h_br'].grid(row=1, column=1, sticky=tk.W)

        # Engines > Fuel Management

        fuelmanager = cw.ENGLabelFrame(engines, text="", style=style)
        fuelmanager.grid(row=2, column=0, columnspan=2, pady=5)

        widgets['a_fuel_connected'] = cw.Alert(fuelmanager, text='TETHERED',
                                               style=style)
        widgets['h_load'] = cw.Indicator(fuelmanager, text="LOAD",
                                         style=style)
        widgets['h_dump'] = cw.Indicator(fuelmanager, text="DUMP",
                                         style=style)

        widgets['a_fuel_connected'].grid(row=0, column=0, padx=10)
        widgets['h_dump'].grid(row=0, column=1)
        widgets['h_load'].grid(row=0, column=2)

    def _render_subsystems(self):

        subsystems = cw.ENGLabelFrame(self.left_frame, text="Subsystems",
                                      style=style)
        subsystems.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        widgets['INS'] = cw.Indicator(subsystems, text='INS', style=style)
        widgets['RADAR'] = cw.Indicator(subsystems, text='RAD', style=style)
        widgets['LOS'] = cw.Indicator(subsystems, text='LOS', style=style)
        widgets['GNC'] = cw.Indicator(subsystems, text='GNC', style=style)
        widgets['a_ATMO'] = cw.Alert(subsystems, text='IN ATMO', style=style)
        widgets['CHUTE'] = cw.OneTimeButton(subsystems, text='CHUTE',
                                            style=style)
        widgets['a_SRBTIME'] = cw.Alert(subsystems, text='120s', invis=True,
                                        style=style)

        widgets['SRB'] = cw.OneTimeButton(subsystems, text='SRB', style=style)

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

    def _electrical_grid(self):
        # Electrical Grid
        hegrid = cw.ENGLabelFrame(self.right_frame_top,
                                  text="Habitat Electrical Grid", style=style)
        hegrid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Canvas(hegrid, width=375, height=350).pack()

    def _render_right_top(self):
        # Method 1
        # Draw all objects on a canvas including the switches
        method1 = cw.ENGLabelFrame(self.right_frame_top, text="Method 1",
                                   style=style)
        method1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        widgets['m1_he_grid'] = tk.Canvas(method1, width=375, height=350)
        widgets['m1_he_grid'].pack(padx=5, pady=5)

        # Method 2
        # Draw the unactive parts as an image, and superimpose buttons
        # and labels
        method2 = cw.ENGLabelFrame(self.right_frame_top, text="Method 2",
                                   style=style)
        method2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        images['ECS_bg'] = ImageTk.PhotoImage(Image.open(
            "data/textures/eng_mockup.PNG").resize((375, 95)))  # TODO: make this relative to orbitx.py
        widgets['m2_he_grid'] = tk.Label(method2, image=images['ECS_bg'],
                                         width=375, height=95)
        widgets['m2_he_grid'].pack(padx=5, pady=5)

        sw_width = 15
        sw_height = 23
        images['sw_open'] = ImageTk.PhotoImage(Image.open(
            "data/textures/eng_switch_open.PNG").resize(
            (sw_width, sw_height)))

        images['sw_closed'] = ImageTk.PhotoImage(Image.open(
            "data/textures/eng_switch_closed.PNG").resize(
            (sw_width, sw_height)))

        def switch(event):
            event.widget.configure(image=images['sw_closed'])

#        widgets['sw_ln1'] = tk.Button(widgets['m2_he_grid'],
#                                      width=sw_width, height=sw_height,
#                                      image=images['sw_open'],
#                                      relief=tk.FLAT,
#                                      bd=0,
#                                      bg=style.bg)
#        widgets['sw_ln1'].place(x=125, y=35)
#
#        widgets['sw_ln1'].bind('<Button-1>', switch)
#        widgets['sw_ln1'].bind_all('a', switch)

        def get_pos(event):
            position_display.configure(
                text='x = ' + str(event.x) + '  '
                     'y = ' + str(event.y))

        widgets['m2_he_grid'].bind('<Button-1>', get_pos)

        position_display = tk.Label(method2)
        position_display.pack()

    def _render_hab_reactors(self):
        hreactor = cw.ENGLabelFrame(self.right_frame_bot,
                                    text="Habitat Reactor", style=style)
        hreactor.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        widgets['hr_INJ-1'] = cw.Indicator(hreactor, text="R-INJ-1",
                                           style=style)
        widgets['hr_INJ-2'] = cw.Indicator(hreactor, text="R-INJ-2",
                                           style=style)
        widgets['hr_heater'] = cw.Indicator(hreactor, text="HEAT",
                                            style=style)
        widgets["hr_curr"] = cw.ENGLabel(hreactor, text='CURR',
                                         value=0, unit='A', style=style)
        widgets['hr_temp'] = cw.ENGLabel(hreactor, text='TEMP',
                                         value=81, unit='*C', style=style)
        widgets['a_hr_overtemp'] = cw.Alert(hreactor, text="OVERTEMP",
                                            style=style)

        widgets['hr_INJ-1'].grid(row=0, column=0, padx=10)
        widgets['hr_INJ-2'].grid(row=1, column=0)
        widgets['hr_heater'].grid(row=2, column=0)
        widgets["hr_curr"].grid(row=0, column=1, sticky=tk.W)
        widgets['hr_temp'].grid(row=1, column=1, sticky=tk.W)
        widgets['a_hr_overtemp'].grid(row=2, column=1)

        graph_frame = tk.Frame(hreactor)
        graph_width = 400
        hr_graph = tk.Canvas(graph_frame,
                             width=graph_width, height=200)
        graph_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
        hr_graph.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        hreactor.grid_columnconfigure(0, weight=1, minsize=60)
        hreactor.grid_columnconfigure(1, weight=1, minsize=70)
        hreactor.grid_columnconfigure(2, weight=3, minsize=graph_width)

    def _render_reactor_confinement(self):

        hrconfinement = cw.ENGLabelFrame(self.right_frame_bot,
                                         text="Reactor Confinement",
                                         style=style)
        hrconfinement.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        widgets['hr_RCON-1'] = cw.Indicator(hrconfinement, text="RCON-1",
                                            style=style)
        widgets['hr_RCON-2'] = cw.Indicator(hrconfinement, text="RCON-2",
                                            style=style)
        widgets["hr_RCON-1_temp"] = cw.ENGLabel(hrconfinement, text='TEMP',
                                                value=84, unit='*C',
                                                style=style)
        widgets['hr_RCON-2_temp'] = cw.ENGLabel(hrconfinement, text='TEMP',
                                                value=80, unit='*C',
                                                style=style)
        widgets['hr_BATT'] = cw.ENGLabel(hrconfinement, text='BATT',
                                         value=2000, unit='As',
                                         style=style)
        widgets['a_hr_lowBatt'] = cw.Alert(hrconfinement, text='LOW BATT',
                                           style=style)

        widgets['hr_RCON-1'].grid(row=0, column=0)
        widgets['hr_RCON-2'].grid(row=1, column=0)
        widgets["hr_RCON-1_temp"].grid(row=0, column=1)
        widgets['hr_RCON-2_temp'].grid(row=1, column=1)
        widgets['hr_BATT'].grid(row=2, column=0, columnspan=2, pady=10)
        widgets['a_hr_lowBatt'].grid(row=3, column=0, columnspan=2)

        hrconfinement.grid_columnconfigure(0, weight=1, minsize=60)
        hrconfinement.grid_columnconfigure(1, weight=1, minsize=70)

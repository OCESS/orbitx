import tkinter as tk

class coolantPage(tk.Frame):
    """
    An second tab for coolants and radiators
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


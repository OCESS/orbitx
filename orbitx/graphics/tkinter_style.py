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
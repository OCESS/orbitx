"""Symbols representing commonly used strings.
Feel free to `from strings import *`, your linter might not like you though."""

HABITAT = 'Habitat'
AYSE = 'AYSE'
SUN = 'Sun'
EARTH = 'Earth'
MODULE = 'Module'
SUN = 'Sun'
OCESS = 'OCESS'

RADS1 = 'RAD-S1'
RADS2 = 'RAD-S2'
AGRAV = 'A GRAV'
RCON1 = 'R-CON1'
RCON2 = 'R-CON2'
ARCON1 = 'Ayse R-CON1'
ARCON2 = 'Ayse R-CON2'
ACC1 = 'ACC1'
ION1 = 'ION1'
ACC2 = 'ACC2'
ION2 = 'ION2'
ACC3 = 'ACC3'
ION3 = 'ION3'
ACC4 = 'ACC4'
ION4 = 'ION4'
TRN1 = 'TRN1'
BUS1 = 'Primary Habitat Bus'
BUS2 = 'Secondary Habitat Bus'
BUS3 = 'Tertiary Habitat Bus'
AYSE_BUS = 'Ayse Power Bus'
TRN2 = 'TRN2'
FCELL = 'Fuel Cell'
BAT1 = 'BAT'
BAT2 = 'BACKUP BAT'
AYSE_BAT = 'AYSE BAT'
RCSP = 'RCSP'
COM = 'COM'
HAB_REACT = 'HAB reactor'
INJ1 = 'INJECTOR 1'
INJ2 = 'INJECTOR 2'
REACT_INJ1 = 'REACT INJ1'
REACT_INJ2 = 'REACT INJ2'
FCELL_INJ = 'F-CELL INJ'
AYSE_REACT = 'AYSE reactor'
DOCK_MOD = 'DOCK MOD'
RADAR = 'RADAR'
INS = 'INS'
DEPLY_PAK = 'DEPLY PAK'
ACTVT_PAK = 'ACTVT PAK'
GNC = 'GNC'
LOS = 'LOS'
SRB = 'SRB'
PLS = 'PLS'
CNT = 'CNT'
DUMP = 'DUMP'
LOAD = 'LOAD'
LP1 = 'LP-1'
LP2 = 'LP-2'
LP3 = 'LP-3'
RAD1 = 'RAD 1'
RAD2 = 'RAD 2'
RAD3 = 'RAD 3'
RAD4 = 'RAD 4'
RAD5 = 'RAD 5'
RAD6 = 'RAD 6'
RAD7 = 'RAD 7'
RAD8 = 'RAD 8'
EECOM = 'EECOM'
NETWORK = 'Network'

# This list is actually the single source-of-truth for what is and isn't a
# component!
# Changing the length of this list will likely invalidate any saves that have
# data about components. Changing the ordering will also have similar effects!
COMPONENT_NAMES = [
    RADS1,
    RADS2,
    AGRAV,
    RCON1,
    RCON2,
    ARCON1,
    ARCON2,
    ACC1,
    ION1,
    ACC2,
    ION2,
    ACC3,
    ION3,
    ACC4,
    ION4,
    FCELL,
    BAT1,
    BAT2,
    AYSE_BAT,
    RCSP,
    COM,
    HAB_REACT,
    INJ1,
    INJ2,
    REACT_INJ1,
    REACT_INJ2,
    FCELL_INJ,
    AYSE_REACT,
    DOCK_MOD,
    RADAR,
    INS,
    EECOM,
    NETWORK,
]

# This is referenced by data_structures.CoolantView.name!
COOLANT_LOOP_NAMES = [LP1, LP2, LP3]

# This is referenced by data_structures.RadiatorView.name!
RADIATOR_NAMES = [RAD1, RAD2, RAD3, RAD4, RAD5, RAD6, RAD7, RAD8]

BUS_NAMES = [BUS1, BUS2, BUS3, AYSE_BUS]

"""Symbols representing commonly used strings.
Feel free to `from strings import *`, even if your linter doesn't like it."""

HABITAT = 'Habitat'
AYSE = 'AYSE'
SUN = 'Sun'
EARTH = 'Earth'
MODULE = 'Module'
SUN = 'Sun'
OCESS = 'OCESS'

RADS1 = 'Primary Radiation Shielding'
RADS2 = 'Secondary Radiation Shielding'
AGRAV = 'Artificial Gravity'
RCON1 = 'Primary Reactor Containment'
RCON2 = 'Secondary Reactor Containment'
ARCON1 = 'Primary AYSE Reactor Containment'
ARCON2 = 'Secondary AYSE Reactor Containment'
ACC1 = 'ACC1'
ION1 = 'ION1'
ACC2 = 'ACC2'
ION2 = 'ION2'
ACC3 = 'ACC3'
ION3 = 'ION3'
ACC4 = 'ACC4'
ION4 = 'ION4'
PRIMARY_PUMP_1 = 'Loop 1 Primary Coolant Pump'
PRIMARY_PUMP_2 = 'Loop 2 Primary Coolant Pump'
SECONDARY_PUMP_1 = 'Loop 1 Secondary Coolant Pump'
SECONDARY_PUMP_2 = 'Loop 2 Secondary Coolant Pump'
HAB_CONV = 'High-Low Voltage Converter'
BUS1 = 'High-Voltage Habitat Bus'
BUS2 = 'Low-Voltage Habitat Bus'
AYSE_BUS = 'AYSE Power Bus'
AYSE_CONV = 'AYSE-Habitat Link'
FCELL = 'Fuel Cell'
BAT1 = 'Primary Battery'
BAT2 = 'Backup Battery'
AYSE_BAT = 'AYSE Battery'
RCSP = 'Reaction Control Thrusters'
COM = 'COM'
HAB_REACT = 'Habitat Tokamak Reactor'
REACTOR_HEATER = 'Reactor Heater'
INJ1 = 'INJECTOR 1'
INJ2 = 'INJECTOR 2'
REACT_INJ1 = 'REACT INJ1'
REACT_INJ2 = 'REACT INJ2'
FCELL_INJ = 'F-CELL INJ'
AYSE_REACT = 'AYSE Tokamak Reactor'
DOCK_MOD = 'DOCK MOD'
RADAR = 'Radar'
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
HAB_FUEL = 'Habitat Fuel'
AYSE_FUEL = 'AYSE Fuel'

# This list is actually the single source-of-truth for what is and isn't a
# component!
# Changing the length of this list will likely invalidate any saves that have
# data about components. Changing the ordering will also have similar effects!
COMPONENT_NAMES = [
    REACTOR_HEATER,
    FCELL_INJ,
    SECONDARY_PUMP_1,
    SECONDARY_PUMP_2,
    EECOM,
    NETWORK,
    COM,
    INS,
    LOS,
    GNC,
    FCELL,
    BAT1,
    BAT2,
    HAB_CONV,
    PRIMARY_PUMP_1,
    PRIMARY_PUMP_2,
    RADS1,
    RADS2,
    AGRAV,
    RCON1,
    RCON2,
    ACC1,
    ACC2,
    ACC3,
    ACC4,
    ION1,
    ION2,
    ION3,
    ION4,
    RCSP,
    INJ1,
    INJ2,
    HAB_REACT,
    REACT_INJ1,
    REACT_INJ2,
    DOCK_MOD,
    RADAR,
    AYSE_CONV,
    AYSE_REACT,
    AYSE_BAT,
    ARCON1,
    ARCON2,
]

# This is referenced by data_structures.CoolantView.name!
COOLANT_LOOP_NAMES = [LP1, LP2, LP3]

# This is referenced by data_structures.RadiatorView.name!
RADIATOR_NAMES = [RAD1, RAD2, RAD3, RAD4, RAD5, RAD6, RAD7, RAD8]

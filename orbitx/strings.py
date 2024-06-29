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
FCELL = 'Fuel Cell'
BAT1 = 'Primary Battery'
BAT2 = 'Backup Battery'
AYSE_BAT = 'AYSE Battery'
RCSP = 'Reaction Control Thrusters'
HAB_REACT = 'Habitat Tokamak Reactor'
REACTOR_HEATER = 'Reactor Heater'
REACT_INJ1 = 'Primary Reactor Injector'
REACT_INJ2 = 'Secondary Reactor Injector'
ENGINE_INJ1 = 'Primary Engine Injector'
ENGINE_INJ2 = 'Secondary Engine Injector'
FCELL_INJ = 'Fuel Cell Injector'  # TODO: Add this to the draw.io diagram and reconcile the other injectors
AYSE_REACT = 'AYSE Tokamak Reactor'
RADAR = 'Radar'
COM = 'COM'
INS = 'INS'
GNC = 'GNC'
LOS = 'LOS'
SRB = 'SRB'
EECOM = 'EECOM'
NETWORK = 'Network'
GPD1 = 'Graviton Emitter 1'
GPD2 = 'Graviton Emitter 2'
GPD3 = 'Graviton Emitter 3'
GPD4 = 'Graviton Emitter 4'
TTC = 'Tachyon-Tardyon Collider'
AYSE_INJ1 = 'Primary AYSE Injector'
AYSE_INJ2 = 'Secondary AYSE Injector'
AYSE_PUMP_1 = 'Primary AYSE Coolant Pump'
AYSE_PUMP_2 = 'Secondary AYSE Coolant Pump'
AYSE_CONV = 'AYSE-Habitat Link'
HAB_CONV = 'High-Low Voltage Converter'

BUS1 = 'High-Voltage Habitat Bus'
BUS2 = 'Low-Voltage Habitat Bus'
AYSE_BUS = 'AYSE Power Bus'
HAB_FUEL = 'Habitat Fuel'
AYSE_FUEL = 'AYSE Fuel'
DEPLY_PAK = 'DEPLY PAK'
ACTVT_PAK = 'ACTVT PAK'
DOCK_MOD = 'DOCK MOD'
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

# This list is actually the single source-of-truth for what is and isn't a
# component!
# Changing the length of this list will likely invalidate any saves that have
# data about components. Changing the ordering will also have similar effects!
# In this context, components are engineering bits and bobs and widgets that we
# definitely want to simulate the temperature of, and control whether or not they
# are on or off.
# For example, EARTH or HAB_FUEL are not components, but ENG1 and ENGINE_INJ1 are.
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
    PRIMARY_PUMP_1,
    PRIMARY_PUMP_2,
    SECONDARY_PUMP_1,
    SECONDARY_PUMP_2,
    HAB_CONV,
    FCELL,
    BAT1,
    BAT2,
    AYSE_BAT,
    RCSP,
    COM,
    HAB_REACT,
    REACTOR_HEATER,
    REACT_INJ1,
    REACT_INJ2,
    ENGINE_INJ1,
    ENGINE_INJ2,
    FCELL_INJ,
    AYSE_CONV,
    AYSE_REACT,
    RADAR,
    INS,
    GNC,
    LOS,
    SRB,
    EECOM,
    NETWORK,
    GPD1,
    GPD2,
    GPD3,
    GPD4,
    TTC,
    AYSE_INJ1,
    AYSE_INJ2,
    AYSE_PUMP_1,
    AYSE_PUMP_2,
]

# This is referenced by data_structures.CoolantView.name!
COOLANT_LOOP_NAMES = [LP1, LP2, LP3]

# This is referenced by data_structures.RadiatorView.name!
RADIATOR_NAMES = [RAD1, RAD2, RAD3, RAD4, RAD5, RAD6, RAD7, RAD8]

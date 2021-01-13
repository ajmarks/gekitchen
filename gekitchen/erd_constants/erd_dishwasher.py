"""Constants for handling dishwasher ERD values"""

__all__ = (
    "ErdCycleStateRaw",
    "ErdCycleState",
    "ErdOperatingState",
    "ErdRinseAgentRaw",
    "ErdRinseAgent",
    "CYCLE_STATE_RAW_MAP",
    "RINSE_AGENT_RAW_MAP"        
)

import enum

@enum.unique
class ErdCycleStateRaw(enum.Enum):
    STATE_01 = "01"
    STATE_02 = "02"
    STATE_03 = "03"
    STATE_04 = "04"
    STATE_05 = "05"
    STATE_06 = "06"
    STATE_07 = "07"
    STATE_08 = "08"
    STATE_09 = "09"
    STATE_10 = "10"
    STATE_11 = "11"
    STATE_12 = "12"
    STATE_13 = "13"
    STATE_14 = "14"
    STATE_15 = "15"
    STATE_16 = "16"
    STATE_17 = "17"
    STATE_18 = "18"

@enum.unique
class ErdCycleState(enum.Enum):
    NA = -1
    PRE_WASH = 1
    SENSING = 2
    MAIN_WASH = 3
    DRYING = 4
    SANITIZING = 5
    RINSING = 6
    PAUSE = 7

@enum.unique
class ErdOperatingState(enum.Enum):
    NA = "FF"
    PAUSE = "04"
    LOW_POWER = "00"
    POWER_UP = "01"
    STANDBY = "02"
    DELAY_START = "03"
    CYCLE_ACTIVE = "05"
    EOC = "06"
    DOWNLOAD_MODE = "07"
    SENSOR_CHECK_MODE = "08"
    LOAD_ACTIVATION_MODE = "09"
    MC_ONLY_MODE = "11"
    WARNING_MODE = "12"
    CONTROL_LOCKED = "13"
    CSM_TRIPPED = "14"

#I might be doing something wrong, but I saw an "02" value come through
#which doesn't seem to be in any of the documentation I saw... it registered
#as low on the interface, so I'll just assume there's two codes
@enum.unique
class ErdRinseAgentRaw(enum.Enum):
    RINSE_AGENT_GOOD = "00"
    RINSE_AGENT_LOW1 = "01"
    RINSE_AGENT_LOW2 = "02"

@enum.unique
class ErdRinseAgent(enum.Enum):
    NA = "FF"
    RINSE_AGENT_GOOD = "00"
    RINSE_AGENT_LOW = "01"

CYCLE_STATE_RAW_MAP = {
    ErdCycleStateRaw.STATE_01: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_02: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_03: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_04: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_05: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_06: ErdCycleState.PRE_WASH,
    ErdCycleStateRaw.STATE_07: ErdCycleState.SENSING,
    ErdCycleStateRaw.STATE_08: ErdCycleState.MAIN_WASH,
    ErdCycleStateRaw.STATE_09: ErdCycleState.MAIN_WASH,
    ErdCycleStateRaw.STATE_10: ErdCycleState.DRYING,
    ErdCycleStateRaw.STATE_11: ErdCycleState.SANITIZING,
    ErdCycleStateRaw.STATE_12: ErdCycleState.RINSING,
    ErdCycleStateRaw.STATE_13: ErdCycleState.RINSING,
    ErdCycleStateRaw.STATE_14: ErdCycleState.RINSING,
    ErdCycleStateRaw.STATE_15: ErdCycleState.RINSING,
    ErdCycleStateRaw.STATE_16: ErdCycleState.PAUSE,
    ErdCycleStateRaw.STATE_17: ErdCycleState.NA,
    ErdCycleStateRaw.STATE_18: ErdCycleState.NA
}

RINSE_AGENT_RAW_MAP = {
    ErdRinseAgentRaw.RINSE_AGENT_GOOD: ErdRinseAgent.RINSE_AGENT_GOOD,
    ErdRinseAgentRaw.RINSE_AGENT_LOW1: ErdRinseAgent.RINSE_AGENT_LOW,
    ErdRinseAgentRaw.RINSE_AGENT_LOW2: ErdRinseAgent.RINSE_AGENT_LOW
}

""" ERD Converters for dishwasher """

__all__ = (
    "ErdCycleStateConverter",
    "ErdOperatingStateConverter",
    "ErdRinseAgentConverter"
)

from .abstract import ErdReadOnlyConverter, ErdValueConverter
from .primitives import *
from gekitchen.erd.values.dishwasher import *

class ErdCycleStateConverter(ErdReadOnlyConverter[ErdCycleState]):
    def erd_decode(self, value: str) -> ErdCycleState:
        """ Decodes the dishwasher cycle state """    
        try:
            raw = ErdCycleStateRaw(value)
            return CYCLE_STATE_RAW_MAP[raw]
        except (ValueError, KeyError):
            return ErdCycleState.NA

class ErdOperatingStateConverter(ErdReadOnlyConverter[ErdOperatingState]):
    def erd_decode(self, value: str) -> ErdOperatingState:
        """Decode the dishwasher operating state """
        try:
            return ErdOperatingState(value)
        except ValueError:
            return ErdOperatingState.NA

class ErdRinseAgentConverter(ErdReadOnlyConverter[ErdRinseAgent]):
    def erd_decode(self, value: str) -> ErdRinseAgent:
        """ Decodes the dishwasher rinse agent status """
        try:
            raw = ErdRinseAgentRaw(value)
            return RINSE_AGENT_RAW_MAP[raw]
        except (ValueError, KeyError):
            return ErdRinseAgent.NA

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

""" ERD Converters for fridge """

__all__ = (
    "FridgeDoorStatusConverter",
    "HotWaterStatusConverter",
    "FridgeIceBucketStatusConverter",
    "IceMakerControlStatusConverter",
    "ErdFilterStatusConverter",
    "FridgeSetPointLimitsConverter",
    "FridgeSetPointsConverter"
)

from .abstract import ErdReadOnlyConverter, ErdValueConverter
from .primitives import *
from gekitchen.erd.values.fridge import *

class FridgeIceBucketStatusConverter(ErdReadOnlyConverter[FridgeIceBucketStatus]):
    def erd_decode(self, value: str) -> FridgeIceBucketStatus:
        """Decode Ice bucket status"""
        if not value:
            n = 0
        else:
            n = ErdIntConverter.erd_decode(value)

        is_present_ff = bool(n & 1)
        is_present_fz = bool(n & 2)
        state_full_ff = ErdFullNotFull.FULL if n & 4 else ErdFullNotFull.NOT_FULL
        state_full_fz = ErdFullNotFull.FULL if n & 8 else ErdFullNotFull.NOT_FULL

        if not is_present_ff:
            state_full_ff = ErdFullNotFull.NA
        if not is_present_fz:
            state_full_fz = ErdFullNotFull.NA

        if not (is_present_ff or is_present_ff):
            # No ice buckets at all
            total_status = ErdFullNotFull.NA
        elif (state_full_ff == ErdFullNotFull.NOT_FULL) or (state_full_fz == ErdFullNotFull.NOT_FULL):
            # At least one bucket is not full
            total_status = ErdFullNotFull.NOT_FULL
        else:
            total_status = ErdFullNotFull.FULL

        ice_status = FridgeIceBucketStatus(
            state_full_fridge=state_full_ff,
            state_full_freezer=state_full_fz,
            is_present_fridge=is_present_ff,
            is_present_freezer=is_present_fz,
            total_status=total_status,
        )
        return ice_status

class IceMakerControlStatusConverter(ErdValueConverter[IceMakerControlStatus]):
    def erd_decode(self, value: str) -> IceMakerControlStatus:
        def parse_status(val: str) -> ErdOnOff:
            try:
                return ErdOnOff(val)
            except ValueError:
                return ErdOnOff.NA

        status_fz = parse_status(value[:2])
        status_ff = parse_status(value[2:])

        return IceMakerControlStatus(status_fridge=status_ff, status_freezer=status_fz)
    def erd_encode(self, value: IceMakerControlStatus):
        return value.status_freezer.value + value.status_fridge.value

class FridgeDoorStatusConverter(ErdReadOnlyConverter[FridgeDoorStatus]):
    def erd_decode(self, value: str) -> FridgeDoorStatus:
        def get_door_status(val: str) -> ErdDoorStatus:
            try:
                return ErdDoorStatus(val)
            except ValueError:
                return ErdDoorStatus.NA

        fridge_right = get_door_status(value[:2])
        fridge_left = get_door_status(value[2:4])
        freezer = get_door_status(value[4:6])
        drawer = get_door_status(value[6:8])
        if (fridge_right != ErdDoorStatus.OPEN) and (fridge_left != ErdDoorStatus.OPEN):
            if freezer == ErdDoorStatus.OPEN:
                status = "Freezer Open"
            else:
                status = "Closed"
        elif freezer == ErdDoorStatus.OPEN:
            status = "All Open"
        else:
            status = "Fridge Open"
        return FridgeDoorStatus(
            fridge_right=fridge_right,
            fridge_left=fridge_left,
            freezer=freezer,
            drawer=drawer,
            status=status,
        )

class FridgeSetPointLimitsConverter(ErdReadOnlyConverter[FridgeSetPointLimits]):
    def erd_decode(self, value: str) -> FridgeSetPointLimits:
        return FridgeSetPointLimits(
            fridge_min=ErdSignedByteConverter.erd_decode(value[0:2]),
            fridge_max=ErdSignedByteConverter.erd_decode(value[2:4]),
            freezer_min=ErdSignedByteConverter.erd_decode(value[4:6]),
            freezer_max=ErdSignedByteConverter.erd_decode(value[6:8]),
        )

class FridgeSetPointsConverter(ErdValueConverter[FridgeSetPoints]):
    def erd_decode(self, value: str) -> FridgeSetPoints:
        return FridgeSetPoints(
            fridge=ErdSignedByteConverter.erd_decode(value[0:2]),
            freezer=ErdSignedByteConverter.erd_decode(value[2:4]),
        )
    @staticmethod    
    def erd_encode(value: FridgeSetPoints):
        return ErdSignedByteConverter.erd_encode(value.fridge) + ErdSignedByteConverter.erd_encode(value.freezer)

class HotWaterStatusConverter(ErdReadOnlyConverter[HotWaterStatus]):
    def erd_decode(self, value: str) -> HotWaterStatus:
        if not value:
            return HotWaterStatus(
                status=ErdHotWaterStatus.NA,
                time_until_ready=None,
                current_temp=None,
                tank_full=ErdFullNotFull.NA,
                brew_module=ErdPresent.NA,
                pod_status=ErdPodStatus.NA,
            )
        try:
            status = ErdHotWaterStatus(value[:2])
        except ValueError:
            status = ErdHotWaterStatus.NA

        time_until_ready = timedelta(minutes=ErdIntConverter.erd_decode(value[2:6]))
        current_temp = ErdIntConverter.erd_decode(value[6:8])

        try:
            tank_full = ErdFullNotFull(value[8:10])
        except ValueError:
            tank_full = ErdFullNotFull.NA

        try:
            brew_module = ErdPresent(value[10:12])
        except ValueError:
            brew_module = ErdPresent.NA

        try:
            pod_status = ErdPodStatus(value[12:14])
        except ValueError:
            pod_status = ErdPodStatus.NA

        return HotWaterStatus(
            status=status,
            time_until_ready=time_until_ready,
            current_temp=current_temp,
            tank_full=tank_full,
            brew_module=brew_module,
            pod_status=pod_status,
        )

class ErdFilterStatusConverter(ErdReadOnlyConverter[ErdFilterStatus]):
    def erd_decode(self, value: str) -> ErdFilterStatus:
        """Decode water filter status.

        This appears to be 9 bytes, of which only the first two are obviously used. I suspect that the others
        relate to how much time remains on the filter.  Leaving as a TODO.
        """
        status_byte = value[:2]
        if status_byte == "00":
            status_byte = value[2:4]
        try:
            return ErdFilterStatus(status_byte)
        except ValueError:
            return ErdFilterStatus.NA

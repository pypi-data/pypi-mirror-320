"""Module for the HaHomematic model."""

from __future__ import annotations

import logging
from typing import Final

from hahomematic.const import (
    CLICK_EVENTS,
    DEVICE_ERROR_EVENTS,
    IMPULSE_EVENTS,
    Flag,
    Operations,
    Parameter,
    ParamsetKey,
)
from hahomematic.decorators import inspector
from hahomematic.model import device as hmd
from hahomematic.model.event import create_event_and_append_to_channel
from hahomematic.model.generic import create_data_point_and_append_to_channel

__all__ = ["create_data_points_and_events"]

# Some parameters are marked as INTERNAL in the paramset and not considered by default,
# but some are required and should be added here.
_ALLOWED_INTERNAL_PARAMETERS: Final[tuple[Parameter, ...]] = (Parameter.DIRECTION,)
_LOGGER: Final = logging.getLogger(__name__)


@inspector()
def create_data_points_and_events(device: hmd.Device) -> None:
    """Create the data points associated to this device."""
    for channel in device.channels.values():
        for paramset_key, paramsset_key_descriptions in channel.paramsset_descriptions.items():
            if not device.central.parameter_visibility.is_relevant_paramset(
                model=device.model,
                channel_no=channel.no,
                paramset_key=paramset_key,
            ):
                continue
            for (
                parameter,
                parameter_data,
            ) in paramsset_key_descriptions.items():
                if device.central.parameter_visibility.parameter_is_ignored(
                    model=device.model,
                    channel_no=channel.no,
                    paramset_key=paramset_key,
                    parameter=parameter,
                ):
                    _LOGGER.debug(
                        "CREATE_DATA_POINTS_AND_APPEND_TO_DEVICE: Ignoring parameter: %s [%s]",
                        parameter,
                        channel.address,
                    )
                    continue
                parameter_is_un_ignored: bool = device.central.parameter_visibility.parameter_is_un_ignored(
                    model=device.model,
                    channel_no=channel.no,
                    paramset_key=paramset_key,
                    parameter=parameter,
                )

                if paramset_key == ParamsetKey.MASTER:
                    # All MASTER parameters must be un ignored
                    if not parameter_is_un_ignored:
                        continue

                    # required to fix hm master paramset operation values
                    if parameter_is_un_ignored and parameter_data["OPERATIONS"] == 0:
                        parameter_data["OPERATIONS"] = 3

                if parameter_data["OPERATIONS"] & Operations.EVENT and (
                    parameter in CLICK_EVENTS
                    or parameter.startswith(DEVICE_ERROR_EVENTS)
                    or parameter in IMPULSE_EVENTS
                ):
                    create_event_and_append_to_channel(
                        channel=channel,
                        parameter=parameter,
                        parameter_data=parameter_data,
                    )
                if (
                    not parameter_data["OPERATIONS"] & Operations.EVENT
                    and not parameter_data["OPERATIONS"] & Operations.WRITE
                ) or (
                    parameter_data["FLAGS"] & Flag.INTERNAL
                    and parameter not in _ALLOWED_INTERNAL_PARAMETERS
                    and not parameter_is_un_ignored
                ):
                    _LOGGER.debug(
                        "CREATE_DATA_POINTS: Skipping %s (no event or internal)",
                        parameter,
                    )
                    continue
                # CLICK_EVENTS are allowed for Buttons
                if parameter not in IMPULSE_EVENTS and (
                    not parameter.startswith(DEVICE_ERROR_EVENTS) or parameter_is_un_ignored
                ):
                    create_data_point_and_append_to_channel(
                        channel=channel,
                        paramset_key=paramset_key,
                        parameter=parameter,
                        parameter_data=parameter_data,
                    )

from typing import Callable
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.components.select import SelectEntity, SelectEntityDescription

from .const import (
    DOMAIN,
    DATA_COORDINATORS,
    SELECT_HORIZONTAL_SWING,
    SELECT_VERTICAL_SWING,
    AQUAREA_COORDINATORS,
)
from aio_panasonic_comfort_cloud import PanasonicDevice, ChangeRequestBuilder, constants
import aioaquarea

from .coordinator import PanasonicDeviceCoordinator, AquareaDeviceCoordinator
from .base import PanasonicDataEntity, AquareaDataEntity

@dataclass(frozen=True, kw_only=True)
class PanasonicSelectEntityDescription(SelectEntityDescription):
    """Description of a select entity."""

    set_option: Callable[[ChangeRequestBuilder, str], ChangeRequestBuilder]
    get_current_option: Callable[[PanasonicDevice], str]
    is_available: Callable[[PanasonicDevice], bool]
    get_options: Callable[[PanasonicDevice], list[str]] = None


HORIZONTAL_SWING_DESCRIPTION = PanasonicSelectEntityDescription(
    key=SELECT_HORIZONTAL_SWING,
    translation_key=SELECT_HORIZONTAL_SWING,
    icon="mdi:swap-horizontal",
    name="Horizontal Swing Mode",
    options=[
        opt.name
        for opt in constants.AirSwingLR
        if opt != constants.AirSwingLR.Unavailable
    ],
    set_option=lambda builder, new_value: builder.set_horizontal_swing(new_value),
    get_current_option=lambda device: device.parameters.horizontal_swing_mode.name,
    is_available=lambda device: device.has_horizontal_swing,
)
VERTICAL_SWING_DESCRIPTION = PanasonicSelectEntityDescription(
    key=SELECT_VERTICAL_SWING,
    translation_key=SELECT_VERTICAL_SWING,
    icon="mdi:swap-vertical",
    name="Vertical Swing Mode",
    get_options=lambda device: [
        opt.name
        for opt in constants.AirSwingUD
        if opt != constants.AirSwingUD.Swing or device.features.auto_swing_ud
    ],
    set_option=lambda builder, new_value: builder.set_vertical_swing(new_value),
    get_current_option=lambda device: device.parameters.vertical_swing_mode.name,
    is_available=lambda device: True,
)



async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    entities = []
    data_coordinators: list[PanasonicDeviceCoordinator] = hass.data[DOMAIN][DATA_COORDINATORS]
    aquarea_coordinators = hass.data[DOMAIN].get(AQUAREA_COORDINATORS, [])

    for coordinator in data_coordinators:
        entities.append(PanasonicSelectEntity(coordinator, HORIZONTAL_SWING_DESCRIPTION))
        entities.append(PanasonicSelectEntity(coordinator, VERTICAL_SWING_DESCRIPTION))

    # --- Aquarea selects ---
    for coordinator in aquarea_coordinators:
        device = coordinator.device
        # Quiet mode
        if hasattr(device, "has_quiet_mode") and getattr(device, "has_quiet_mode", False):
            quiet_desc = PanasonicSelectEntityDescription(
                key="quiet_mode",
                translation_key="quiet_mode",
                name="Quiet Mode",
                icon="mdi:volume-off",
                options=getattr(device, "quiet_modes", []),
                set_option=lambda builder, value: builder.set_quiet_mode(value),
                get_current_option=lambda dev: getattr(dev, "quiet_mode", None),
                is_available=lambda dev: getattr(dev, "has_quiet_mode", False),
            )
            entities.append(PanasonicSelectEntity(coordinator, quiet_desc))
        # Operation mode
        if hasattr(device, "has_operation_mode") and getattr(device, "has_operation_mode", False):
            op_desc = PanasonicSelectEntityDescription(
                key="operation_mode",
                translation_key="operation_mode",
                name="Operation Mode",
                icon="mdi:cog",
                options=getattr(device, "operation_modes", []),
                set_option=lambda builder, value: builder.set_operation_mode(value),
                get_current_option=lambda dev: getattr(dev, "operation_mode", None),
                is_available=lambda dev: getattr(dev, "has_operation_mode", False),
            )
            entities.append(PanasonicSelectEntity(coordinator, op_desc))
        # Presets
        if hasattr(device, "has_presets") and getattr(device, "has_presets", False):
            preset_desc = PanasonicSelectEntityDescription(
                key="preset",
                translation_key="preset",
                name="Preset",
                icon="mdi:star",
                options=getattr(device, "presets", []),
                set_option=lambda builder, value: builder.set_preset(value),
                get_current_option=lambda dev: getattr(dev, "preset", None),
                is_available=lambda dev: getattr(dev, "has_presets", False),
            )
            entities.append(PanasonicSelectEntity(coordinator, preset_desc))

        # Powerful Time
        if hasattr(device, "powerful_time") and hasattr(device, "set_powerful_time"):
            pow_desc = AquareaSelectEntityDescription(
                key="powerful_time",
                translation_key="powerful_time",
                name="Powerful Time",
                icon="mdi:timer-outline",
                options=[e.name for e in aioaquarea.PowerfulTime],
                set_option=lambda dev, val: dev.set_powerful_time(aioaquarea.PowerfulTime[val]),
                get_current_option=lambda dev: getattr(dev.powerful_time, "name", str(dev.powerful_time)),
                is_available=lambda dev: dev.powerful_time is not None,
            )
            entities.append(AquareaSelectEntity(coordinator, pow_desc))

        # Special Status
        if hasattr(device, "special_status") and hasattr(device, "set_special_status"):
            special_desc = AquareaSelectEntityDescription(
                key="special_status",
                translation_key="special_status",
                name="Special Status",
                icon="mdi:leaf",
                options=[e.name for e in aioaquarea.SpecialStatus],
                set_option=lambda dev, val: dev.set_special_status(aioaquarea.SpecialStatus[val]),
                get_current_option=lambda dev: getattr(dev.special_status, "name", str(dev.special_status)),
                is_available=lambda dev: dev.special_status is not None,
            )
            entities.append(AquareaSelectEntity(coordinator, special_desc))

    async_add_entities(entities)


class PanasonicSelectEntityBase(SelectEntity):
    """Base class for all select entities."""

    entity_description: PanasonicSelectEntityDescription


class PanasonicSelectEntity(PanasonicDataEntity, PanasonicSelectEntityBase):

    def __init__(
        self,
        coordinator: PanasonicDeviceCoordinator,
        description: PanasonicSelectEntityDescription,
    ):
        self.entity_description = description
        if description.get_options is not None:
            self._attr_options = description.get_options(coordinator.device)
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.entity_description.is_available(self.coordinator.device)

    async def async_select_option(self, option: str) -> None:
        builder = self.coordinator.get_change_request_builder()
        self.entity_description.set_option(builder, option)
        await self.coordinator.async_apply_changes(builder)
        self._attr_current_option = option
        self.async_write_ha_state()

    def _async_update_attrs(self) -> None:
        self._attr_current_option = self.entity_description.get_current_option(
            self.coordinator.device
        )

@dataclass(frozen=True, kw_only=True)
class AquareaSelectEntityDescription(SelectEntityDescription):
    """Description of an Aquarea select entity."""
    set_option: Callable[['AquareaDevice', str], Any]
    get_current_option: Callable[['AquareaDevice'], str]
    is_available: Callable[['AquareaDevice'], bool]

class AquareaSelectEntity(AquareaDataEntity, SelectEntity):
    entity_description: AquareaSelectEntityDescription

    def __init__(self, coordinator: AquareaDeviceCoordinator, description: AquareaSelectEntityDescription):
        self.entity_description = description
        self._attr_options = description.options
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        return self.entity_description.is_available(self.coordinator.device)

    async def async_select_option(self, option: str) -> None:
        await self.entity_description.set_option(self.coordinator.device, option)
        self._attr_current_option = option
        self.async_write_ha_state()

    def _async_update_attrs(self) -> None:
        self._attr_available = self.available
        self._attr_current_option = self.entity_description.get_current_option(self.coordinator.device)


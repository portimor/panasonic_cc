"""Support for Panasonic Nanoe."""

import logging
from typing import Callable
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from aio_panasonic_comfort_cloud import (
    constants,
    PanasonicDevice,
    PanasonicDeviceZone,
    ChangeRequestBuilder,
)


from . import DOMAIN
from .const import (
    DATA_COORDINATORS,
    CONF_FORCE_ENABLE_NANOE,
    DEFAULT_FORCE_ENABLE_NANOE,
)
from .coordinator import PanasonicDeviceCoordinator, AquareaDeviceCoordinator
from .base import PanasonicDataEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PanasonicSwitchEntityDescription(SwitchEntityDescription):
    """Describes Panasonic Switch entity."""

    on_func: Callable[[ChangeRequestBuilder], ChangeRequestBuilder]
    off_func: Callable[[ChangeRequestBuilder], ChangeRequestBuilder]
    get_state: Callable[[PanasonicDevice], bool]
    is_available: Callable[[PanasonicDevice], bool]


NANOE_DESCRIPTION = PanasonicSwitchEntityDescription(
    key="nanoe",
    translation_key="nanoe",
    name="Nanoe",
    icon="mdi:virus-off",
    on_func=lambda builder: builder.set_nanoe_mode(constants.NanoeMode.On),
    off_func=lambda builder: builder.set_nanoe_mode(constants.NanoeMode.Off),
    get_state=lambda device: device.parameters.nanoe_mode
    in [constants.NanoeMode.On, constants.NanoeMode.ModeG, constants.NanoeMode.All],
    is_available=lambda device: device.has_nanoe,
)
ECONAVI_DESCRIPTION = PanasonicSwitchEntityDescription(
    key="eco-navi",
    translation_key="eco-navi",
    name="ECONAVI",
    icon="mdi:leaf",
    on_func=lambda builder: builder.set_eco_navi_mode(constants.EcoNaviMode.On),
    off_func=lambda builder: builder.set_eco_navi_mode(constants.EcoNaviMode.Off),
    get_state=lambda device: device.parameters.eco_navi_mode
    == constants.EcoNaviMode.On,
    is_available=lambda device: device.has_eco_navi,
)
ECO_FUNCTION_DESCRIPTION = PanasonicSwitchEntityDescription(
    key="eco-function",
    translation_key="eco-function",
    name="AI ECO",
    icon="mdi:leaf",
    on_func=lambda builder: builder.set_eco_function_mode(constants.EcoFunctionMode.On),
    off_func=lambda builder: builder.set_eco_function_mode(
        constants.EcoFunctionMode.Off
    ),
    get_state=lambda device: device.parameters.eco_function_mode
    == constants.EcoFunctionMode.On,
    is_available=lambda device: device.has_eco_function,
)
IAUTOX_DESCRIPTION = PanasonicSwitchEntityDescription(
    key="iauto-x",
    translation_key="iauto-x",
    name="iAUTO-X",
    icon="mdi:snowflake",
    on_func=lambda builder: builder.set_iautox_mode(constants.IAutoXMode.On),
    off_func=lambda builder: builder.set_iautox_mode(constants.IAutoXMode.Off),
    get_state=lambda device: device.parameters.iautox_mode == constants.IAutoXMode.On
    and device.parameters.mode == constants.OperationMode.Auto,
    is_available=lambda device: device.has_iauto_x,
)


def create_zone_mode_description(zone: PanasonicDeviceZone):
    return PanasonicSwitchEntityDescription(
        key=f"zone-{zone.id}",
        translation_key=f"zone-{zone.id}",
        name=zone.name,
        icon="mdi:thermostat",
        off_func=lambda builder: builder.set_zone_mode(zone.id, constants.ZoneMode.Off),
        on_func=lambda builder: builder.set_zone_mode(zone.id, constants.ZoneMode.On),
        get_state=lambda device: device.parameters.get_zone(zone.id).mode
        == constants.ZoneMode.On,
        is_available=lambda device: True,
    )



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    devices = []
    data_coordinators: list[PanasonicDeviceCoordinator] = hass.data[DOMAIN][DATA_COORDINATORS]
    aquarea_coordinators = hass.data[DOMAIN].get("aquarea_coordinators", [])
    force_enable_nanoe = entry.options.get(CONF_FORCE_ENABLE_NANOE, DEFAULT_FORCE_ENABLE_NANOE)

    # Comfort Cloud switches (legacy)
    for data_coordinator in data_coordinators:
        devices.append(PanasonicSwitchEntity(data_coordinator, NANOE_DESCRIPTION, always_available=force_enable_nanoe))
        devices.append(PanasonicSwitchEntity(data_coordinator, ECONAVI_DESCRIPTION))
        devices.append(PanasonicSwitchEntity(data_coordinator, ECO_FUNCTION_DESCRIPTION))
        devices.append(PanasonicSwitchEntity(data_coordinator, IAUTOX_DESCRIPTION))
        if data_coordinator.device.has_zones:
            for zone in data_coordinator.device.parameters.zones:
                devices.append(PanasonicSwitchEntity(data_coordinator, create_zone_mode_description(zone)))

    # --- Aquarea switches ---
    for coordinator in aquarea_coordinators:
        device = coordinator.device
        # Nanoe
        if hasattr(device, "has_nanoe") and getattr(device, "has_nanoe", False):
            devices.append(PanasonicSwitchEntity(coordinator, NANOE_DESCRIPTION))
        # Eco mode
        if hasattr(device, "has_eco_mode") and getattr(device, "has_eco_mode", False):
            eco_desc = PanasonicSwitchEntityDescription(
                key="eco_mode",
                translation_key="eco_mode",
                name="Eco Mode",
                icon="mdi:leaf",
                on_func=lambda builder: builder.set_eco_mode(True),
                off_func=lambda builder: builder.set_eco_mode(False),
                get_state=lambda dev: getattr(dev, "eco_mode", False),
                is_available=lambda dev: getattr(dev, "has_eco_mode", False),
            )
            devices.append(PanasonicSwitchEntity(coordinator, eco_desc))
        # Powerful mode
        if hasattr(device, "has_powerful_mode") and getattr(device, "has_powerful_mode", False):
            powerful_desc = PanasonicSwitchEntityDescription(
                key="powerful_mode",
                translation_key="powerful_mode",
                name="Powerful Mode",
                icon="mdi:flash",
                on_func=lambda builder: builder.set_powerful_mode(True),
                off_func=lambda builder: builder.set_powerful_mode(False),
                get_state=lambda dev: getattr(dev, "powerful_mode", False),
                is_available=lambda dev: getattr(dev, "has_powerful_mode", False),
            )
            devices.append(PanasonicSwitchEntity(coordinator, powerful_desc))
        # Force heater
        if hasattr(device, "has_force_heater") and getattr(device, "has_force_heater", False):
            force_heater_desc = PanasonicSwitchEntityDescription(
                key="force_heater",
                translation_key="force_heater",
                name="Force Heater",
                icon="mdi:radiator",
                on_func=lambda builder: builder.set_force_heater(True),
                off_func=lambda builder: builder.set_force_heater(False),
                get_state=lambda dev: getattr(dev, "force_heater", False),
                is_available=lambda dev: getattr(dev, "has_force_heater", False),
            )
            devices.append(PanasonicSwitchEntity(coordinator, force_heater_desc))
        # Force DHW
        if hasattr(device, "has_force_dhw") and getattr(device, "has_force_dhw", False):
            force_dhw_desc = PanasonicSwitchEntityDescription(
                key="force_dhw",
                translation_key="force_dhw",
                name="Force DHW",
                icon="mdi:water-boiler",
                on_func=lambda builder: builder.set_force_dhw(True),
                off_func=lambda builder: builder.set_force_dhw(False),
                get_state=lambda dev: getattr(dev, "force_dhw", False),
                is_available=lambda dev: getattr(dev, "has_force_dhw", False),
            )
            devices.append(PanasonicSwitchEntity(coordinator, force_dhw_desc))
        # Defrost
        if hasattr(device, "has_defrost") and getattr(device, "has_defrost", False):
            defrost_desc = PanasonicSwitchEntityDescription(
                key="defrost",
                translation_key="defrost",
                name="Defrost",
                icon="mdi:snowflake-melt",
                on_func=lambda builder: builder.set_defrost(True),
                off_func=lambda builder: builder.set_defrost(False),
                get_state=lambda dev: getattr(dev, "defrost", False),
                is_available=lambda dev: getattr(dev, "has_defrost", False),
            )
            devices.append(PanasonicSwitchEntity(coordinator, defrost_desc))

    async_add_entities(devices)


class PanasonicSwitchEntityBase(SwitchEntity):
    """Base class for all Panasonic switch entities."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    entity_description: PanasonicSwitchEntityDescription  # type: ignore[override]


class PanasonicSwitchEntity(PanasonicDataEntity, PanasonicSwitchEntityBase):
    """Representation of a Panasonic switch."""

    def __init__(
        self,
        coordinator: PanasonicDeviceCoordinator,
        description: PanasonicSwitchEntityDescription,
        always_available: bool = False,
    ):
        """Initialize the Switch."""
        self.entity_description = description
        self._always_available = always_available
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._always_available or self.entity_description.is_available(
            self.coordinator.device
        )

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        self._attr_available = self.entity_description.is_available(
            self.coordinator.device
        )
        self._attr_is_on = self.entity_description.get_state(self.coordinator.device)

    async def async_turn_on(self, **kwargs):
        """Turn on the Switch."""
        builder = self.coordinator.get_change_request_builder()
        self.entity_description.on_func(builder)
        await self.coordinator.async_apply_changes(builder)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the Switch."""
        builder = self.coordinator.get_change_request_builder()
        self.entity_description.off_func(builder)
        await self.coordinator.async_apply_changes(builder)
        self._attr_is_on = False
        self.async_write_ha_state()

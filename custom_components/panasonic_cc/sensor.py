from typing import Callable, Any
from dataclasses import dataclass
import logging

from homeassistant.const import UnitOfTemperature, EntityCategory
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
    SensorEntityDescription,
)

from aio_panasonic_comfort_cloud import (
    PanasonicDevice,
    PanasonicDeviceEnergy,
    PanasonicDeviceZone,
    constants,
)
from aioaquarea import Device as AquareaDevice

from .const import DOMAIN, DATA_COORDINATORS, ENERGY_COORDINATORS, AQUAREA_COORDINATORS
from .base import PanasonicDataEntity, PanasonicEnergyEntity, AquareaDataEntity
from .coordinator import (
    PanasonicDeviceCoordinator,
    PanasonicDeviceEnergyCoordinator,
    AquareaDeviceCoordinator,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PanasonicSensorEntityDescription(SensorEntityDescription):
    """Describes Panasonic sensor entity."""

    get_state: Callable[[PanasonicDevice], Any] | None = None
    is_available: Callable[[PanasonicDevice], bool] | None = None


@dataclass(frozen=True, kw_only=True)
class PanasonicEnergySensorEntityDescription(SensorEntityDescription):
    """Describes Panasonic sensor entity."""

    get_state: Callable[[PanasonicDeviceEnergy], Any] | None = None


@dataclass(frozen=True, kw_only=True)
class AquareaSensorEntityDescription(SensorEntityDescription):
    """Describes Aquarea sensor entity."""

    get_state: Callable[[AquareaDevice], Any] | None = None
    is_available: Callable[[AquareaDevice], bool] | None = None


INSIDE_TEMPERATURE_DESCRIPTION = PanasonicSensorEntityDescription(
    key="inside_temperature",
    translation_key="inside_temperature",
    name="Inside Temperature",
    icon="mdi:thermometer",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    get_state=lambda device: device.parameters.inside_temperature,
    is_available=lambda device: device.parameters.inside_temperature is not None,
)
OUTSIDE_TEMPERATURE_DESCRIPTION = PanasonicSensorEntityDescription(
    key="outside_temperature",
    translation_key="outside_temperature",
    name="Outside Temperature",
    icon="mdi:thermometer",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    get_state=lambda device: device.parameters.outside_temperature,
    is_available=lambda device: device.parameters.outside_temperature is not None,
)
LAST_UPDATE_TIME_DESCRIPTION = PanasonicSensorEntityDescription(
    key="last_update",
    translation_key="last_update",
    name="Last Updated",
    icon="mdi:clock-outline",
    device_class=SensorDeviceClass.TIMESTAMP,
    entity_category=EntityCategory.DIAGNOSTIC,
    state_class=None,
    native_unit_of_measurement=None,
    get_state=lambda device: device.last_update,
    is_available=lambda device: True,
    entity_registry_enabled_default=False,
)
DATA_AGE_DESCRIPTION = PanasonicSensorEntityDescription(
    key="data_age",
    translation_key="data_age",
    name="Cached Data Age",
    icon="mdi:clock-outline",
    device_class=SensorDeviceClass.TIMESTAMP,
    entity_category=EntityCategory.DIAGNOSTIC,
    state_class=None,
    native_unit_of_measurement=None,
    get_state=lambda device: device.timestamp,
    is_available=lambda device: device.info.status_data_mode
    == constants.StatusDataMode.CACHED,
    entity_registry_enabled_default=False,
)
DATA_MODE_DESCRIPTION = PanasonicSensorEntityDescription(
    key="status_data_mode",
    translation_key="status_data_mode",
    name="Data Mode",
    options=[opt.name for opt in constants.StatusDataMode],
    device_class=SensorDeviceClass.ENUM,
    entity_category=EntityCategory.DIAGNOSTIC,
    state_class=None,
    native_unit_of_measurement=None,
    get_state=lambda device: device.info.status_data_mode.name,
    is_available=lambda device: True,
    entity_registry_enabled_default=True,
)
DAILY_ENERGY_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="daily_energy_sensor",
    translation_key="daily_energy_sensor",
    name="Daily Energy",
    icon="mdi:flash",
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement="kWh",
    get_state=lambda energy: energy.consumption,
)
DAILY_HEATING_ENERGY_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="daily_heating_energy",
    translation_key="daily_heating_energy",
    name="Daily Heating Energy",
    icon="mdi:flash",
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement="kWh",
    get_state=lambda energy: energy.heating_consumption,
)
DAILY_COOLING_ENERGY_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="daily_cooling_energy",
    translation_key="daily_cooling_energy",
    name="Daily Cooling Energy",
    icon="mdi:flash",
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement="kWh",
    get_state=lambda energy: energy.cooling_consumption,
)
POWER_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="current_power",
    translation_key="current_power",
    name="Current Extrapolated Power",
    icon="mdi:flash",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement="W",
    get_state=lambda energy: energy.current_power,
)
COOLING_POWER_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="cooling_power",
    translation_key="cooling_power",
    name="Cooling Extrapolated Power",
    icon="mdi:flash",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement="W",
    get_state=lambda energy: energy.cooling_power,
)
HEATING_POWER_DESCRIPTION = PanasonicEnergySensorEntityDescription(
    key="heating_power",
    translation_key="heating_power",
    name="Heating Extrapolated Power",
    icon="mdi:flash",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement="W",
    get_state=lambda energy: energy.heating_power,
)

AQUAREA_OUTSIDE_TEMPERATURE_DESCRIPTION = AquareaSensorEntityDescription(
    key="outside_temperature",
    translation_key="outside_temperature",
    name="Outside Temperature",
    icon="mdi:thermometer",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    get_state=lambda device: device.temperature_outdoor,
    is_available=lambda device: device.temperature_outdoor is not None,
)


def create_zone_temperature_description(zone: PanasonicDeviceZone):
    return PanasonicSensorEntityDescription(
        key=f"zone-{zone.id}-temperature",
        translation_key=f"zone-{zone.id}-temperature",
        name=f"{zone.name} Temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        get_state=lambda device: zone.temperature,
        is_available=lambda device: zone.has_temperature,
    )


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    data_coordinators: list[PanasonicDeviceCoordinator] = hass.data[DOMAIN][
        DATA_COORDINATORS
    ]
    energy_coordinators: list[PanasonicDeviceEnergyCoordinator] = hass.data[DOMAIN][
        ENERGY_COORDINATORS
    ]
    aquarea_coordinators: list[AquareaDeviceCoordinator] = hass.data[DOMAIN][
        AQUAREA_COORDINATORS
    ]

    for coordinator in data_coordinators:
        entities.append(
            PanasonicSensorEntity(coordinator, INSIDE_TEMPERATURE_DESCRIPTION)
        )
        entities.append(
            PanasonicSensorEntity(coordinator, OUTSIDE_TEMPERATURE_DESCRIPTION)
        )
        entities.append(
            PanasonicSensorEntity(coordinator, LAST_UPDATE_TIME_DESCRIPTION)
        )
        entities.append(PanasonicSensorEntity(coordinator, DATA_AGE_DESCRIPTION))
        entities.append(PanasonicSensorEntity(coordinator, DATA_MODE_DESCRIPTION))
        if coordinator.device.has_zones:
            for zone in coordinator.device.parameters.zones:
                entities.append(
                    PanasonicSensorEntity(
                        coordinator, create_zone_temperature_description(zone)
                    )
                )

    for coordinator in energy_coordinators:
        entities.append(
            PanasonicEnergySensorEntity(coordinator, DAILY_ENERGY_DESCRIPTION)
        )
        entities.append(
            PanasonicEnergySensorEntity(coordinator, DAILY_COOLING_ENERGY_DESCRIPTION)
        )
        entities.append(
            PanasonicEnergySensorEntity(coordinator, DAILY_HEATING_ENERGY_DESCRIPTION)
        )
        entities.append(PanasonicEnergySensorEntity(coordinator, POWER_DESCRIPTION))
        entities.append(
            PanasonicEnergySensorEntity(coordinator, COOLING_POWER_DESCRIPTION)
        )
        entities.append(
            PanasonicEnergySensorEntity(coordinator, HEATING_POWER_DESCRIPTION)
        )


    for coordinator in aquarea_coordinators:
        device = coordinator.device
        # Temperatura exterior
        entities.append(AquareaSensorEntity(coordinator, AQUAREA_OUTSIDE_TEMPERATURE_DESCRIPTION))
        # Temperatura del tanque
        if hasattr(device, "tank_temperature"):
            tank_temp_desc = AquareaSensorEntityDescription(
                key="tank_temperature",
                translation_key="tank_temperature",
                name="Tank Temperature",
                icon="mdi:water-boiler",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                get_state=lambda dev: getattr(dev, "tank_temperature", None),
                is_available=lambda dev: getattr(dev, "tank_temperature", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, tank_temp_desc))
        # Temperaturas de zonas
        if hasattr(device, "zones"):
            for zone in getattr(device, "zones", []):
                if hasattr(zone, "temperature"):
                    zone_temp_desc = AquareaSensorEntityDescription(
                        key=f"zone_{getattr(zone, 'id', 'x')}_temperature",
                        translation_key=f"zone_{getattr(zone, 'id', 'x')}_temperature",
                        name=f"Zone {getattr(zone, 'name', 'X')} Temperature",
                        icon="mdi:thermometer",
                        device_class=SensorDeviceClass.TEMPERATURE,
                        state_class=SensorStateClass.MEASUREMENT,
                        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                        get_state=lambda dev, z=zone: getattr(z, "temperature", None),
                        is_available=lambda dev, z=zone: getattr(z, "temperature", None) is not None,
                    )
                    entities.append(AquareaSensorEntity(coordinator, zone_temp_desc))
        # Flow temperature
        if hasattr(device, "flow_temperature"):
            flow_temp_desc = AquareaSensorEntityDescription(
                key="flow_temperature",
                translation_key="flow_temperature",
                name="Flow Temperature",
                icon="mdi:thermometer",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                get_state=lambda dev: getattr(dev, "flow_temperature", None),
                is_available=lambda dev: getattr(dev, "flow_temperature", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, flow_temp_desc))
        # Return temperature
        if hasattr(device, "return_temperature"):
            return_temp_desc = AquareaSensorEntityDescription(
                key="return_temperature",
                translation_key="return_temperature",
                name="Return Temperature",
                icon="mdi:thermometer",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                get_state=lambda dev: getattr(dev, "return_temperature", None),
                is_available=lambda dev: getattr(dev, "return_temperature", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, return_temp_desc))
        # Estado del compresor
        if hasattr(device, "compressor_status"):
            comp_desc = AquareaSensorEntityDescription(
                key="compressor_status",
                translation_key="compressor_status",
                name="Compressor Status",
                icon="mdi:engine",
                get_state=lambda dev: getattr(dev, "compressor_status", None),
                is_available=lambda dev: getattr(dev, "compressor_status", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, comp_desc))
        # Consumo energético
        if hasattr(device, "energy_consumption"):
            energy_desc = AquareaSensorEntityDescription(
                key="energy_consumption",
                translation_key="energy_consumption",
                name="Energy Consumption",
                icon="mdi:flash",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL_INCREASING,
                native_unit_of_measurement="kWh",
                get_state=lambda dev: getattr(dev, "energy_consumption", None),
                is_available=lambda dev: getattr(dev, "energy_consumption", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, energy_desc))
        # Códigos de error / alarmas
        if hasattr(device, "error_code"):
            error_desc = AquareaSensorEntityDescription(
                key="error_code",
                translation_key="error_code",
                name="Error Code",
                icon="mdi:alert",
                get_state=lambda dev: getattr(dev, "error_code", None),
                is_available=lambda dev: getattr(dev, "error_code", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, error_desc))
        if hasattr(device, "alarm_code"):
            alarm_desc = AquareaSensorEntityDescription(
                key="alarm_code",
                translation_key="alarm_code",
                name="Alarm Code",
                icon="mdi:alert-octagon",
                get_state=lambda dev: getattr(dev, "alarm_code", None),
                is_available=lambda dev: getattr(dev, "alarm_code", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, alarm_desc))

        # Pump Duty
        if hasattr(device, "pump_duty"):
            pump_desc = AquareaSensorEntityDescription(
                key="pump_duty",
                translation_key="pump_duty",
                name="Pump Duty",
                icon="mdi:pump",
                state_class=SensorStateClass.MEASUREMENT,
                get_state=lambda dev: getattr(dev, "pump_duty", None),
                is_available=lambda dev: getattr(dev, "pump_duty", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, pump_desc))
            
        # Current Direction
        if hasattr(device, "current_direction"):
            dir_desc = AquareaSensorEntityDescription(
                key="current_direction",
                translation_key="current_direction",
                name="Current Direction",
                icon="mdi:directions-fork",
                get_state=lambda dev: getattr(dev, "current_direction", None),
                is_available=lambda dev: getattr(dev, "current_direction", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, dir_desc))
            
        # Special Status
        if hasattr(device, "special_status"):
            special_desc = AquareaSensorEntityDescription(
                key="special_status",
                translation_key="special_status",
                name="Special Status",
                icon="mdi:information",
                get_state=lambda dev: getattr(dev, "special_status", None),
                is_available=lambda dev: getattr(dev, "special_status", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, special_desc))
            
        # Device Mode Status
        if hasattr(device, "device_mode_status"):
            mode_desc = AquareaSensorEntityDescription(
                key="device_mode_status",
                translation_key="device_mode_status",
                name="Device Mode Status",
                icon="mdi:list-status",
                get_state=lambda dev: getattr(dev, "device_mode_status", None),
                is_available=lambda dev: getattr(dev, "device_mode_status", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, mode_desc))
            
        # Holiday Timer
        if hasattr(device, "holiday_timer"):
            hol_desc = AquareaSensorEntityDescription(
                key="holiday_timer",
                translation_key="holiday_timer",
                name="Holiday Timer",
                icon="mdi:calendar-clock",
                get_state=lambda dev: getattr(dev, "holiday_timer", None),
                is_available=lambda dev: getattr(dev, "holiday_timer", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, hol_desc))
            
        # Powerful Time
        if hasattr(device, " शक्तिशाली_time"): # Wait, typo, let me use powerful_time.
            pass
        if hasattr(device, "powerful_time"):
            pow_desc = AquareaSensorEntityDescription(
                key="powerful_time",
                translation_key="powerful_time",
                name="Powerful Time",
                icon="mdi:timer-outline",
                get_state=lambda dev: getattr(dev, "powerful_time", None),
                is_available=lambda dev: getattr(dev, "powerful_time", None) is not None,
            )
            entities.append(AquareaSensorEntity(coordinator, pow_desc))

    async_add_entities(entities)


class PanasonicSensorEntityBase(SensorEntity):
    """Base class for all sensor entities."""

    entity_description: PanasonicSensorEntityDescription  # type: ignore[override]


class PanasonicSensorEntity(PanasonicDataEntity, PanasonicSensorEntityBase):

    def __init__(
        self,
        coordinator: PanasonicDeviceCoordinator,
        description: PanasonicSensorEntityDescription,
    ):
        self.entity_description = description
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.entity_description.is_available is None:
            return False
        return self.entity_description.is_available(self.coordinator.device)

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        if self.entity_description.is_available:
            self._attr_available = self.entity_description.is_available(
                self.coordinator.device
            )
        if self.entity_description.get_state:
            self._attr_native_value = self.entity_description.get_state(
                self.coordinator.device
            )


class PanasonicEnergySensorEntity(PanasonicEnergyEntity, SensorEntity):

    entity_description: PanasonicEnergySensorEntityDescription  # type: ignore[override]

    def __init__(
        self,
        coordinator: PanasonicDeviceEnergyCoordinator,
        description: PanasonicEnergySensorEntityDescription,
    ):
        self.entity_description = description
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        value = self.entity_description.get_state(self.coordinator.energy)
        self._attr_available = value is not None
        self._attr_native_value = value


class AquareaSensorEntity(AquareaDataEntity, SensorEntity):

    entity_description: AquareaSensorEntityDescription

    def __init__(
        self,
        coordinator: AquareaDeviceCoordinator,
        description: AquareaSensorEntityDescription,
    ):
        self.entity_description = description
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        value = (
            self.entity_description.is_available(self.coordinator.device)
            if self.entity_description.is_available
            else None
        )
        return value if value is not None else False

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        if self.entity_description.is_available:
            self._attr_available = self.entity_description.is_available(
                self.coordinator.device
            )
        if self.entity_description.get_state:
            self._attr_native_value = self.entity_description.get_state(
                self.coordinator.device
            )

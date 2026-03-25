import logging
from dataclasses import dataclass
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory

from .const import DOMAIN, AQUAREA_COORDINATORS
from .base import AquareaDataEntity
from .coordinator import AquareaDeviceCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class AquareaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Aquarea binary sensor entity."""
    state_func: callable

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    entities = []
    aquarea_coordinators = hass.data[DOMAIN].get(AQUAREA_COORDINATORS, [])

    for coordinator in aquarea_coordinators:
        device = coordinator.device
        if hasattr(device, "is_on_error"):
            error_desc = AquareaBinarySensorEntityDescription(
                key="is_on_error",
                translation_key="is_on_error",
                name="Error Status",
                device_class=BinarySensorDeviceClass.PROBLEM,
                entity_category=EntityCategory.DIAGNOSTIC,
                state_func=lambda dev: getattr(dev, "is_on_error", False)
            )
            entities.append(AquareaBinarySensorEntity(coordinator, error_desc))

    async_add_entities(entities)

class AquareaBinarySensorEntity(AquareaDataEntity, BinarySensorEntity):
    entity_description: AquareaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AquareaDeviceCoordinator,
        description: AquareaBinarySensorEntityDescription,
    ):
        self.entity_description = description
        super().__init__(coordinator, description.key)

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.state_func(self.coordinator.device)

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        self._attr_is_on = self.entity_description.state_func(self.coordinator.device)

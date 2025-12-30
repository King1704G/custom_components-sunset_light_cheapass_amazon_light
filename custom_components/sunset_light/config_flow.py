"""Config flow for Sunset Light."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_MAC
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .const import CONF_PROFILE, DEFAULT_PROFILE, DOMAIN
from .protocol import list_profiles, PROFILE_HEXAGON

_LOGGER = logging.getLogger(__name__)

class SunsetLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunset Light."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def _discover_devices(self):
        service_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
        devices = {}
        for info in bluetooth.async_discovered_service_info(self.hass, connectable=True):
            uuids = {s.lower() for s in info.service_uuids}
            name = info.name or ""
            if service_uuid.lower() not in uuids and not any(
                hint in name.lower() for hint in ("hexagon", "sunset")
            ):
                continue
            label = f"{info.name or 'Unknown'} ({info.address})"
            devices[label] = info.address
        return devices

    def _guess_profile(self, name: str) -> str:
        lower = (name or "").lower()
        if "hexagon" in lower:
            return PROFILE_HEXAGON
        return DEFAULT_PROFILE

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            source = user_input.get("device_source")
            mac = None
            profile_key = user_input.get(CONF_PROFILE, DEFAULT_PROFILE)
            if source == "manual":
                mac = user_input.get(CONF_MAC)
                if not mac:
                    errors["base"] = "no_mac"
                else:
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_configured()
                    user_input[CONF_MAC] = mac
                    return self.async_create_entry(title="Sunset Light", data=user_input)
            else:
                mac = self._discover_devices().get(source)
                if not mac:
                    errors["base"] = "no_mac"
                else:
                    # If profile left at default, guess based on the label.
                    if profile_key == DEFAULT_PROFILE:
                        guessed = self._guess_profile(source or "")
                        user_input[CONF_PROFILE] = guessed
                    user_input[CONF_MAC] = mac
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title="Sunset Light", data=user_input)

        profile_options = {key: label for key, label in list_profiles()}
        discovered = self._discover_devices()
        if discovered:
            # Preselect first device and its guessed profile.
            first_label, first_addr = next(iter(discovered.items()))
            guessed_profile = self._guess_profile(first_label)
            device_options = [SelectOptionDict(value=label, label=label) for label in discovered.keys()]
            device_options.append(SelectOptionDict(value="manual", label="Manual entry"))
            data_schema = vol.Schema(
                {
                    vol.Required(
                        "device_source",
                        default=first_label,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=device_options,
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="device",
                        )
                    ),
                    vol.Required(
                        CONF_PROFILE,
                        default=guessed_profile,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=k, label=v) for k, v in profile_options.items()],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="profile",
                        )
                    ),
                    vol.Optional(CONF_MAC): TextSelector(),
                }
            )
        else:
            data_schema = vol.Schema(
                {
                    vol.Required(
                        "device_source",
                        default="manual",
                    ): SelectSelector(
                            SelectSelectorConfig(
                                options=[SelectOptionDict(value="manual", label="Manual entry")],
                                mode=SelectSelectorMode.DROPDOWN,
                                translation_key="device",
                            )
                        ),
                    vol.Required(CONF_MAC): TextSelector(),
                    vol.Required(
                        CONF_PROFILE,
                        default=DEFAULT_PROFILE,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=k, label=v) for k, v in profile_options.items()],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="profile",
                        )
                    ),
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "helper": "Choose a discovered device or select 'Manual entry' and fill Bluetooth MAC + type.",
            },
        )

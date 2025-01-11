"""Python wrapper for the Palazzetti Connection Box API."""

import json
from json.decoder import JSONDecodeError

import aiohttp

from .config import PalazzettiClientConfig
from .const import (
    API_COMMAND_URL_TEMPLATE,
    COMMAND_CHECK_ONLINE,
    COMMAND_SET_FAN_SILENT,
    COMMAND_SET_FAN_SPEED,
    COMMAND_SET_OFF,
    COMMAND_SET_ON,
    COMMAND_SET_POWER_MODE,
    COMMAND_SET_TEMPERATURE,
    COMMAND_UPDATE_PROPERTIES,
    COMMAND_UPDATE_STATE,
    REDACTED_DATA,
)
from .exceptions import CommunicationError, ValidationError
from .state import _PalazzettiAPIData, _PalazzettiState
from .temperature import TemperatureDefinition


class PalazzettiClient:
    """Interface class for the Overkiz API."""

    connected = False

    def __init__(
        self,
        hostname: str,
        session: aiohttp.ClientSession | None = None,
        config: PalazzettiClientConfig = PalazzettiClientConfig(),
    ):
        self._hostname = hostname
        self._session = session or aiohttp.ClientSession()
        self._config = config
        self._state = _PalazzettiState(config)

    async def connect(self) -> bool:
        """Connect to the device."""
        r = await self._execute_command(
            command=COMMAND_UPDATE_PROPERTIES,
            merge_state=False,
        )
        if r.success:
            self._state.merge_properties(r)
            self.connected = True
        else:
            self.connected = False
        return self.connected

    async def is_online(self) -> bool:
        """Test if the device is online."""
        if not self.connected:
            await self.connect()
        return (await self._execute_command(command=COMMAND_CHECK_ONLINE)).success

    async def update_state(self) -> bool:
        """Update the device's state."""
        # Connect if not connected yet
        if not self.connected:
            await self.connect()
        # Check if connection was successful before updating
        if self.connected:
            self.connected = (
                await self._execute_command(command=COMMAND_UPDATE_STATE)
            ).success
        return self.connected

    @property
    def sw_version(self) -> str:
        """Return the software version."""
        return self._state.sw_version

    @property
    def hw_version(self) -> str:
        """Return the hardware version"""
        return self._state.hw_version

    @property
    def has_on_off_switch(self) -> bool:
        """Return the availability of the on/of switch"""
        return self._state.has_on_off_switch

    @property
    def target_temperature(self) -> int:
        """Return the target temperature"""
        return self._state.target_temperature

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self._state.current_temperature

    @property
    def has_air_outlet_temperature(self) -> bool:
        """Return the air outlet temperature."""
        return self._state.has_air_outlet_temperature

    @property
    def air_outlet_temperature(self) -> float:
        """Return the air outlet temperature."""
        return self._state.air_outlet_temperature

    @property
    def room_temperature(self) -> float:
        """DEPRECATED - Return the room temperature."""
        return self._state.current_temperature

    @property
    def outlet_temperature(self) -> float:
        """DEPRECATED - Return the outlet temperature."""
        return self._state.air_outlet_temperature

    @property
    def has_wood_combustion_temperature(self) -> bool:
        """Return the air outlet temperature."""
        return self._state.has_wood_combustion_temperature

    @property
    def wood_combustion_temperature(self) -> float:
        """Return the wood combustion temperature."""
        return self._state.wood_combustion_temperature

    @property
    def T1(self) -> float:
        """Return the T1 temperature."""
        return self._state.T1

    @property
    def T2(self) -> float:
        """Return the T2 temperature."""
        return self._state.T2

    @property
    def T3(self) -> float:
        """Return the T3 temperature."""
        return self._state.T3

    @property
    def T4(self) -> float:
        """Return the T4 temperature."""
        return self._state.T4

    @property
    def T5(self) -> float:
        """Return the T5 temperature."""
        return self._state.T5

    def list_temperatures(self) -> list[TemperatureDefinition]:
        """Return a list of all available temperatures."""
        return self._state.list_temperatures()

    @property
    def host(self) -> str:
        """Return the host name or IP address."""
        return self._hostname

    @property
    def mac(self) -> str:
        """Return the mac address."""
        return self._state.mac

    @property
    def name(self) -> str:
        """Return the stove's name."""
        return self._state.name

    @property
    def status(self) -> int:
        """Return the stove's status."""
        return self._state.status

    @property
    def fan_speed(self) -> int:
        """Return the fan mode."""
        return self._state.main_fan_speed

    @property
    def power_mode(self) -> int:
        """Return the power mode."""
        return self._state.power_mode

    @property
    def pellet_quantity(self) -> int:
        """Return the pellet quantity."""
        return self._state.pellet_quantity

    @property
    def has_pellet_level(self) -> bool:
        """Return the availability of the pellet level."""
        return (
            self._state.has_leveltronic_pellet_sensor
            or self._state.has_capacitive_pellet_sensor
        )

    @property
    def pellet_level(self) -> float:
        """Return the pellet level."""
        return self._state.pellet_level

    @property
    def pellet_level_min(self) -> float:
        """Return the minimum pellet level."""
        return self._state.pellet_level_min

    @property
    def pellet_level_max(self) -> float:
        """Return the maximum pellet level."""
        return self._state.pellet_level_max

    @property
    def pellet_level_threshold(self) -> float:
        """Return the pellet level threshold."""
        return self._state.pellet_level_threshold

    @property
    def is_on(self) -> bool:
        """Check if the stove is on."""
        return self._state.is_on

    @property
    def is_heating(self) -> bool:
        """Check if the stove is currently heating."""
        return self._state.is_heating

    @property
    def has_fan_silent(self) -> bool:
        """Check if the fan has the silent mode available."""
        return self._state.has_fan_mode_silent

    @property
    def has_fan_high(self) -> bool:
        """Check if the fan has the high mode available."""
        return self._state.has_fan_mode_high

    @property
    def has_fan_auto(self) -> bool:
        """Check if the fan has the auto mode available."""
        return self._state.has_fan_mode_auto

    @property
    def fan_speed_min(self) -> int:
        """Return the minimum fan speed."""
        return self._state.main_fan_min

    @property
    def fan_speed_max(self) -> int:
        """Return the maximum fan speed."""
        return self._state.main_fan_max

    @property
    def target_temperature_min(self) -> int:
        """Return the minimum target temperature."""
        return self._state.target_temperature_min

    @property
    def target_temperature_max(self) -> int:
        """Return the maximum target temperature."""
        return self._state.target_temperature_max

    async def set_target_temperature(self, temperature: int) -> bool:
        """Sets the target temperature."""
        if (
            temperature >= self._state.target_temperature_min
            and temperature <= self._state.target_temperature_max
        ):
            res = await self._execute_command(
                command=COMMAND_SET_TEMPERATURE,
                parameter=temperature,
            )
            return self._state.merge_state(res)
        return False

    async def set_fan_silent(self) -> bool:
        """Set the fan to silent mode."""
        return (
            await self._execute_command(
                command=COMMAND_SET_FAN_SILENT, merge_state=True
            )
        ).success

    async def set_fan_high(self) -> bool:
        """Set the fan to high mode."""
        return await self.set_fan_speed(6)

    async def set_fan_auto(self) -> bool:
        """Set the fan to auto mode."""
        return await self.set_fan_speed(7)

    async def set_fan_speed(self, fan_speed: int) -> bool:
        """Set the fan speed."""
        if (
            (self._state.main_fan_min <= fan_speed <= self._state.main_fan_max)
            or (fan_speed == 6 and self._state.has_fan_mode_high)
            or (fan_speed == 7 and self._state.has_fan_mode_auto)
        ):
            return (
                await self._execute_command(
                    command=COMMAND_SET_FAN_SPEED, parameter=fan_speed, merge_state=True
                )
            ).success
        raise ValidationError(f"Main fan speed ({fan_speed}) out of range.")

    async def set_power_mode(self, power: int) -> bool:
        """Set the power mode."""
        if 1 <= power <= 5:
            return (
                await self._execute_command(
                    command=COMMAND_SET_POWER_MODE,
                    parameter=power,
                )
            ).success
        raise ValidationError(f"Power mode ({power}) out of range.")

    async def set_on(self, on: bool) -> bool:
        """Set the stove on or off."""
        if self._state.has_on_off_switch:
            return (
                await self._execute_command(
                    command=COMMAND_SET_ON if on else COMMAND_SET_OFF,
                )
            ).success
        raise ValidationError("Main operation switch not available.")

    async def _execute_command(
        self,
        command: str,
        parameter: str | int = None,
        merge_state=True,
    ) -> _PalazzettiAPIData:
        request_url = API_COMMAND_URL_TEMPLATE.format(
            host=self._hostname,
            command_and_parameter=f"{command} {parameter}" if parameter else command,
        )

        try:
            async with self._session.get(request_url) as response:
                payload = _PalazzettiAPIData(await response.text())
        except (TypeError, JSONDecodeError) as ex:
            self.connected = False
            raise CommunicationError("Invalid API response") from ex
        except aiohttp.ClientError as ex:
            self.connected = False
            raise CommunicationError("API communication error") from ex

        if merge_state:
            self._state.merge_state(payload)
        return payload

    def to_json(self, redact: bool = False) -> str:
        """Return a snapshot of the client as a json string."""
        return json.dumps(self.to_dict(redact))

    def to_dict(
        self,
        redact: bool = False,
    ) -> dict[str, bool | dict[str, str | bool | int | float | list[int | str]]]:
        """Return a snapshot of the client as a dict."""
        data = {
            "host": self._hostname,
            "connected": self.connected,
            "state": self._state.to_dict(),
        }

        if redact:
            redacted = {
                "DNS": [REDACTED_DATA],
                "EADDR": REDACTED_DATA,
                "EGW": REDACTED_DATA,
                "EMAC": REDACTED_DATA,
                "GATEWAY": REDACTED_DATA,
                "MAC": REDACTED_DATA,
                "SN": REDACTED_DATA,
                "WADR": REDACTED_DATA,
                "WBCST": REDACTED_DATA,
                "WMAC": REDACTED_DATA,
                "WGW": REDACTED_DATA,
                "WSSID": REDACTED_DATA,
            }
            data["host"] = REDACTED_DATA
            data["state"]["properties"] = data["state"]["properties"] | redacted
            data["state"]["attributes"] = data["state"]["attributes"] | redacted

        return data

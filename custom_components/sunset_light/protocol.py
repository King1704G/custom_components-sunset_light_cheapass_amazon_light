"""Protocol profiles for Sunset Light devices."""

import colorsys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


def _checksum(packet: Iterable[int]) -> int:
    """Compute checksum: one's complement of folded sum."""
    total = sum(packet)
    while total > 0xFF:
        total = (total >> 8) + (total & 0xFF)
    return (~total) & 0xFF


def _build_packet(cmd: int, payload: bytes = b"") -> bytes:
    total_length = 5 + len(payload)
    data = bytearray([0x55, cmd, 0xFF, total_length])
    data.extend(payload)
    data.append(_checksum(data))
    return bytes(data)


@dataclass
class ProtocolProfile:
    name: str
    service_uuid: str
    write_char_uuid: str
    notify_char_uuid: str
    effect_list: List[str]

    def build_power(self, on: bool) -> List[bytes]:
        raise NotImplementedError

    def build_color(self, r: int, g: int, b: int) -> List[bytes]:
        raise NotImplementedError

    def build_brightness(self, brightness_ha: int) -> List[bytes]:
        raise NotImplementedError

    def build_scene(self, scene_name: str) -> List[bytes]:
        raise NotImplementedError

    def build_white(self) -> List[bytes]:
        return self.build_color(255, 255, 255)


class SunsetLightProfile(ProtocolProfile):
    """Original Sunset Light behavior (default)."""

    def __init__(self) -> None:
        self.name = "Sunset Light"
        self.service_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
        self.write_char_uuid = "0000fff3-0000-1000-8000-00805f9b34fb"
        self.notify_char_uuid = "0000fff4-0000-1000-8000-00805f9b34fb"
        self.effect_list = [
            "Fantasy", "Sunset", "Forest", "Ghost", "Sunrise",
            "Midsummer", "Tropicaltwilight", "Green Prairie", "Rubyglow",
            "Aurora", "Savanah", "Alarm", "Lake Placid", "Neon",
            "Sundowner", "Bluestar", "Redrose", "Rating", "Disco", "Autumn",
        ]
        self._scene_params: Dict[str, bytes] = {
            "green prairie": b"\x81",
            "ghost": b"\x84",
            "disco": b"\x87",
            "alarm": b"\x88",
            "savanah": b"\x8B",
            "fantasy": b"\x80",
            "sunset": b"\x82",
            "forest": b"\x82",
            "sunrise": b"\x83",
            "midsummer": b"\x85",
            "tropicaltwilight": b"\x86",
            "rubyglow": b"\x89",
            "aurora": b"\x89",
            "lake placid": b"\x8C",
            "neon": b"\x8D",
            "sundowner": b"\x8E",
            "bluestar": b"\x8F",
            "redrose": b"\x90",
            "rating": b"\x91",
            "autumn": b"\x93",
        }

    def build_power(self, on: bool) -> List[bytes]:
        return [_build_packet(0x01, b"\x01" if on else b"\x00")]

    def build_color(self, r: int, g: int, b: int) -> List[bytes]:
        return [_build_packet(0x03, bytes([r, g, b]))]

    def build_brightness(self, brightness_ha: int) -> List[bytes]:
        value = int(brightness_ha / 255 * 100)
        value = max(0, min(100, value))
        return [_build_packet(0x05, bytes([value]))]

    def build_scene(self, scene_name: str) -> List[bytes]:
        payload = self._scene_params.get(scene_name.lower())
        if payload is None:
            return []
        return [_build_packet(0x06, payload)]


class HexagonProfile(ProtocolProfile):
    """Hexagon variant observed via captures."""

    def __init__(self) -> None:
        self.name = "Hexagon Light"
        self.service_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
        self.write_char_uuid = "0000fff3-0000-1000-8000-00805f9b34fb"
        self.notify_char_uuid = "0000fff4-0000-1000-8000-00805f9b34fb"

        # IDs from full-app capture (classic + festival + other)
        self._classic_ids = [
            0x0002, 0x0003, 0x0004, 0x0007, 0x0010, 0x0017, 0x002D, 0x0023, 0x0037,
            0x000D, 0x0030, 0x0047, 0x005B, 0x006D, 0x0071, 0x003B, 0x001A, 0x0020,
        ]
        self._festival_ids = [
            0x0008, 0x000B, 0x0066, 0x0005, 0x0074, 0x006F, 0x0006, 0x000C, 0x001D,
            0x0001, 0x0009, 0x000A, 0x000E, 0x000F, 0x0011,
        ]
        all_ids = set(range(1, 0x76))
        all_ids.difference_update(self._classic_ids)
        all_ids.difference_update(self._festival_ids)
        self._other_ids = sorted(all_ids)

        classic_names = [
            "Symphony", "Energy", "Jump", "Vitality", "Accumulation", "Chase",
            "Space-time", "Ephemeral", "Flow", "Forest", "Neon Lights", "Green Jade",
            "Running", "Pink Light", "Alarm", "Aurora", "Rainbow", "Melody",
        ]
        festival_names = [
            "Christmas", "Halloween", "Valentine's Day", "New Year", "Candlelight",
            "Birthday", "Ghost", "Party", "Carnival", "Disco", "Sweet", "Romantic",
            "Dating", "Ball", "Game",
        ]
        other_names = [
            "Cycling", "Fantasy color", "Seven-color energy", "Seven-color jump", "Red-green-blue jump",
            "Yellow-cyan-purple jump", "Seven-color strobe", "Red-green-blue strobe", "Yellow-cyan-purple strobe",
            "Seven-color gradient", "Red-yellow alternating gradient", "Red-purple alternating gradient",
            "Green-cyan alternating gradient", "Green-yellow alternating gradient", "Blue-purple alternating gradient",
            "Red accumulation", "Green accumulation", "Blue accumulation", "Yellow accumulation", "Cyan accumulation",
            "Purple accumulation", "White accumulation", "Seven-color chase", "Red-green-blue chase",
            "Yellow-cyan-purple chase", "Seven-color drift", "Red-green-blue drift", "Yellow-cyan-purple drift",
            "Seven-color brushing", "Red-green-blue brushing", "Yellow-cyan brushing", "Seven-color melody closing",
            "Red-green-blue melody closing", "Yellow-cyan-purple melody closing", "Seven-color opening and closing",
            "Red-green-blue opening and closing", "Yellow-cyan-purple opening and closing", "Red opening and closing",
            "Green opening and closing", "Blue opening and closing", "Yellow opening and closing",
            "Cyan opening and closing", "Purple opening and closing", "White opening and closing",
            "Seven-color light and dark transition", "Red-green-blue light and dark transition",
            "Purple-cyan-yellow light and dark transition", "Six-color dark transition red",
            "Six-color dark transition green", "Six-color dark transition blue", "Six-color dark transition cyan",
            "Six-color dark transition yellow", "Six-color dark transition purple", "Six-color dark transition white",
            "Seven-color flowing water", "Red-green-blue flowing water", "Cyan-yellow-purple flowing water",
            "Red-green flowing water", "Green-blue flowing water", "Yellow-blue flowing water",
            "Yellow-cyan flowing water", "Cyan-purple flowing water", "Black-and-white flowing water",
            "White-red-white flow", "White-green-white flow", "White-blue-white flow", "White-yellow-white flow",
            "White-cyan-white flow", "White-purple-white flow", "Red-white-red flow", "Green-white-green flow",
            "Blue-white-blue flow", "Yellow-white-yellow flow", "Cyan-white-cyan flow", "Purple-white-purple flow",
        ]

        classic = {classic_names[i]: sid for i, sid in enumerate(self._classic_ids)}
        festival = {festival_names[i]: sid for i, sid in enumerate(self._festival_ids)}
        other = {name: sid for name, sid in zip(other_names, self._other_ids)}
        if len(other) < len(self._other_ids):
            start = len(other)
            for idx, sid in enumerate(self._other_ids[start:], start + 1):
                other[f"Other {idx:02d} (id {sid})"] = sid

        self._scene_map: Dict[str, int] = {}
        for mapping in (classic, festival, other):
            self._scene_map.update({k.lower(): v for k, v in mapping.items()})

        self.effect_list = list(classic.keys()) + list(festival.keys()) + list(other.keys())
        self._default_scene_param = 0x3200

    def _int_to_bytes_be(self, value: int, width: int = 2) -> bytes:
        return value.to_bytes(width, byteorder="big", signed=False)

    def build_power(self, on: bool) -> List[bytes]:
        return [_build_packet(0x01, b"\x01" if on else b"\x00")]

    def build_brightness(self, brightness_ha: int) -> List[bytes]:
        scaled = int(brightness_ha / 255 * 1000)
        scaled = max(0, min(1000, scaled))
        return [_build_packet(0x05, self._int_to_bytes_be(scaled))]

    def build_color(self, r: int, g: int, b: int) -> List[bytes]:
        h, s, _v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        hue_deg = int(h * 360)
        sat = int(s * 1000)
        return [_build_packet(0x03, self._int_to_bytes_be(hue_deg) + self._int_to_bytes_be(sat))]

    def build_scene(self, scene_name: str) -> List[bytes]:
        scene_id = self._scene_map.get(scene_name.lower())
        if scene_id is None:
            return []
        packets = [
            _build_packet(0x06, self._int_to_bytes_be(scene_id)),
            _build_packet(0x0F, self._int_to_bytes_be(self._default_scene_param)),
        ]
        return packets


PROFILE_SUNSET = "sunset_light"
PROFILE_HEXAGON = "hexagon_light"


def get_profile(profile_key: Optional[str]) -> ProtocolProfile:
    if profile_key == PROFILE_HEXAGON:
        return HexagonProfile()
    return SunsetLightProfile()


def list_profiles() -> List[tuple[str, str]]:
    return [
        (PROFILE_SUNSET, "Sunset Light"),
        (PROFILE_HEXAGON, "Hexagon Light"),
    ]

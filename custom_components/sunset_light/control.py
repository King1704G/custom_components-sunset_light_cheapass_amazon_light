
from typing import Iterable

from .protocol import ProtocolProfile


async def _send_packets(client, packets: Iterable[bytes], write_uuid: str):
    for packet in packets:
        await client.write_gatt_char(write_uuid, packet)


async def turn_on(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_power(True), profile.write_char_uuid)


async def turn_off(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_power(False), profile.write_char_uuid)


async def set_white(client, profile: ProtocolProfile):
    await _send_packets(client, profile.build_white(), profile.write_char_uuid)


async def set_scene(client, profile: ProtocolProfile, scene_name: str):
    packets = profile.build_scene(scene_name)
    if packets:
        await _send_packets(client, packets, profile.write_char_uuid)


async def set_color(client, profile: ProtocolProfile, r: int, g: int, b: int):
    await _send_packets(client, profile.build_color(r, g, b), profile.write_char_uuid)


async def set_brightness(client, profile: ProtocolProfile, brightness: int):
    await _send_packets(client, profile.build_brightness(brightness), profile.write_char_uuid)


async def set_scene_id(client, profile: ProtocolProfile, scene_id: int, param: int | None):
    if hasattr(profile, "build_scene_by_id"):
        await _send_packets(client, profile.build_scene_by_id(scene_id, param), profile.write_char_uuid)


async def set_music_mode(client, profile: ProtocolProfile, mode):
    if hasattr(profile, "build_music_mode"):
        await _send_packets(client, profile.build_music_mode(mode), profile.write_char_uuid)


async def set_music_sensitivity(client, profile: ProtocolProfile, value: int):
    if hasattr(profile, "build_music_sensitivity"):
        await _send_packets(client, profile.build_music_sensitivity(value), profile.write_char_uuid)


async def set_schedule(
    client,
    profile: ProtocolProfile,
    on_enabled: bool,
    on_hour: int,
    on_minute: int,
    on_days_mask: int,
    off_enabled: bool,
    off_hour: int,
    off_minute: int,
    off_days_mask: int,
):
    if hasattr(profile, "build_schedule"):
        await _send_packets(
            client,
            profile.build_schedule(
                on_enabled,
                on_hour,
                on_minute,
                on_days_mask,
                off_enabled,
                off_hour,
                off_minute,
                off_days_mask,
            ),
            profile.write_char_uuid,
        )

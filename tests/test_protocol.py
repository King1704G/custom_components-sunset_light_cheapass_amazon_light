import pytest

from custom_components.sunset_light.protocol import (
    SunsetLightProfile,
    HexagonProfile,
)


def test_sunset_packets():
    p = SunsetLightProfile()
    on_pkt = p.build_power(True)[0]
    off_pkt = p.build_power(False)[0]
    assert on_pkt[1] == 0x01 and on_pkt[-1] != 0  # checksum present
    assert off_pkt[1] == 0x01
    color_pkt = p.build_color(1, 2, 3)[0]
    assert color_pkt[1] == 0x03
    scene = p.build_scene("ghost")[0]
    assert scene[1] == 0x06


def test_hexagon_packets():
    p = HexagonProfile()
    on_pkt = p.build_power(True)[0]
    assert on_pkt[1] == 0x01
    color_pkt = p.build_color(255, 0, 0)[0]
    assert color_pkt[1] == 0x03
    scene_packets = p.build_scene("Symphony")
    assert scene_packets and scene_packets[0][1] == 0x06

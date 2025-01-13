import json
from typing import Any

import pytest

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.cli import as_json, parse_bytes
from crystalfontz.device import CFA533Status
from crystalfontz.keys import KeyState, KeyStates, KP_UP
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
    GpioRead,
    KeypadPolled,
    LcdMemory,
    Versions,
)


@pytest.mark.parametrize(
    "text,buffer",
    [
        ("hello world", b"hello world"),
        ("\\\\", b"\\"),
        ("\\a", b"\a"),
        ("\\o333", (0o333).to_bytes(1, "big")),
        ("\\o22", (0o22).to_bytes(1, "big")),
        ("\\xff", b"\xff"),
        ("\\", b"\\"),
        ("\\s", b"\\s"),
        ("\\xf", b"\\xf"),
    ],
)
@pytest.mark.filterwarnings("ignore:invalid escape sequence")
def test_parse_bytes(text, buffer) -> None:
    assert parse_bytes(text) == buffer


OBJECTS = [
    Versions(b"CFA533: h1.4, u1v2"),
    LcdMemory(b"\xff\x00\x01\x02\x03\x04\x05\x06\x07"),
    DowDeviceInformation(b"\xff\x00\x01\x02\x03\x04\x05\x06\x07"),
    DowTransactionResult(b"\xff\x01\x02\x03\x04\x05\x06\x07\xff"),
    KeypadPolled(bytes([KP_UP, KP_UP, KP_UP])),
    CFA533Status(
        temperature_sensors_enabled={1, 2},
        key_states=KeyStates(
            up=KeyState(pressed=False, pressed_since=True, released_since=True),
            enter=KeyState(pressed=False, pressed_since=True, released_since=True),
            exit=KeyState(pressed=False, pressed_since=True, released_since=True),
            left=KeyState(pressed=False, pressed_since=True, released_since=True),
            right=KeyState(pressed=False, pressed_since=True, released_since=True),
            down=KeyState(pressed=False, pressed_since=True, released_since=True),
        ),
        atx_power_switch_functionality_settings=AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunction.KEYPAD_RESET},
            auto_polarity=True,
            reset_invert=False,
            power_invert=False,
            power_pulse_length_seconds=1.0,
        ),
        watchdog_counter=0,
        contrast=0.5,
        keypad_brightness=0.5,
        atx_sense_on_floppy=False,
        cfa633_contrast=0.5,
        lcd_brightness=0.5,
    ),
    GpioRead(bytes([0xFF, 0b0111, 0x11, 0b1101])),
    b"\01",
]


@pytest.mark.parametrize("obj", OBJECTS)
def test_repr(obj: Any, snapshot) -> None:
    assert repr(obj) == snapshot


@pytest.mark.parametrize("obj", OBJECTS)
def test_json(obj: Any, snapshot) -> None:
    assert json.dumps(as_json(obj)) == snapshot

#!/usr/bin/env python3
"""
Test 04: ReadTemperature
Tests temperature sensor reading.
"""

import os
import pytest
from st3215 import ST3215


@pytest.fixture(scope="module")
def device():
    dev = os.getenv("ST3215_DEV")
    if not dev:
        pytest.skip("ST3215_DEV not set; skipping hardware integration tests")
    return dev


@pytest.fixture(scope="module")
def servo(device):
    s = ST3215(device)
    yield s
    try:
        s.portHandler.closePort()
    except Exception:
        pass


def test_read_temperature(servo):
    sid = 1
    temp = servo.ReadTemperature(sid)
    assert temp is not None and isinstance(temp, int)
    assert -40 <= temp <= 150

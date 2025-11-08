#!/usr/bin/env python3
"""
Test 03: ReadLoad + ReadVoltage + ReadCurrent
Tests telemetry reading functions.
Special Instructions: Apply physical force to servo shaft before running.
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


def test_read_load_voltage_current(servo):
    """Read load, voltage and current and assert they are numeric and within reasonable ranges."""
    sid = 1
    load = servo.ReadLoad(sid)
    voltage = servo.ReadVoltage(sid)
    current = servo.ReadCurrent(sid)

    assert load is not None and isinstance(load, float)
    assert 0.0 <= load <= 100.0

    assert voltage is not None and isinstance(voltage, float)
    assert 0.0 <= voltage <= 30.0

    assert current is not None and isinstance(current, float)
    assert 0.0 <= current <= 10000.0

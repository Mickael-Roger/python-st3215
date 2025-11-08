#!/usr/bin/env python3
"""
Test 08: ReadStatus
Tests servo status reading.
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


def test_read_status(servo):
    sid = 1
    status = servo.ReadStatus(sid)
    assert status is not None and isinstance(status, dict)
    # Expect keys from implementation
    expected_keys = {"Voltage","Sensor","Temperature","Current","Angle","Overload"}
    assert expected_keys.issubset(set(status.keys()))

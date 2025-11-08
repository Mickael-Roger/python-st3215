#!/usr/bin/env python3
"""
Test 01: PingServo
Tests basic communication with servo ID 1.
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


def test_ping_servo(servo):
    """Ping servo with ID 1 and expect a boolean success response."""
    assert servo.PingServo(1) is True

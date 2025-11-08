#!/usr/bin/env python3
"""
Test 02: ListServos
Scans the bus for all connected servos.
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


def test_list_servos(servo):
    """List servos and assert that it returns a non-empty list containing ID 1."""
    servos = servo.ListServos()
    assert isinstance(servos, list)
    assert len(servos) > 0
    assert 1 in servos

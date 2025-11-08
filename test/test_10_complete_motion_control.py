#!/usr/bin/env python3
"""
Test 10: Complete Motion Control
Comprehensive test of servo control functions.
Tests StartServo, SetAcceleration, SetSpeed, rotation mode, position mode, and StopServo.
"""

import os
import time
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


def test_complete_motion_control(servo):
    sid = 1

    # Start servo
    assert servo.StartServo(sid) is not None

    # Set acceleration and speed
    assert servo.SetAcceleration(sid, 100) is not None
    assert servo.SetSpeed(sid, 2000) is not None

    # Test rotation for a short time (if supported by hardware)
    assert servo.Rotate(sid, 500) is not None
    time.sleep(1)
    assert servo.Rotate(sid, -500) is not None
    time.sleep(1)

    # Position control: move +500 and back
    curr = servo.ReadPosition(sid)
    assert curr is not None and isinstance(curr, int)

    target1 = curr + 500
    assert servo.MoveTo(sid, target1, speed=1500, acc=80, wait=True) is not None

    target2 = curr - 500
    assert servo.MoveTo(sid, target2, speed=1500, acc=80, wait=True) is not None

    assert servo.MoveTo(sid, curr, speed=1500, acc=80, wait=True) is not None

    # Stop servo
    assert servo.StopServo(sid) is not None


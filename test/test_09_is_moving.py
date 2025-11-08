#!/usr/bin/env python3
"""
Test 09: IsMoving
Tests motion detection.
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


def wait_for_stop(servo, sid, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        moving = servo.IsMoving(sid)
        if moving is False:
            return True
        time.sleep(0.05)
    return False


def test_is_moving_detection(servo):
    """Test motion detection API: IsMoving before, during and after a commanded move."""
    sid = 1

    # Initial state: expect a boolean (may be True or False depending on servo)
    initial = servo.IsMoving(sid)
    assert initial is not None and isinstance(initial, bool)

    # Start servo
    started = servo.StartServo(sid)
    assert started is not None

    # Read current position
    curr = servo.ReadPosition(sid)
    assert curr is not None and isinstance(curr, int)

    # Initiate a non-blocking small move
    target = curr + 100
    moved = servo.MoveTo(sid, target, speed=1000, acc=50, wait=False)
    assert moved is not None

    # Short delay to let movement start
    time.sleep(0.1)
    during = servo.IsMoving(sid)
    assert during is not None and isinstance(during, bool)

    # Wait for movement to finish
    finished = wait_for_stop(servo, sid, timeout=10.0)
    assert finished, "Servo did not stop within timeout"

    # Final check
    final = servo.IsMoving(sid)
    assert final is not None and final is False

    # Stop servo
    stopped = servo.StopServo(sid)
    assert stopped is not None

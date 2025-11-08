#!/usr/bin/env python3
"""
Test 07: ReadCorrection
Tests position correction reading.
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


def test_read_correction(servo):
    sid = 1
    corr = servo.ReadCorrection(sid)
    assert corr is not None and isinstance(corr, int)
    assert -2047 <= corr <= 2047

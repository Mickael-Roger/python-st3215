# -*- coding: utf-8 -*-
"""Custom exceptions and error message helpers for the st3215 package.

This module provides a small set of exception types and helper functions
that standardize messages for communication results and servo status bits.
"""
from typing import Dict


class ST3215Error(Exception):
    """Base exception for st3215-related errors."""


class PortError(ST3215Error):
    """Errors related to serial port operations."""


class PacketError(ST3215Error):
    """Errors related to packet construction, transmission or parsing."""


class TimeoutError(ST3215Error):
    """Packet or response timeout occurred."""


class CommunicationError(ST3215Error):
    """General communication errors with servos."""


class ServoError(ST3215Error):
    """Errors reported by the servo itself (status packet errors)."""


class ValidationError(ST3215Error):
    """Input validation errors (e.g., invalid servo ID, out of range values)."""


# Keep a mapping for the communication result constants to human-readable messages.
COMM_RESULTS: Dict[int, str] = {
    0: "Communication success!",
    -1: "Port is in use!",
    -2: "Failed transmit instruction packet!",
    -3: "Failed to get status packet from device!",
    -4: "Incorrect instruction packet!",
    -5: "Now receiving status packet!",
    -6: "There is no status packet (timeout)!",
    -7: "Incorrect status packet (corrupt)!",
    -9: "Function not available for this protocol or ID!",
}


def comm_result_message(code: int) -> str:
    """Return a compact human readable message for a communication result code.

    Args:
        code: communication result code (use the COMM_* constants from values.py)

    Returns:
        A short descriptive string for logging or exceptions.
    """
    return COMM_RESULTS.get(code, "")


# Servo/packet error bit descriptions
_SERVO_ERROR_BITS = {
    1: "Input voltage error",
    2: "Angle sensor error",
    4: "Overheat error",
    8: "Over voltage / electrical error",
    32: "Overload error",
}


def servo_error_message(error_bits: int) -> str:
    """Return a combined, human friendly message for servo error bits.

    Args:
        error_bits: bitfield from the servo status packet.

    Returns:
        A comma separated description of present error bits or an empty string.
    """
    parts = []
    for bit, msg in _SERVO_ERROR_BITS.items():
        if error_bits & bit:
            parts.append(msg)
    return ", ".join(parts)


def raise_comm_error(comm_result: int, context: str = "") -> None:
    """Raise an appropriate exception based on the communication result code.

    Args:
        comm_result: The communication result code from packet operations.
        context: Additional context about what operation failed.

    Raises:
        Appropriate ST3215Error subclass based on the error code.
    """
    if comm_result == 0:  # COMM_SUCCESS
        return

    msg = comm_result_message(comm_result)
    if context:
        msg = f"{context}: {msg}"

    if comm_result == -1:  # COMM_PORT_BUSY
        raise PortError(msg)
    elif comm_result == -2:  # COMM_TX_FAIL
        raise PacketError(msg)
    elif comm_result == -3:  # COMM_RX_FAIL
        raise PacketError(msg)
    elif comm_result == -4:  # COMM_TX_ERROR
        raise PacketError(msg)
    elif comm_result == -6:  # COMM_RX_TIMEOUT
        raise TimeoutError(msg)
    elif comm_result == -7:  # COMM_RX_CORRUPT
        raise PacketError(msg)
    elif comm_result == -9:  # COMM_NOT_AVAILABLE
        raise CommunicationError(msg)
    else:
        raise CommunicationError(msg)


def raise_servo_error(error_bits: int, context: str = "") -> None:
    """Raise a ServoError if error bits are set.

    Args:
        error_bits: The error bitfield from servo status packet.
        context: Additional context about what operation failed.

    Raises:
        ServoError if any error bits are set.
    """
    if error_bits == 0:
        return

    msg = servo_error_message(error_bits)
    if context:
        msg = f"{context}: {msg}"
    raise ServoError(msg)

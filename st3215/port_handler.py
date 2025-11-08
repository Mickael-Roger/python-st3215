import time
import serial
import sys
import logging
from typing import Optional, Union

from .values import *
from .errors import PortError

logger = logging.getLogger(__name__)


class PortHandler(object):
    def __init__(self, port_name: str):
        self.is_open: bool = False
        self.baudrate: int = DEFAULT_BAUDRATE
        self.packet_start_time: float = 0.0
        self.packet_timeout: float = 0.0
        self.tx_time_per_byte: float = 0.0

        self.is_using: bool = False
        self.port_name: str = port_name
        self.ser = None  # type: Optional[serial.Serial]

    def port_open(self) -> bool:
        logger.debug(f"Opening port: {self.port_name}")
        return self.port_setup()

    def port_close(self) -> None:
        logger.debug(f"Closing port: {self.port_name}")
        if self.ser is not None:
            self.ser.close()
        self.is_open = False
        logger.info(f"Port closed: {self.port_name}")

    def port_clear(self) -> None:
        if self.ser is not None:
            # flush the input buffer
            self.ser.flush()

    def port_set_name(self, port_name: str) -> None:
        self.port_name = port_name

    def port_get_name(self) -> str:
        return self.port_name

    def get_baud_rate(self) -> int:
        return self.baudrate

    def get_bytes_available(self) -> int:
        # may raise AttributeError if port is not open
        return self.ser.in_waiting if self.ser is not None else 0

    def port_read(self, length: int) -> Union[bytes, list]:
        # return raw bytes on Python3, keep legacy list behaviour for older Python
        if sys.version_info > (3, 0):
            return self.ser.read(length) if self.ser is not None else b""
        else:
            return (
                [ord(ch) for ch in self.ser.read(length)]
                if self.ser is not None
                else []
            )

    def port_write(self, packet: bytes) -> int:
        if self.ser is None:
            logger.error("Attempted to write to closed serial port")
            raise PortError("Serial port not opened")
        try:
            bytes_written = self.ser.write(packet)
            logger.debug(f"Wrote {bytes_written} bytes to port")
            return bytes_written
        except Exception as e:
            logger.error(f"Failed to write to port: {e}")
            raise PortError(f"Failed to write to port: {e}")

    def set_packet_timeout(self, packet_length: int) -> None:
        self.packet_start_time = self.get_current_time()
        self.packet_timeout = (
            (self.tx_time_per_byte * packet_length)
            + (self.tx_time_per_byte * 3.0)
            + LATENCY_TIMER
        )

    def set_packet_timeout_millis(self, msec: float) -> None:
        self.packet_start_time = self.get_current_time()
        self.packet_timeout = msec

    def is_packet_timeout(self) -> bool:
        if self.get_time_since_start() > self.packet_timeout:
            self.packet_timeout = 0
            return True

        return False

    def get_current_time(self) -> float:
        # use microsecond precision
        return time.time() * 1000.0

    def get_time_since_start(self) -> float:
        time_since = self.get_current_time() - self.packet_start_time
        if time_since < 0.0:
            self.packet_start_time = self.get_current_time()

        return time_since

    def port_setup(self) -> bool:
        try:
            if self.is_open:
                logger.debug("Port already open, closing before reopening")
                self.port_close()

            logger.info(
                f"Setting up serial port: {self.port_name} at {self.baudrate} baud"
            )
            self.ser = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                timeout=0,
            )

            self.is_open = True

            # reset input buffer if available
            if hasattr(self.ser, "reset_input_buffer"):
                self.ser.reset_input_buffer()
                logger.debug("Input buffer reset")

            # time to transmit one byte in milliseconds * 10 (start/stop bits) ((1000/baudrate) * 10)
            self.tx_time_per_byte = 10000.0 / self.baudrate

            logger.info(f"Successfully opened port: {self.port_name}")
            return True
        except Exception as exc:
            logger.error(f"Failed to open serial port '{self.port_name}': {exc}")
            raise PortError(f"Failed to open serial port '{self.port_name}': {exc}")

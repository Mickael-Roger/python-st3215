import logging
from typing import List, Tuple, Optional
from .values import *
from .errors import comm_result_message, servo_error_message

logger = logging.getLogger(__name__)


def sts_tohost(a: int, b: int) -> int:
    if a & (1 << b):
        return -(a & ~(1 << b))
    else:
        return a


def sts_toscs(a: int, b: int) -> int:
    if a < 0:
        return -a | (1 << b)
    else:
        return a


def sts_makedword(a: int, b: int) -> int:
    return (a & 0xFFFF) | (b & 0xFFFF) << 16


def sts_loword(l: int) -> int:
    return l & 0xFFFF


def sts_hiword(h: int) -> int:
    return (h >> 16) & 0xFFFF


def get_protocol_version() -> float:
    return 1.0


def get_tx_rx_result(result: int) -> str:
    # Provide a standardized message using errors.comm_result_message
    msg = comm_result_message(result)
    if msg:
        return f"[TxRxResult] {msg}"
    return ""


def get_rx_packet_error(error: int) -> str:
    # Return a standardized servo error message
    if error == 0:
        return ""
    msg = servo_error_message(error)
    if msg:
        return f"[ServoStatus] {msg}!"
    return ""


class ProtocolPacketHandler(object):
    def __init__(self, port_handler):
        # self.sts_setend(protocol_end)# STServo bit end(STS/SMS=0, SCS=1)
        self.portHandler = port_handler
        self.sts_end = 0

    def sts_getend(self) -> int:
        return self.sts_end

    def sts_setend(self, e: int) -> None:
        self.sts_end = e

    def sts_makeword(self, a: int, b: int) -> int:
        if self.sts_end == 0:
            return (a & 0xFF) | ((b & 0xFF) << 8)
        else:
            return (b & 0xFF) | ((a & 0xFF) << 8)

    def sts_lobyte(self, w: int) -> int:
        if self.sts_end == 0:
            return w & 0xFF
        else:
            return (w >> 8) & 0xFF

    def sts_hibyte(self, w: int) -> int:
        if self.sts_end == 0:
            return (w >> 8) & 0xFF
        else:
            return w & 0xFF

    def packet_tx(self, txpacket: List[int]) -> int:
        checksum = 0
        total_packet_length = txpacket[PKT_LENGTH] + 4  # 4: HEADER0 HEADER1 ID LENGTH

        if self.portHandler.is_using:
            logger.warning("Port is busy, cannot transmit packet")
            return COMM_PORT_BUSY
        self.portHandler.is_using = True

        # check max packet length
        if total_packet_length > TXPACKET_MAX_LEN:
            logger.error(
                f"Packet length {total_packet_length} exceeds maximum {TXPACKET_MAX_LEN}"
            )
            self.portHandler.is_using = False
            return COMM_TX_ERROR

        # make packet header
        txpacket[PKT_HEADER_0] = 0xFF
        txpacket[PKT_HEADER_1] = 0xFF

        # add a checksum to the packet
        for idx in range(2, total_packet_length - 1):  # except header, checksum
            checksum += txpacket[idx]

        txpacket[total_packet_length - 1] = ~checksum & 0xFF

        logger.debug(
            f"Transmitting packet to ID {txpacket[PKT_ID]}: length={total_packet_length}"
        )

        # tx packet
        self.portHandler.port_clear()
        written_packet_length = self.portHandler.port_write(txpacket)
        if total_packet_length != written_packet_length:
            logger.error(
                f"Packet transmission failed: expected {total_packet_length} bytes, wrote {written_packet_length}"
            )
            self.portHandler.is_using = False
            return COMM_TX_FAIL

        logger.debug(f"Successfully transmitted packet ({written_packet_length} bytes)")
        return COMM_SUCCESS

    def packet_rx(self) -> Tuple[List[int], int]:
        rxpacket: List[int] = []

        result = COMM_TX_FAIL
        checksum = 0
        rx_length = 0
        wait_length = 6  # minimum length (HEADER0 HEADER1 ID LENGTH ERROR CHKSUM)

        logger.debug("Waiting for response packet...")

        while True:
            rxpacket.extend(self.portHandler.port_read(wait_length - rx_length))
            rx_length = len(rxpacket)
            if rx_length >= wait_length:
                # find packet header
                idx = 0
                for idx in range(0, (rx_length - 1)):
                    if (rxpacket[idx] == 0xFF) and (rxpacket[idx + 1] == 0xFF):
                        break

                if idx == 0:  # found at the beginning of the packet
                    if (
                        (rxpacket[PKT_ID] > 0xFD)
                        or (rxpacket[PKT_LENGTH] > RXPACKET_MAX_LEN)
                        or (rxpacket[PKT_ERROR] > 0x7F)
                    ):
                        # unavailable ID or unavailable Length or unavailable Error
                        # remove the first byte in the packet
                        logger.debug("Invalid packet header, removing first byte")
                        del rxpacket[0]
                        rx_length -= 1
                        continue

                    # re-calculate the exact length of the rx packet
                    if wait_length != (rxpacket[PKT_LENGTH] + PKT_LENGTH + 1):
                        wait_length = rxpacket[PKT_LENGTH] + PKT_LENGTH + 1
                        logger.debug(f"Adjusted wait length to {wait_length}")
                        continue

                    if rx_length < wait_length:
                        # check timeout
                        if self.portHandler.is_packet_timeout():
                            if rx_length == 0:
                                logger.warning(
                                    "Packet reception timeout: no data received"
                                )
                                result = COMM_RX_TIMEOUT
                            else:
                                logger.warning(
                                    f"Packet reception timeout: incomplete packet ({rx_length}/{wait_length} bytes)"
                                )
                                result = COMM_RX_CORRUPT
                            break
                        else:
                            continue

                    # calculate checksum
                    for i in range(2, wait_length - 1):  # except header, checksum
                        checksum += rxpacket[i]
                    checksum = ~checksum & 0xFF

                    # verify checksum
                    if rxpacket[wait_length - 1] == checksum:
                        logger.debug(
                            f"Received valid packet from ID {rxpacket[PKT_ID]} ({wait_length} bytes)"
                        )
                        result = COMM_SUCCESS
                    else:
                        logger.error(
                            f"Checksum mismatch: expected {checksum}, got {rxpacket[wait_length - 1]}"
                        )
                        result = COMM_RX_CORRUPT
                    break

                else:
                    # remove unnecessary packets
                    logger.debug(f"Removed {idx} unnecessary bytes from packet buffer")
                    del rxpacket[0:idx]
                    rx_length -= idx

            else:
                # check timeout
                if self.portHandler.is_packet_timeout():
                    if rx_length == 0:
                        logger.warning("Packet reception timeout: no data received")
                        result = COMM_RX_TIMEOUT
                    else:
                        logger.warning(
                            f"Packet reception timeout: incomplete packet ({rx_length}/{wait_length} bytes)"
                        )
                        result = COMM_RX_CORRUPT
                    break

        self.portHandler.is_using = False
        return rxpacket, result

    def packet_tx_rx(self, txpacket: List[int]) -> Tuple[Optional[List[int]], int, int]:
        rxpacket: Optional[List[int]] = None
        error = 0

        # tx packet
        result = self.packet_tx(txpacket)
        if result != COMM_SUCCESS:
            return rxpacket, result, error

        # (ID == Broadcast ID) == no need to wait for status packet or not available
        if txpacket[PKT_ID] == BROADCAST_ID:
            self.portHandler.is_using = False
            return rxpacket, result, error

        # set packet timeout
        if txpacket[PKT_INSTRUCTION] == INST_READ:
            self.portHandler.set_packet_timeout(txpacket[PKT_PARAMETER0 + 1] + 6)
        else:
            self.portHandler.set_packet_timeout(
                6
            )  # HEADER0 HEADER1 ID LENGTH ERROR CHECKSUM

        # rx packet
        while True:
            rxpacket, result = self.packet_rx()
            if result != COMM_SUCCESS or txpacket[PKT_ID] == (
                rxpacket[PKT_ID] if rxpacket else None
            ):
                break

        if result == COMM_SUCCESS and rxpacket and txpacket[PKT_ID] == rxpacket[PKT_ID]:
            error = rxpacket[PKT_ERROR]

        return rxpacket, result, error

    def ping(self, sts_id: int) -> Tuple[int, int, int]:
        model_number = 0
        error = 0

        txpacket = [0] * 6

        if sts_id >= BROADCAST_ID:
            logger.warning(f"Invalid servo ID for ping: {sts_id}")
            return model_number, COMM_NOT_AVAILABLE, error

        logger.debug(f"Pinging servo ID {sts_id}")
        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_PING

        rxpacket, result, error = self.packet_tx_rx(txpacket)

        if result == COMM_SUCCESS:
            data_read, result, error = self.read_tx_rx(
                sts_id, 3, 2
            )  # Address 3 : Model Number
            if result == COMM_SUCCESS:
                model_number = self.sts_makeword(data_read[0], data_read[1])
                logger.info(f"Servo ID {sts_id} responded: model {model_number}")
            else:
                logger.debug(f"Servo ID {sts_id} ping failed to read model number")
        else:
            logger.debug(f"Servo ID {sts_id} did not respond to ping")

        return model_number, result, error

    def action(self, sts_id: int) -> int:
        txpacket = [0] * 6

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_ACTION

        _, result, _ = self.packet_tx_rx(txpacket)

        return result

    def read_tx(self, sts_id: int, address: int, length: int) -> int:

        txpacket = [0] * 8

        if sts_id >= BROADCAST_ID:
            return COMM_NOT_AVAILABLE

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        result = self.packet_tx(txpacket)

        # set packet timeout
        if result == COMM_SUCCESS:
            self.portHandler.set_packet_timeout(length + 6)

        return result

    def read_rx(self, sts_id: int, length: int) -> Tuple[list, int, int]:
        result = COMM_TX_FAIL
        error = 0

        rxpacket = None
        data = []

        while True:
            rxpacket, result = self.packet_rx()

            if result != COMM_SUCCESS or rxpacket[PKT_ID] == sts_id:
                break

        if result == COMM_SUCCESS and rxpacket[PKT_ID] == sts_id:
            error = rxpacket[PKT_ERROR]

            data.extend(rxpacket[PKT_PARAMETER0 : PKT_PARAMETER0 + length])

        return data, result, error

    def read_tx_rx(
        self, sts_id: int, address: int, length: int
    ) -> Tuple[list, int, int]:
        txpacket = [0] * 8
        data: list = []

        if sts_id >= BROADCAST_ID:
            return data, COMM_NOT_AVAILABLE, 0

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        rxpacket, result, error = self.packet_tx_rx(txpacket)
        if result == COMM_SUCCESS:
            error = rxpacket[PKT_ERROR]

            data.extend(rxpacket[PKT_PARAMETER0 : PKT_PARAMETER0 + length])

        return data, result, error

    def read_tx_1byte(self, sts_id: int, address: int) -> int:
        return self.read_tx(sts_id, address, 1)

    def read_rx_1byte(self, sts_id: int) -> Tuple[int, int, int]:
        data, result, error = self.read_rx(sts_id, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read_tx_rx_1byte(self, sts_id: int, address: int) -> Tuple[int, int, int]:
        data, result, error = self.read_tx_rx(sts_id, address, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read_tx_2bytes(self, sts_id: int, address: int) -> int:
        return self.read_tx(sts_id, address, 2)

    def read_rx_2bytes(self, sts_id: int) -> Tuple[int, int, int]:
        data, result, error = self.read_rx(sts_id, 2)
        data_read = (
            self.sts_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        )
        return data_read, result, error

    def read_tx_rx_2bytes(self, sts_id: int, address: int) -> Tuple[int, int, int]:
        data, result, error = self.read_tx_rx(sts_id, address, 2)
        data_read = (
            self.sts_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        )
        return data_read, result, error

    def read_tx_4bytes(self, sts_id: int, address: int) -> int:
        return self.read_tx(sts_id, address, 4)

    def read_rx_4bytes(self, sts_id: int) -> Tuple[int, int, int]:
        data, result, error = self.read_rx(sts_id, 4)
        data_read = (
            sts_makedword(
                self.sts_makeword(data[0], data[1]), self.sts_makeword(data[2], data[3])
            )
            if (result == COMM_SUCCESS)
            else 0
        )
        return data_read, result, error

    def read_tx_rx_4bytes(self, sts_id: int, address: int) -> Tuple[int, int, int]:
        data, result, error = self.read_tx_rx(sts_id, address, 4)
        data_read = (
            sts_makedword(
                self.sts_makeword(data[0], data[1]), self.sts_makeword(data[2], data[3])
            )
            if (result == COMM_SUCCESS)
            else 0
        )
        return data_read, result, error

    def write_tx_only(self, sts_id: int, address: int, length: int, data: list) -> int:
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1 : PKT_PARAMETER0 + 1 + length] = data[0:length]

        result = self.packet_tx(txpacket)
        self.portHandler.is_using = False

        return result

    def write_tx_rx(
        self, sts_id: int, address: int, length: int, data: list
    ) -> Tuple[int, int]:
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1 : PKT_PARAMETER0 + 1 + length] = data[0:length]
        rxpacket, result, error = self.packet_tx_rx(txpacket)

        return result, error

    def write_tx_1byte(self, sts_id: int, address: int, data: int) -> int:
        data_write = [data]
        return self.write_tx_only(sts_id, address, 1, data_write)

    def write_tx_rx_1byte(
        self, sts_id: int, address: int, data: int
    ) -> Tuple[int, int]:
        data_write = [data]
        return self.write_tx_rx(sts_id, address, 1, data_write)

    def write_tx_2bytes(self, sts_id: int, address: int, data: int) -> int:
        data_write = [self.sts_lobyte(data), self.sts_hibyte(data)]
        return self.write_tx_only(sts_id, address, 2, data_write)

    def write_tx_rx_2bytes(
        self, sts_id: int, address: int, data: int
    ) -> Tuple[int, int]:
        data_write = [self.sts_lobyte(data), self.sts_hibyte(data)]
        return self.write_tx_rx(sts_id, address, 2, data_write)

    def write_tx_4bytes(self, sts_id: int, address: int, data: int) -> int:
        data_write = [
            self.sts_lobyte(sts_loword(data)),
            self.sts_hibyte(sts_loword(data)),
            self.sts_lobyte(sts_hiword(data)),
            self.sts_hibyte(sts_hiword(data)),
        ]
        return self.write_tx_only(sts_id, address, 4, data_write)

    def write_tx_rx_4bytes(
        self, sts_id: int, address: int, data: int
    ) -> Tuple[int, int]:
        data_write = [
            self.sts_lobyte(sts_loword(data)),
            self.sts_hibyte(sts_loword(data)),
            self.sts_lobyte(sts_hiword(data)),
            self.sts_hibyte(sts_hiword(data)),
        ]
        return self.write_tx_rx(sts_id, address, 4, data_write)

    def reg_write_tx_only(
        self, sts_id: int, address: int, length: int, data: list
    ) -> int:
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_REG_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1 : PKT_PARAMETER0 + 1 + length] = data[0:length]

        result = self.packet_tx(txpacket)
        self.portHandler.is_using = False

        return result

    def reg_write_tx_rx(
        self, sts_id: int, address: int, length: int, data: list
    ) -> Tuple[int, int]:
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = sts_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_REG_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1 : PKT_PARAMETER0 + 1 + length] = data[0:length]

        _, result, error = self.packet_tx_rx(txpacket)

        return result, error

    def sync_read_tx(
        self, start_address: int, data_length: int, param: list, param_length: int
    ) -> int:
        txpacket = [0] * (param_length + 8)
        # 8: HEADER0 HEADER1 ID LEN INST START_ADDR DATA_LEN CHKSUM

        txpacket[PKT_ID] = BROADCAST_ID
        txpacket[PKT_LENGTH] = param_length + 4  # 7: INST START_ADDR DATA_LEN CHKSUM
        txpacket[PKT_INSTRUCTION] = INST_SYNC_READ
        txpacket[PKT_PARAMETER0 + 0] = start_address
        txpacket[PKT_PARAMETER0 + 1] = data_length

        txpacket[PKT_PARAMETER0 + 2 : PKT_PARAMETER0 + 2 + param_length] = param[
            0:param_length
        ]

        # print(txpacket)
        result = self.packet_tx(txpacket)
        return result

    def sync_read_rx(self, data_length: int, param_length: int) -> Tuple[int, list]:
        wait_length = (6 + data_length) * param_length
        self.portHandler.set_packet_timeout(wait_length)
        rxpacket = []
        rx_length = 0
        while True:
            rxpacket.extend(self.portHandler.port_read(wait_length - rx_length))
            rx_length = len(rxpacket)
            if rx_length >= wait_length:
                result = COMM_SUCCESS
                break
            else:
                # check timeout
                if self.portHandler.is_packet_timeout():
                    if rx_length == 0:
                        result = COMM_RX_TIMEOUT
                    else:
                        result = COMM_RX_CORRUPT
                    break
        self.portHandler.is_using = False
        return result, rxpacket

    def sync_write_tx_only(
        self, start_address: int, data_length: int, param: list, param_length: int
    ) -> int:
        txpacket = [0] * (param_length + 8)
        # 8: HEADER0 HEADER1 ID LEN INST START_ADDR DATA_LEN ... CHKSUM

        txpacket[PKT_ID] = BROADCAST_ID
        txpacket[PKT_LENGTH] = (
            param_length + 4
        )  # 4: INST START_ADDR DATA_LEN ... CHKSUM
        txpacket[PKT_INSTRUCTION] = INST_SYNC_WRITE
        txpacket[PKT_PARAMETER0 + 0] = start_address
        txpacket[PKT_PARAMETER0 + 1] = data_length

        txpacket[PKT_PARAMETER0 + 2 : PKT_PARAMETER0 + 2 + param_length] = param[
            0:param_length
        ]

        _, result, _ = self.packet_tx_rx(txpacket)

        return result

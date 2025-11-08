import logging
from typing import Dict, List, Tuple, Optional
from .values import *

logger = logging.getLogger(__name__)


class GroupSyncRead:
    def __init__(self, ph, start_address: int, data_length: int):
        self.ph = ph
        self.start_address: int = start_address
        self.data_length: int = data_length

        self.last_result: bool = False
        self.is_param_changed: bool = False
        self.param: List[int] = []
        self.data_dict: Dict[int, List[int]] = {}

        self.clear_param()

    def make_param(self) -> None:
        if not self.data_dict:  # len(self.data_dict.keys()) == 0:
            return

        self.param = []

        for sts_id in self.data_dict:
            self.param.append(sts_id)

    def add_param(self, sts_id: int) -> bool:
        if sts_id in self.data_dict:  # sts_id already exist
            logger.warning(f"Servo ID {sts_id} already exists in sync read group")
            return False

        self.data_dict[sts_id] = []  # [0] * self.data_length
        logger.debug(f"Added servo ID {sts_id} to sync read group")

        self.is_param_changed = True
        return True

    def remove_param(self, sts_id: int) -> None:
        if sts_id not in self.data_dict:  # NOT exist
            logger.debug(f"Servo ID {sts_id} not in sync read group, cannot remove")
            return

        del self.data_dict[sts_id]
        logger.debug(f"Removed servo ID {sts_id} from sync read group")

        self.is_param_changed = True

    def clear_param(self) -> None:
        logger.debug("Clearing all parameters from sync read group")
        self.data_dict.clear()

    def packet_tx(self) -> int:
        if len(self.data_dict.keys()) == 0:
            logger.warning("No servos in sync read group, cannot transmit")
            return COMM_NOT_AVAILABLE

        if self.is_param_changed is True or not self.param:
            self.make_param()

        logger.debug(f"Transmitting sync read packet to {len(self.data_dict)} servo(s)")
        result = self.ph.sync_read_tx(
            self.start_address, self.data_length, self.param, len(self.data_dict.keys())
        )

        if result == COMM_SUCCESS:
            logger.debug("Sync read packet transmitted successfully")
        else:
            logger.warning(f"Sync read packet transmission failed: result={result}")

        return result

    def packet_rx(self) -> int:
        self.last_result = True
        result = COMM_RX_FAIL

        if len(self.data_dict.keys()) == 0:
            logger.warning("No servos in sync read group, cannot receive")
            return COMM_NOT_AVAILABLE

        logger.debug(
            f"Receiving sync read responses from {len(self.data_dict)} servo(s)"
        )
        result, rxpacket = self.ph.sync_read_rx(
            self.data_length, len(self.data_dict.keys())
        )
        # print(rxpacket)
        if len(rxpacket) >= (self.data_length + 6):
            for sts_id in self.data_dict:
                self.data_dict[sts_id], result = self.read_rx(
                    rxpacket, sts_id, self.data_length
                )
                if result != COMM_SUCCESS:
                    logger.warning(f"Failed to read data for servo ID {sts_id}")
                    self.last_result = False
                # print(sts_id)
        else:
            logger.warning(f"Received packet too short: {len(rxpacket)} bytes")
            self.last_result = False
        # print(self.last_result)

        if self.last_result:
            logger.debug("All sync read responses received successfully")
        else:
            logger.warning("Some sync read responses failed")

        return result

    def packet_tx_rx(self) -> int:
        result = self.packet_tx()
        if result != COMM_SUCCESS:
            return result

        return self.packet_rx()

    def read_rx(
        self, rxpacket: List[int], sts_id: int, data_length: int
    ) -> Tuple[Optional[List[int]], int]:
        # print(sts_id)
        # print(rxpacket)
        data: List[int] = []
        rx_length = len(rxpacket)
        # print(rx_length)
        rx_index = 0
        while (rx_index + 6 + data_length) <= rx_length:
            headpacket = [0x00, 0x00, 0x00]
            while rx_index < rx_length:
                headpacket[2] = headpacket[1]
                headpacket[1] = headpacket[0]
                headpacket[0] = rxpacket[rx_index]
                rx_index += 1
                if (
                    (headpacket[2] == 0xFF)
                    and (headpacket[1] == 0xFF)
                    and headpacket[0] == sts_id
                ):
                    # print(rx_index)
                    break
            # print(rx_index+3+data_length)
            if (rx_index + 3 + data_length) > rx_length:
                break
            if rxpacket[rx_index] != (data_length + 2):
                rx_index += 1
                # print(rx_index)
                continue
            rx_index += 1
            Error = rxpacket[rx_index]
            rx_index += 1
            calSum = sts_id + (data_length + 2) + Error
            data = [Error]
            data.extend(rxpacket[rx_index : rx_index + data_length])
            for i in range(0, data_length):
                calSum += rxpacket[rx_index]
                rx_index += 1
            calSum = ~calSum & 0xFF
            # print(calSum)
            if calSum != rxpacket[rx_index]:
                return None, COMM_RX_CORRUPT
            return data, COMM_SUCCESS
        # print(rx_index)
        return None, COMM_RX_CORRUPT

    def is_available(
        self, sts_id: int, address: int, data_length: int
    ) -> Tuple[bool, int]:
        # if self.last_result is False or sts_id not in self.data_dict:
        if sts_id not in self.data_dict:
            return False, 0

        if (address < self.start_address) or (
            self.start_address + self.data_length - data_length < address
        ):
            return False, 0
        if not self.data_dict[sts_id]:
            return False, 0
        if len(self.data_dict[sts_id]) < (data_length + 1):
            return False, 0
        return True, self.data_dict[sts_id][0]

    def get_data(self, sts_id: int, address: int, data_length: int) -> int:
        if data_length == 1:
            return self.data_dict[sts_id][address - self.start_address + 1]
        elif data_length == 2:
            return self.ph.sts_makeword(
                self.data_dict[sts_id][address - self.start_address + 1],
                self.data_dict[sts_id][address - self.start_address + 2],
            )
        elif data_length == 4:
            return self.ph.sts_makedword(
                self.ph.sts_makeword(
                    self.data_dict[sts_id][address - self.start_address + 1],
                    self.data_dict[sts_id][address - self.start_address + 2],
                ),
                self.ph.sts_makeword(
                    self.data_dict[sts_id][address - self.start_address + 3],
                    self.data_dict[sts_id][address - self.start_address + 4],
                ),
            )
        else:
            return 0

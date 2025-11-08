import logging
from typing import Dict, List
from .values import *

logger = logging.getLogger(__name__)


class GroupSyncWrite:
    def __init__(self, ph, start_address: int, data_length: int):
        self.ph = ph
        self.start_address: int = start_address
        self.data_length: int = data_length

        self.is_param_changed: bool = False
        self.param: List[int] = []
        self.data_dict: Dict[int, List[int]] = {}

        self.param_clear()

    def make_param(self) -> None:
        if not self.data_dict:
            return

        self.param = []

        for sts_id in self.data_dict:
            if not self.data_dict[sts_id]:
                return

            self.param.append(sts_id)
            self.param.extend(self.data_dict[sts_id])

    def param_add(self, sts_id: int, data: List[int]) -> bool:
        if sts_id in self.data_dict:  # sts_id already exist
            logger.warning(f"Servo ID {sts_id} already exists in sync write group")
            return False

        if len(data) > self.data_length:  # input data is longer than set
            logger.error(
                f"Data length {len(data)} exceeds configured length {self.data_length}"
            )
            return False

        self.data_dict[sts_id] = data
        logger.debug(f"Added servo ID {sts_id} to sync write group")

        self.is_param_changed = True
        return True

    def param_remove(self, sts_id: int) -> None:
        if sts_id not in self.data_dict:  # NOT exist
            logger.debug(f"Servo ID {sts_id} not in sync write group, cannot remove")
            return

        del self.data_dict[sts_id]
        logger.debug(f"Removed servo ID {sts_id} from sync write group")

        self.is_param_changed = True

    def param_change(self, sts_id: int, data: List[int]) -> bool:
        if sts_id not in self.data_dict:  # NOT exist
            logger.warning(f"Servo ID {sts_id} not in sync write group, cannot change")
            return False

        if len(data) > self.data_length:  # input data is longer than set
            logger.error(
                f"Data length {len(data)} exceeds configured length {self.data_length}"
            )
            return False

        self.data_dict[sts_id] = data
        logger.debug(f"Changed data for servo ID {sts_id} in sync write group")

        self.is_param_changed = True
        return True

    def param_clear(self) -> None:
        logger.debug("Clearing all parameters from sync write group")
        self.data_dict.clear()

    def packet_tx(self) -> int:
        if len(self.data_dict.keys()) == 0:
            logger.warning("No servos in sync write group, cannot transmit")
            return COMM_NOT_AVAILABLE

        if self.is_param_changed is True or not self.param:
            self.make_param()

        logger.debug(
            f"Transmitting sync write packet to {len(self.data_dict)} servo(s)"
        )
        result = self.ph.sync_write_tx_only(
            self.start_address,
            self.data_length,
            self.param,
            len(self.data_dict.keys()) * (1 + self.data_length),
        )

        if result == COMM_SUCCESS:
            logger.debug("Sync write packet transmitted successfully")
        else:
            logger.warning(f"Sync write packet transmission failed: result={result}")

        return result

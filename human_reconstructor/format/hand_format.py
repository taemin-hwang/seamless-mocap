import numpy as np
from enum import Enum

class HAND_STATUS(Enum):
    OPEN = 0
    CLOSED = 1
    INDEX = 2

def get_status_from_idx(idx):
    status = HAND_STATUS.OPEN
    if idx == HAND_STATUS.OPEN.value:
        status = HAND_STATUS.OPEN
    elif idx == HAND_STATUS.CLOSED.value:
        status = HAND_STATUS.CLOSED
    elif idx == HAND_STATUS.INDEX.value:
        status = HAND_STATUS.INDEX
    return status
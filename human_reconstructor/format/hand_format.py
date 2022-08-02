import numpy as np
from enum import Enum

class HAND_STATUS(Enum):
    RIGHT_OPEN = 0
    RIGHT_CLOSED = 1
    RIGHT_INDEX = 2
    LEFT_OPEN = 3
    LEFT_CLOSED = 4
    LEFT_INDEX = 5

def get_status_from_idx(idx):
    status = HAND_STATUS.RIGHT_CLOSED
    if idx == HAND_STATUS.RIGHT_OPEN.value:
        status = HAND_STATUS.RIGHT_OPEN
    elif idx == HAND_STATUS.RIGHT_CLOSED.value:
        status = HAND_STATUS.RIGHT_CLOSED
    elif idx == HAND_STATUS.RIGHT_INDEX.value:
        status = HAND_STATUS.RIGHT_INDEX
    elif idx == HAND_STATUS.LEFT_OPEN.value:
        status = HAND_STATUS.LEFT_OPEN
    elif idx == HAND_STATUS.LEFT_CLOSED.value:
        status = HAND_STATUS.LEFT_CLOSED
    elif idx == HAND_STATUS.LEFT_INDEX.value:
        status = HAND_STATUS.LEFT_INDEX
    return status
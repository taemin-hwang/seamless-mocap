import numpy as np
from enum import Enum

class FACE_STATUS(Enum):
    CLOSED = 0
    A = 1
    E = 2
    I = 3
    O = 4
    U = 5

def get_status_from_idx(idx):
    status = FACE_STATUS.CLOSED
    if idx == FACE_STATUS.CLOSED.value:
        status = FACE_STATUS.CLOSED
    elif idx == FACE_STATUS.A.value:
        status = FACE_STATUS.A
    elif idx == FACE_STATUS.E.value:
        status = FACE_STATUS.E
    elif idx == FACE_STATUS.I.value:
        status = FACE_STATUS.I
    elif idx == FACE_STATUS.O.value:
        status = FACE_STATUS.O
    elif idx == FACE_STATUS.U.value:
        status = FACE_STATUS.U
    return status
#ifndef _TRANSFER_INTERFACE_H_
#define _TRANSFER_INTERFACE_H_

#include <vector>

#include "system/logger/logger.h"
#include "system/types.h"

class TransferInterface {
 public:
    TransferInterface() = default;
    virtual ~TransferInterface() = default;

    virtual void SendPeopleKeypoints(const seamless::PeopleKeypoints& people_keypoints) = 0;
};

#endif
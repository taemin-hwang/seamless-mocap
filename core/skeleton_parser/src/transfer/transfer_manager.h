#ifndef _TRANSFER_MANAGER_H_
#define _TRANSFER_MANAGER_H_

#include <iostream>

#include "transfer/transfer_interface.h"
#include "system/logger/logger.h"

class TransferManager : public TransferInterface {
 public:
    TransferManager() = default;
    virtual ~TransferManager() = default;

    void SendPeopleKeypoints(const PeopleKeypoints& people_keypoints);
};

#endif
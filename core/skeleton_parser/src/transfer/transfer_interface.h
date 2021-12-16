#ifndef _TRANSFER_INTERFACE_H_
#define _TRANSFER_INTERFACE_H_

#include <vector>

#include "system/logger/logger.h"

using XYCoordinate = std::pair<float, float>;
using PersonKeypoints = std::vector<XYCoordinate>;
using PeopleKeypoints = std::vector<PersonKeypoints>;

class TransferInterface {
 public:
    TransferInterface() = default;
    virtual ~TransferInterface() = default;

    virtual void SendPeopleKeypoints(const PeopleKeypoints& people_keypoints) = 0;
};

#endif
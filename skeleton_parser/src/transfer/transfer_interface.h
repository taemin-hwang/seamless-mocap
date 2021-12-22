#ifndef _TRANSFER_INTERFACE_H_
#define _TRANSFER_INTERFACE_H_

#include <vector>
#include <string>

#include "system/logger/logger.h"
#include "system/types.h"

class TransferInterface {
 public:
    TransferInterface() = default;
    virtual ~TransferInterface() = default;

    virtual void Initialize(const std::string&, const int&) = 0;
    virtual void SendPeopleKeypoints(const seamless::PeopleKeypoints& people_keypoints) = 0;

    void SetIpAddress(const std::string& ip_addr) { ip_addr_ = ip_addr; }
    void SetPort(const int& port) { port_ = port; }

 protected:
    std::string ip_addr_ = "";
    int port_ = 0;
};

#endif
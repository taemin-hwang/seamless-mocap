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
    virtual void SendPeopleKeypoints(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& people_keypoints) = 0;

    void SetIpAddress(const std::string& ip_addr) { ip_addr_ = ip_addr; }
    void SetPort(const int& port) { port_ = port; }

 protected:
    inline virtual void PrintElement(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& people_keypoints) {
        for (auto& b : bbox) {
            std::pair<int, int> left_top = b.GetLeftTop();
            std::pair<int, int> right_bottom = b.GetRightBottom();
            std::cout << left_top.first << ", " << left_top.second << std::endl;
            std::cout << right_bottom.first << ", " << right_bottom.second << std::endl;
            std::cout << b.GetConfidence() << std::endl;
        }
        for (auto& person_keypoint : people_keypoints) {
            auto kp = person_keypoint.GetKeypoint();
            auto c = person_keypoint.GetConfidence();
            for(int i = 0; i < kp.size(); i++) {
                std::cout << "[" << kp[i].first << ", " << kp[i].second << ", " << c[i] << std::endl;
            }
        }
    }

 protected:
    std::string ip_addr_ = "";
    int port_ = 0;
};

#endif
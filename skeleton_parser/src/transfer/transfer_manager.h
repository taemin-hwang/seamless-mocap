#ifndef _TRANSFER_MANAGER_H_
#define _TRANSFER_MANAGER_H_

#include <iostream>
#include <vector>
#include <string>
#include <cstring>

// rapidjson
#include <rapidjson/rapidjson.h>
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

#include "transfer/transfer_interface.h"
#include "system/logger/logger.h"

#include <arpa/inet.h>
#include <sys/socket.h>

class TransferManager : public TransferInterface {
 public:
    TransferManager() = default;
    virtual ~TransferManager() = default;

    void Initialize(const int&, const std::string&, const int&);
    void SendPeopleKeypoints(const seamless::PeopleSkeleton& people_skeleton);
    void Shutdown();

 private:
    std::string GetStringFromPeopleKeypoint(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& keypoint, const seamless::TimestampMilliseconds timestamp, const seamless::FrameSize framesize, int id);
    void SetObjectFromPersonKeypoint(rapidjson::Value& annots_object, rapidjson::Document::AllocatorType& allocator, const seamless::PersonBoundBox& bbox, const seamless::PersonKeypointsWithConfidence& keypoint);

 private:
    int sock_;
    struct sockaddr_in serv_addr_;
};

#endif

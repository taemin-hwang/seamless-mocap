#ifndef _TRANSFER_MANAGER_H_
#define _TRANSFER_MANAGER_H_

#include <iostream>
#include <vector>
#include <string>
#include <cstring>

// curl for HTTP
#include <curl/curl.h>

// rapidjson
#include <rapidjson/rapidjson.h>
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

#include "transfer/transfer_interface.h"
#include "system/logger/logger.h"

class TransferManager : public TransferInterface {
 public:
    TransferManager() = default;
    virtual ~TransferManager() = default;

    void Initialize(const int&, const std::string&, const int&);
    void SendPeopleKeypoints(const seamless::PeopleSkeleton& people_skeleton);

 private:
    std::string GetStringFromPeopleKeypoint(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& keypoint, const seamless::TimestampMilliseconds timestamp, const seamless::FrameSize framesize, int id);
    void SetObjectFromPersonKeypoint(rapidjson::Value& annots_object, rapidjson::Document::AllocatorType& allocator, const seamless::PersonBoundBox& bbox, const seamless::PersonKeypointsWithConfidence& keypoint);
    size_t CallBackFunc(char* ptr, size_t size, size_t nmemb, string* stream);
    size_t WriteFunction(void* ptr, size_t size, size_t nmemb, void* stream);

 private:
    std::string target_url_;
};

#endif

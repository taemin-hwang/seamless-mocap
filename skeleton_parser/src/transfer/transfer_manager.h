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

    void Initialize(const std::string&, const int&);
    void SendPeopleKeypoints(const seamless::PeopleKeypoints& people_keypoints);

 private:
    std::string GetStringFromKeypoint(int id, int type, std::vector<std::pair<int, int>> keypoint);
    size_t CallBackFunc(char* ptr, size_t size, size_t nmemb, string* stream);
    size_t WriteFunction(void* ptr, size_t size, size_t nmemb, void* stream);

 private:
    std::string target_url_;
};

#endif
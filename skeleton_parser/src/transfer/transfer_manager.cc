#include "transfer/transfer_manager.h"

void TransferManager::Initialize(const std::string& ip_addr, const int& port) {
    ip_addr_ = ip_addr;
    port_ = port;

    logInfo << "Try to access to " << ip_addr_ << " (" << port_ << ")";
    target_url_ = "http://" + ip_addr_ + ":" + std::to_string(port_);
    logInfo << target_url_;
}

void TransferManager::SendPeopleKeypoints(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& people_keypoints) {
    if (people_keypoints.size() < 1) {
        logWarn << "People keypoint size is less than 1, No one here";
        return;
    }

    for (auto& b : bbox) {
        std::pair<int, int> left_top = b.GetLeftTop();
        std::pair<int, int> right_bottom = b.GetRightBottom();

        std::cout << left_top.first << ", " << left_top.second << std::endl;
        std::cout << right_bottom.first << ", " << right_bottom.second << std::endl;
        std::cout << b.GetConfidence() << std::endl;

        std::cout << std::endl;
    }

    for (auto& p : people_keypoints) {

    }

    CURL* curl;
    CURLcode res;
    std::string chunk;
    std::string resource_json;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();


    for (auto& person_keypoints : people_keypoints) {
        resource_json = GetStringFromKeypoint(person_keypoints);

        if (curl) {
            curl_easy_setopt(curl, CURLOPT_URL, target_url_.c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, resource_json.c_str());
            res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                logError << "curl_easy_perform() failed : " << curl_easy_strerror(res);
            }
        }
    }

    curl_easy_cleanup(curl);
}

std::string TransferManager::GetStringFromKeypoint(const seamless::PersonKeypointsWithConfidence& keypoint) {
    rapidjson::Document d;
    d.SetObject();

    rapidjson::Document::AllocatorType& allocator = d.GetAllocator();

    size_t sz = allocator.Size();

    d.AddMember("id", keypoint.GetId(), allocator);
    // Value val(kObjectType);
    // val.SetString(timestamp.c_str(), static_cast<SizeType>(timestamp.length()), allocator);
    // d.AddMember("timestamp", val, allocator);
    d.AddMember("bodytype", keypoint.size(), allocator);

    rapidjson::Value array_keypoints(rapidjson::kArrayType);

    auto joint = keypoint.GetKeypoint();
    auto confidence = keypoint.GetConfidence();

    for (int i = 0; i < keypoint.size(); i++) {
        rapidjson::Value element_keypoints(rapidjson::kArrayType);
        {
            element_keypoints.PushBack(static_cast<int>(joint[i].first), allocator); // X
            element_keypoints.PushBack(static_cast<int>(joint[i].second), allocator); // Y
            element_keypoints.PushBack(confidence[i], allocator); // Confidence
        }
        array_keypoints.PushBack(element_keypoints, allocator);
    }

    d.AddMember("keypoints2d", array_keypoints, allocator);

    rapidjson::StringBuffer strbuf;
    rapidjson::Writer<rapidjson::StringBuffer> writer(strbuf);
    d.Accept(writer);

    std::string ret = strbuf.GetString();
    logDebug << ret;

    return ret;
}


size_t TransferManager::CallBackFunc(char* ptr, size_t size, size_t nmemb, string* stream)
{
    int realsize = size * nmemb;
    stream->append(ptr, realsize);
    return realsize;
}

size_t TransferManager::WriteFunction(void *ptr, size_t size, size_t nmemb, void *stream)
{
    fwrite(ptr, size, nmemb, (FILE *)stream);
    return (nmemb*size);
}


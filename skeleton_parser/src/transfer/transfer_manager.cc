#include "transfer/transfer_manager.h"

void TransferManager::SendPeopleKeypoints(const seamless::PeopleKeypoints& people_keypoints) {
    if (people_keypoints.size() < 1) {
        logWarn << "People keypoint size is less than 1";
        return;
    }

    CURL* curl;
    CURLcode res;
    std::string chunk;
    std::string resource_json;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    std::string target_url = "http://127.0.0.1:50001";

    std::vector<std::pair<int, int>> person_keypoint_int_array;
    person_keypoint_int_array.resize(people_keypoints[0].second.size());

    for (auto& person_keypoints : people_keypoints) {
        int person_tracking_id = person_keypoints.first;
        auto person_keypoint_list = person_keypoints.second;

        for (int i = 0; i < person_keypoint_list.size(); i++) {
            person_keypoint_int_array[i] = {static_cast<int>(person_keypoint_list[i].x), static_cast<int>(person_keypoint_list[i].y)};
        }

        resource_json = GetStringFromKeypoint(person_tracking_id, person_keypoint_list.size(), person_keypoint_int_array);

        if (curl) {
            curl_easy_setopt(curl, CURLOPT_URL, target_url.c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, resource_json.c_str());
            res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                logError << "curl_easy_perform() failed : " << curl_easy_strerror(res);
            }
        }
    }

    curl_easy_cleanup(curl);
}

std::string TransferManager::GetStringFromKeypoint(int id, /*std::string timestamp,*/ int bodytype, std::vector<std::pair<int, int>> keypoint) {
    rapidjson::Document d;
    d.SetObject();

    rapidjson::Document::AllocatorType& allocator = d.GetAllocator();

    size_t sz = allocator.Size();

    d.AddMember("id", id, allocator);
    // Value val(kObjectType);
    // val.SetString(timestamp.c_str(), static_cast<SizeType>(timestamp.length()), allocator);
    // d.AddMember("timestamp", val, allocator);
    d.AddMember("bodytype", bodytype, allocator);

    rapidjson::Value array_keypoints(rapidjson::kArrayType);
    for(const auto& kp : keypoint) {
        rapidjson::Value element_keypoints(rapidjson::kArrayType);
        {
            element_keypoints.PushBack(kp.first, allocator);
            element_keypoints.PushBack(kp.second, allocator);
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


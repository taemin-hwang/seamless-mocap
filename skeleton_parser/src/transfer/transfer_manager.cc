#include "transfer/transfer_manager.h"

void TransferManager::Initialize(const std::string& ip_addr, const int& port) {
    ip_addr_ = ip_addr;
    port_ = port;

    logInfo << "Try to access to " << ip_addr_ << " (" << port_ << ")";
    target_url_ = "http://" + ip_addr_ + ":" + std::to_string(port_);
    logInfo << target_url_;
}

void TransferManager::SendPeopleKeypoints(const seamless::PeopleSkeleton& people_skeleton) {
    auto bbox = people_skeleton.GetPeopleBoundBox();
    auto people_keypoints = people_skeleton.GetPeopleKeypointsWithConfidence();
    auto timestamp = people_skeleton.GetTimestampMilliseconds();
    auto frame_size = people_skeleton.GetFrameSize();
    auto camera_id = people_skeleton.GetCameraId();

    if (people_keypoints.size() < 1) {
        logWarn << "People keypoint size is less than 1, No one here";
        return;
    }

    CURL* curl;
    CURLcode res;
    std::string chunk;
    std::string resource_json = "EMPTY";

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    resource_json = GetStringFromPeopleKeypoint(bbox, people_keypoints, timestamp, frame_size, camera_id);
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, target_url_.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, resource_json.c_str());
        res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            logError << "curl_easy_perform() failed : " << curl_easy_strerror(res);
        }
    }
    curl_easy_cleanup(curl);
}

std::string TransferManager::GetStringFromPeopleKeypoint(const seamless::PeopleBoundBox& bbox, const seamless::PeopleKeypointsWithConfidence& keypoint, const seamless::TimestampMilliseconds timestamp, const seamless::FrameSize framesize, int camera_id) {
    rapidjson::Document document;
    document.SetObject();
    rapidjson::Document::AllocatorType& allocator = document.GetAllocator();

    document.AddMember("id", camera_id, allocator);
    document.AddMember("timestamp", timestamp, allocator);
    document.AddMember("height", framesize.second, allocator);
    document.AddMember("width", framesize.first, allocator);

    rapidjson::Value annots_array(rapidjson::kArrayType);

    for(int i = 0; i < keypoint.size(); i++) {
        auto person_keypoint = keypoint[i];
        auto person_bbox = bbox[i];
        rapidjson::Value annots_element(rapidjson::kObjectType);
        SetObjectFromPersonKeypoint(annots_element, allocator, person_bbox, person_keypoint);
        annots_array.PushBack(annots_element, allocator);
    }
    document.AddMember("annots", annots_array, allocator);

    rapidjson::StringBuffer strbuf;
    rapidjson::Writer<rapidjson::StringBuffer> writer(strbuf);
    document.Accept(writer);

    std::string ret = strbuf.GetString();
    logDebug << ret;

    return ret;
}

void TransferManager::SetObjectFromPersonKeypoint(rapidjson::Value& annots_element, rapidjson::Document::AllocatorType& allocator, const seamless::PersonBoundBox& bbox, const seamless::PersonKeypointsWithConfidence& keypoint) {
    // Add member of bounding box
    logDebug << "Add member of bouding box";
    rapidjson::Value array_bbox(rapidjson::kArrayType);
    std::pair<int, int> left_top = bbox.GetLeftTop();
    std::pair<int, int> right_bottom = bbox.GetRightBottom();
    float bbox_confidence = bbox.GetConfidence();
    array_bbox.PushBack(left_top.first, allocator); // Left-Top X
    array_bbox.PushBack(left_top.second, allocator); // Left-Top Y
    array_bbox.PushBack(right_bottom.first, allocator); // Right-Bottom X
    array_bbox.PushBack(right_bottom.second, allocator); // Right-Bottom Y
    array_bbox.PushBack(bbox_confidence, allocator);
    annots_element.AddMember("bbox", array_bbox, allocator);

    // Add member of person id
    logDebug << "Add member of person id";
    annots_element.AddMember("personID", keypoint.GetId(), allocator);

    // Add member of keypoints array
    logDebug << "Add member of keypoint array";
    auto joint = keypoint.GetKeypoint();
    auto joint_confidence = keypoint.GetConfidence();

    rapidjson::Value array_keypoints(rapidjson::kArrayType);
    for (int i = 0; i < keypoint.size(); i++) {
        rapidjson::Value element_keypoints(rapidjson::kArrayType);
        {
            element_keypoints.PushBack(static_cast<int>(joint[i].first), allocator); // X
            element_keypoints.PushBack(static_cast<int>(joint[i].second), allocator); // Y
            element_keypoints.PushBack(joint_confidence[i], allocator); // Confidence
        }
        array_keypoints.PushBack(element_keypoints, allocator);
    }
    annots_element.AddMember("keypoints", array_keypoints, allocator);
    logDebug << "Done";
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

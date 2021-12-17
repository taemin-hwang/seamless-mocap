#include "skeleton_parser.h"
#include "system/logger/logger.h"

// Create TrackerManager, TransferManager, and ConfigParser
SkeletonParser::SkeletonParser() {
    body_tracker_ = std::make_unique<TrackerManager>(BodyFormat::kPose34, DetectionModel::kFast);
    body_transfer_ = std::make_unique<TransferManager>();
    config_parser_ = std::make_unique<ConfigParser>("../etc/config.json");
    viewer_manager_ = std::make_unique<ViewerManager>();
}

// Initialize TrackerManager, TransferManger
void SkeletonParser::Initialize() {
    logDebug << __func__;
    logInfo << "[Server Addr  ] : " << config_parser_->GetAddress();
    logInfo << "[Port Number  ] : " << config_parser_->GetPort();
    logInfo << "[Viewer Status] : " << (config_parser_->IsViewerOn() ? "ON" : "OFF");
    if(config_parser_->IsViewerOn()) {
        enable_viewer_ = true;
    }

    body_tracker_->SetTransferHandler([=](seamless::PeopleKeypoints people_keypoints){ body_transfer_->SendPeopleKeypoints(people_keypoints); });
    if(enable_viewer_) {
        body_tracker_->SetViewerHandler([=](const cv::Mat& image, seamless::PeopleKeypoints people_keypoints){ viewer_manager_->DisplayPeopleKeypoints(image, people_keypoints); });
    }

    body_tracker_->Initialize();
    if(enable_viewer_) viewer_manager_->Initialize();
}

void SkeletonParser::Run() {
    logDebug << __func__;
    body_tracker_->Run();
    if(enable_viewer_) viewer_manager_->Run();
}

void SkeletonParser::Shutdown() {
    logDebug << __func__;
    body_tracker_->Shutdown();
    if(enable_viewer_) viewer_manager_->Shutdown();
}
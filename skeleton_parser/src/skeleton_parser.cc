#include "skeleton_parser.h"
#include "system/logger/logger.h"

// Create TrackerManager, TransferManager, and ConfigParser
SkeletonParser::SkeletonParser() {
    tracker_manager_ = std::make_unique<TrackerManager>(BodyFormat::kPose34, DetectionModel::kFast);
    transfer_manager_ = std::make_unique<TransferManager>();
    config_parser_ = std::make_unique<ConfigParser>("../etc/config.json");
    viewer_manager_ = std::make_unique<ViewerManager>();
}

// Initialize TrackerManager, TransferManger
void SkeletonParser::Initialize() {
    logDebug << __func__;
    logInfo << "[Server Addr  ] : " << config_parser_->GetAddress();
    logInfo << "[Port Number  ] : " << config_parser_->GetPort();
    logInfo << "[Viewer Status] : " << (config_parser_->IsViewerOn() ? "ON" : "OFF");

    // Set HTTP server IP address and port number
    transfer_manager_->Initialize(config_parser_->GetAddress(), config_parser_->GetPort());

    // Set flag if 2D viewer would be ON
    if(config_parser_->IsViewerOn()) {
        enable_viewer_ = true;
    }

    // Set event handler calling when body keypoints are retrieved
    tracker_manager_->SetTransferHandler([=](seamless::PeopleKeypoints people_keypoints){ transfer_manager_->SendPeopleKeypoints(people_keypoints); });
    if(enable_viewer_) {
        tracker_manager_->SetViewerHandler([=](const cv::Mat& image, const std::pair<float, float>& scale, seamless::PeopleKeypoints people_keypoints){
            viewer_manager_->DisplayPeopleKeypoints(image, scale, people_keypoints);
        });
    }

    // Initialize tracker manager and viewer manager
    tracker_manager_->Initialize();
    if(enable_viewer_) viewer_manager_->Initialize();
}

// Run estimating 2D body keypoint, and display it if viewer is enabled
void SkeletonParser::Run() {
    logDebug << __func__;
    tracker_manager_->Run();
    if(enable_viewer_) viewer_manager_->Run();
}

// Shutdown
void SkeletonParser::Shutdown() {
    logDebug << __func__;
    tracker_manager_->Shutdown();
    if(enable_viewer_) viewer_manager_->Shutdown();
}
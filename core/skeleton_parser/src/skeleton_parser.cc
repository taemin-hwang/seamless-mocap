#include "skeleton_parser.h"

SkeletonParser::SkeletonParser() {
    body_tracker_ = std::make_unique<TrackerManager>(BodyFormat::kPose34, DetectionModel::kFast);
    body_transfer_ = std::make_unique<TransferManager>();
    config_parser_ = std::make_unique<ConfigParser>("../etc/config.json");
}

void SkeletonParser::Initialize() {
    std::cout << __func__ << std::endl;
    body_tracker_->Initialize();
}

void SkeletonParser::Run() {
    std::cout << __func__ << std::endl;
    body_tracker_->Run();
}

void SkeletonParser::Shutdown() {
    std::cout << __func__ << std::endl;
    body_tracker_->Shutdown();
}
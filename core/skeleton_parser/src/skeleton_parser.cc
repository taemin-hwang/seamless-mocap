#include "skeleton_parser.h"
#include "system/logger/logger.h"

SkeletonParser::SkeletonParser() {
    body_tracker_ = std::make_unique<TrackerManager>(BodyFormat::kPose34, DetectionModel::kFast);
    body_transfer_ = std::make_unique<TransferManager>();
    config_parser_ = std::make_unique<ConfigParser>("../etc/config.json");
}

void SkeletonParser::Initialize() {
    logDebug << __func__;
    logInfo << "[Server Addr  ] : " << config_parser_->GetAddress();
    logInfo << "[Port Number  ] : " << config_parser_->GetPort();
    logInfo << "[Viewer Status] : " << (config_parser_->IsViewerOn() ? "ON" : "OFF");

    body_tracker_->Initialize();
}

void SkeletonParser::Run() {
    logDebug << __func__;
    body_tracker_->Run();
}

void SkeletonParser::Shutdown() {
    logDebug << __func__;
    body_tracker_->Shutdown();
}
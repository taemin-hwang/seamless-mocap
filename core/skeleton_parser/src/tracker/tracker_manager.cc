
#include <iostream>
#include "tracker/tracker_manager.h"

TrackerManager::TrackerManager(BodyFormat body_format, DetectionModel detection_model)
  : TrackerInterface(body_format, detection_model) {
    zed_tracker_ = std::make_unique<ZedTracker>();
}

TrackerManager::~TrackerManager() {

}

void TrackerManager::Initialize() {
    logDebug << __func__;
    zed_tracker_->Initialize();
}

void TrackerManager::Run(){
    logDebug << __func__;
    zed_tracker_->Run();
}

void TrackerManager::Shutdown() {
    logDebug << __func__;
    zed_tracker_->Shutdown();
}

void TrackerManager::GetHumanKeypoints() {
    logDebug << __func__;
}
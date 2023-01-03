
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
    if( viewer_handler != nullptr) { zed_tracker_->SetViewerHandler(viewer_handler); }
    if( transfer_handler != nullptr) { zed_tracker_->SetTransferHandler(transfer_handler); }
}

void TrackerManager::Run(){
    logDebug << __func__;
    zed_tracker_->Run();
}

void TrackerManager::Shutdown() {
    logDebug << __func__;
    zed_tracker_->Shutdown();
}
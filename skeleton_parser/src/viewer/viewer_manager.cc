#include "viewer/viewer_manager.h"

ViewerManager::ViewerManager() {
    gui_2d_viewer_ = std::make_unique<Gui2DViewer>();
}

void ViewerManager::Initialize(){
    logDebug << __func__;
}

void ViewerManager::Run(){
    logDebug << __func__;
}

void ViewerManager::Shutdown(){
    logDebug << __func__;
}

void ViewerManager::DisplayPeopleKeypoints(const cv::Mat& image, const std::pair<float, float>& scale, const seamless::PeopleKeypoints& people_keypoints) {
    gui_2d_viewer_->Display2DViewer(image, scale, people_keypoints);
}
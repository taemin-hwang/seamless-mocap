#include "viewer/viewer_manager.h"

ViewerManager::ViewerManager() {
    gui_2d_viewer_ = std::make_unique<Gui2DViewer>();
}

void ViewerManager::Initialize(){
    logDebug << __func__;
    // Resolution pc_resolution(min((int)camera_config.resolution.width, 720), min((int)camera_config.resolution.height, 404));
    // auto camera_parameters = zed.getCameraInformation(pc_resolution).camera_configuration.calibration_parameters.left_cam;
    // Mat point_cloud(pc_resolution, MAT_TYPE::F32_C4, MEM::GPU);
    // // Create OpenGL Viewer
    // GLViewer viewer;
    // viewer.init(argc, argv, camera_parameters, obj_det_params.enable_tracking, obj_det_params.body_format);

    // Pose cam_pose;
    // cam_pose.pose_data.setIdentity();

    // Plane floor_plane; // floor plane handle
    // Transform reset_from_floor_plane; // camera transform once floor plane is detected

    // // Main Loop
    // bool need_floor_plane = positional_tracking_parameters.set_as_static;
}

void ViewerManager::Run(){
    logDebug << __func__;
}

void ViewerManager::Shutdown(){
    logDebug << __func__;
}

void ViewerManager::DisplayPeopleKeypoints(const cv::Mat& image, const seamless::PeopleKeypoints& people_keypoints) {
    gui_2d_viewer_->Display2DViewer(image, people_keypoints);
}
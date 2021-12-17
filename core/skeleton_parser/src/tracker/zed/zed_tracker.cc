///////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2021, STEREOLABS.
//
// All rights reserved.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
///////////////////////////////////////////////////////////////////////////

/*****************************************************************************************
 ** This sample demonstrates how to detect human bodies and retrieves their 3D position **
 **         with the ZED SDK and display the result in an OpenGL window.                **
 *****************************************************************************************/

#include <iostream>

#include "tracker/zed/zed_tracker.h"

// Using std and sl namespaces
using namespace std;
using namespace sl;

#ifdef _SL_JETSON_
    const bool isJetson = true;
#else
    const bool isJetson = false;
#endif

ZedTracker::ZedTracker() {

}

void ZedTracker::Initialize() {
    logDebug << __func__;
    if (OpenCamera() == EXIT_FAILURE) {
        return;
    }
    if (EnablePositionalTracking() == EXIT_FAILURE) {
        return;
    }
    if( EnableBodyTracking() == EXIT_FAILURE) {
        return;
    }
}

void ZedTracker::Run() {
    logDebug << __func__;
    // Create ZED Objects filled in the main loop
    Objects bodies;
    // grab runtime parameters
    RuntimeParameters runtime_parameters;
    runtime_parameters.measure3D_reference_frame = sl::REFERENCE_FRAME::WORLD;

    auto image_configuration = GetImageConfiguration();
    auto image = std::get<0>(image_configuration);
    auto image_scale = std::get<1>(image_configuration);

    bool quit = false;
    char key = ' ';

    bool is_tracking_on = object_detection_parameters_.enable_tracking;
    sl::BODY_FORMAT body_format = object_detection_parameters_.body_format;

    seamless::PersonKeypoints person_keypoints;
    seamless::PeopleKeypoints people_keypoints;

    if(body_format == sl::BODY_FORMAT::POSE_18) {
        person_keypoints.resize(18);
    } else {
        person_keypoints.resize(34);
    }

    while(!quit && key != 'q') {
        if (zed_.grab() == ERROR_CODE::SUCCESS) {
            zed_.retrieveObjects(bodies, object_detection_runtime_parameters_);

            int person_id = 0;
            people_keypoints.resize(bodies.object_list.size());
            for (auto i = bodies.object_list.rbegin(); i != bodies.object_list.rend(); ++i) {
                sl::ObjectData& obj = (*i);
                if (renderObject(obj, is_tracking_on)) {
                    // skeleton joints
                    int joint_id = 0;
                    for (auto &kp : obj.keypoint_2d)
                    {
                        cv::Point2f cv_kp = cvt(kp, image_scale);
                        // logDebug << "[" << person_id << "] [" << joint_id << "] : " << cv_kp.x << ", " << cv_kp.y;
                        person_keypoints[joint_id] = {cv_kp.x, cv_kp.y};
                        joint_id++;
                    }
                }
                people_keypoints[person_id].first = obj.id;
                people_keypoints[person_id].second = person_keypoints;
                person_id++;
            }

            if (viewer_handler != nullptr) viewer_handler(image, people_keypoints);
            if (transfer_handler != nullptr) transfer_handler(people_keypoints);
        }
    }
    bodies.object_list.clear();
}

void ZedTracker::Shutdown() {
    logDebug << __func__;
    zed_.disableObjectDetection();
    zed_.disablePositionalTracking();
    zed_.close();
}

int ZedTracker::OpenCamera() {
    logDebug << __func__;
    InitParameters init_parameters;
    init_parameters.camera_resolution = RESOLUTION::HD1080;
    // On Jetson the object detection combined with an heavy depth mode could reduce the frame rate too much
    init_parameters.depth_mode = isJetson ? DEPTH_MODE::PERFORMANCE : DEPTH_MODE::ULTRA;
    init_parameters.coordinate_system = COORDINATE_SYSTEM::RIGHT_HANDED_Y_UP;

    auto returned_state = zed_.open(init_parameters);
    if (returned_state != ERROR_CODE::SUCCESS) {
        Print("Open Camera", returned_state, "\nExit program.");
        zed_.close();
        return EXIT_FAILURE;
    }
}

int ZedTracker::EnablePositionalTracking() {
    logDebug << __func__;
    // Enable Positional tracking (mandatory for object detection)
    //If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    auto returned_state = zed_.enablePositionalTracking(positional_tracking_parameters_);
    if (returned_state != ERROR_CODE::SUCCESS) {
        Print("enable Positional Tracking", returned_state, "\nExit program.");
        zed_.close();
        return EXIT_FAILURE;
    }
}

int ZedTracker::EnableBodyTracking() {
    logDebug << __func__;
    // Set initialization parameters
    object_detection_parameters_.enable_tracking = true; // Objects will keep the same ID between frames
    object_detection_parameters_.detection_model = isJetson ? DETECTION_MODEL::HUMAN_BODY_FAST : DETECTION_MODEL::HUMAN_BODY_ACCURATE;
    object_detection_parameters_.enable_body_fitting = true; // Fitting process is called, user have access to all available informations for a person processed by SDK
    object_detection_parameters_.body_format = BODY_FORMAT::POSE_34; // selects the 34 keypoints body model for SDK outputs

    // Set runtime parameters
    object_detection_runtime_parameters_.detection_confidence_threshold = 40;

    auto returned_state = zed_.enableObjectDetection(object_detection_parameters_);
    if (returned_state != ERROR_CODE::SUCCESS) {
        Print("enable Object Detection", returned_state, "\nExit program.");
        zed_.close();
        return EXIT_FAILURE;
    }
}

std::tuple<cv::Mat, sl::float2> ZedTracker::GetImageConfiguration() {
    logDebug << __func__;
    // For 2D GUI
    auto camera_config = zed_.getCameraInformation().camera_configuration;
    Resolution display_resolution(min((int)camera_config.resolution.width, 1280), min((int)camera_config.resolution.height, 720));
    cv::Mat image_left_ocv(display_resolution.height, display_resolution.width, CV_8UC4, 1);
    Mat image_left(display_resolution, MAT_TYPE::U8_C4, image_left_ocv.data, image_left_ocv.step);
    sl::float2 image_scale(display_resolution.width / (float)camera_config.resolution.width, display_resolution.height / (float) camera_config.resolution.height);
    return {image_left_ocv, image_scale};
}

void ZedTracker::Print(std::string msg_prefix, ERROR_CODE err_code, std::string msg_suffix) {
    cout << "[Sample]";
    if (err_code != ERROR_CODE::SUCCESS)
        cout << "[Error]";
    cout << " " << msg_prefix << " ";
    if (err_code != ERROR_CODE::SUCCESS) {
        cout << " | " << toString(err_code) << " : ";
        cout << toVerbose(err_code);
    }
    if (!msg_suffix.empty())
        cout << " " << msg_suffix;
    cout << endl;
}
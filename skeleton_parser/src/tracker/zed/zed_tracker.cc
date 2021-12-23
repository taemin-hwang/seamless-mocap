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
#include <utility>
#include <cmath> // isnan
#include <opencv2/cvconfig.h>

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

    sl::Resolution camera_resolution = zed_.getCameraInformation().camera_configuration.resolution;
    Resolution display_resolution(min((int)camera_resolution.width, 1280), min((int)camera_resolution.height, 720));
    cv::Mat image_ocv(display_resolution.height, display_resolution.width, CV_8UC4, 1);
    sl::Mat image_zed(display_resolution, MAT_TYPE::U8_C4, image_ocv.data, image_ocv.step);
    sl::float2 image_scale(display_resolution.width / (float)camera_resolution.width, display_resolution.height / (float) camera_resolution.height);

    bool quit = false;
    char key = ' ';
    float current_fps = 0.0;
    bool is_tracking_on = object_detection_parameters_.enable_tracking;
    int person_id = 0;

    seamless::PersonKeypoints person_keypoints;
    seamless::PeopleKeypoints people_keypoints;
    seamless::PersonKeypointsWithConfidence person_keypoints_with_confidence;
    seamless::PeopleKeypointsWithConfidence people_keypoints_with_confidence;
    seamless::PersonBoundBox person_bound_box;
    seamless::PeopleBoundBox people_bound_box;

    // Set person keypoint length woth body format
    SetLengthWithBodyFormat(person_keypoints, person_keypoints_with_confidence, object_detection_parameters_.body_format);

    while(!quit && key != 'q') {
        if (zed_.grab() == ERROR_CODE::SUCCESS) {
            zed_.retrieveImage(image_zed, sl::VIEW::LEFT, sl::MEM::CPU, display_resolution);
            zed_.retrieveObjects(bodies, object_detection_runtime_parameters_);

            // Set vector size with number of people
            SetLengthWithNumberOfPeople(people_keypoints, people_keypoints_with_confidence, people_bound_box, bodies.object_list.size());

            person_id = 0;
            for (auto i = bodies.object_list.rbegin(); i != bodies.object_list.rend(); ++i) {
                sl::ObjectData& obj = (*i);
                if (renderObject(obj, is_tracking_on)) {
                    SetBoundingBox(person_bound_box, obj.bounding_box_2d, image_scale, obj.confidence);// set bounding box
                    SetKeypointPosition(person_keypoints, person_keypoints_with_confidence, obj.keypoint_2d, image_scale);// set skeleton joints
                    SetKeypointConfidence(person_keypoints, person_keypoints_with_confidence, obj.keypoint_confidence);// set skeleton joints
                    SetPersonId(person_keypoints_with_confidence, obj.id);// set person id
                }
                SetPeopleKeypoint(person_id, people_keypoints, obj.id, person_keypoints);
                SetPeopleKeypointWithConfidence(person_id, people_keypoints_with_confidence, person_keypoints_with_confidence);
                SetPeopleBoundBox(person_id, people_bound_box, person_bound_box);
                person_id++;
            }

            if (viewer_handler != nullptr) viewer_handler(image_ocv, {image_scale.x, image_scale.y}, people_keypoints);
            if (transfer_handler != nullptr) transfer_handler(people_bound_box, people_keypoints_with_confidence);

            current_fps = zed_.getCurrentFPS();
            if (current_fps > 0.0) { logInfo << "Current FPS : " << current_fps; }

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
    init_parameters.camera_resolution = RESOLUTION::HD720; //HD2K, HD1080, HD720, VGA
    // On Jetson the object detection combined with an heavy depth mode could reduce the frame rate too much
    init_parameters.depth_mode = DEPTH_MODE::PERFORMANCE;
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
    object_detection_parameters_.detection_model = DETECTION_MODEL::HUMAN_BODY_FAST;
    object_detection_parameters_.enable_body_fitting = true; // Fitting process is called, user have access to all available informations for a person processed by SDK
    // object_detection_parameters_.body_format = BODY_FORMAT::POSE_34; // selects the 34 keypoints body model for SDK outputs
    object_detection_parameters_.body_format = BODY_FORMAT::POSE_18; // selects the 34 keypoints body model for SDK outputs

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

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

#ifndef _ZED_TRACKER_H_
#define _ZED_TRACKET_H_

#include <string>
#include <tuple>
#include <iostream>
#include <deque>
#include <vector>
#include <math.h>

#include <opencv2/opencv.hpp>
#include <opencv2/cvconfig.h>

// ZED includes
#include <sl/Camera.hpp>

// Sample includes
#include "tracker/tracker_interface.h"

class ZedTracker {
 public:
    ZedTracker();
    virtual ~ZedTracker() = default;

    void Initialize();
    void Run();
    void Shutdown();

    virtual void SetViewerHandler(std::function<void(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints&)> f) { viewer_handler = f; };
    virtual void SetTransferHandler(std::function<void(const seamless::PeopleSkeleton&)> f) { transfer_handler = f; };

 private:
    int OpenCamera();
    int EnablePositionalTracking();
    int EnableBodyTracking();
    std::vector<std::vector<float>> GetDepthKeypoint(sl::BodyData obj, sl::Mat depth_map, sl::Resolution display_resolution);
    std::tuple<cv::Mat, sl::float2> GetImageConfiguration();
    void Print(std::string msg_prefix, sl::ERROR_CODE err_code, std::string msg_suffix);
    template<typename T>
    inline cv::Point2f cvt(T pt, sl::float2 scale) {
       return cv::Point2f(pt.x * scale.x, pt.y * scale.y);
    }
    inline bool renderObject(const sl::BodyData& i, const bool isTrackingON) {
        if (isTrackingON)
            return (i.tracking_state == sl::OBJECT_TRACKING_STATE::OK);
        else
            return (i.tracking_state == sl::OBJECT_TRACKING_STATE::OK || i.tracking_state == sl::OBJECT_TRACKING_STATE::OFF);
    }
    cv::Mat slMat2cvMat(sl::Mat& input) {
       // Since cv::Mat data requires a uchar* pointer, we get the uchar1 pointer from sl::Mat (getPtr<T>())
       // cv::Mat and sl::Mat will share a single memory structure
       return cv::Mat(input.getHeight(), input.getWidth(), getOCVtype(input.getDataType()), input.getPtr<sl::uchar1>(sl::MEM::CPU), input.getStepBytes(sl::MEM::CPU));
    }

    // Mapping between MAT_TYPE and CV_TYPE
    int getOCVtype(sl::MAT_TYPE type) {
       int cv_type = -1;
       switch (type) {
          case sl::MAT_TYPE::F32_C1: cv_type = CV_32FC1; break;
          case sl::MAT_TYPE::F32_C2: cv_type = CV_32FC2; break;
          case sl::MAT_TYPE::F32_C3: cv_type = CV_32FC3; break;
          case sl::MAT_TYPE::F32_C4: cv_type = CV_32FC4; break;
          case sl::MAT_TYPE::U8_C1: cv_type = CV_8UC1; break;
          case sl::MAT_TYPE::U8_C2: cv_type = CV_8UC2; break;
          case sl::MAT_TYPE::U8_C3: cv_type = CV_8UC3; break;
          case sl::MAT_TYPE::U8_C4: cv_type = CV_8UC4; break;
          default: break;
       }
        return cv_type;
     }

    inline void SetLengthWithBodyFormat(seamless::PersonKeypoints& person_keypoints, seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence, sl::BODY_FORMAT body_format){
       if(body_format == sl::BODY_FORMAT::BODY_18) {
          person_keypoints.resize(18);
          person_keypoints_with_confidence.resize(18);
       } else {
          person_keypoints.resize(34);
          person_keypoints_with_confidence.resize(34);
       }
    }

    inline void SetLengthWithNumberOfPeople(seamless::PeopleKeypoints& people_keypoints, seamless::PeopleKeypointsWithConfidence& people_keypoints_with_confidence, seamless::PeopleBoundBox& people_bound_box, int num_of_people) {
       people_keypoints.resize(num_of_people);
       people_keypoints_with_confidence.resize(num_of_people);
       people_bound_box.resize(num_of_people);
    }

    inline void SetBoundingBox(seamless::PersonBoundBox& person_bound_box, std::vector<sl::uint2> bounding_box_2d, sl::float2 image_scale, float confidence) {
       cv::Point2f left_top = cvt(bounding_box_2d[0], image_scale);
       cv::Point2f right_bottom = cvt(bounding_box_2d[2], image_scale);
       person_bound_box.SetLeftTop({left_top.x, left_top.y});
       person_bound_box.SetRightBottom({right_bottom.x, right_bottom.y});
       person_bound_box.SetConfidence(confidence/100);
    }

    inline void SetKeypointPosition(seamless::PersonKeypoints& person_keypoints, seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence, std::vector< sl::float2 > keypoint_2d, sl::float2 image_scale){
       int joint_id = 0;
       for (auto &kp : keypoint_2d) {
          cv::Point2f cv_kp = cvt(kp, image_scale);
          person_keypoints[joint_id] = cv_kp;
          person_keypoints_with_confidence.SetKeypointWithId(joint_id, {cv_kp.x, cv_kp.y});
          joint_id++;
       }
    }

    inline void SetKeypointConfidence(seamless::PersonKeypoints& person_keypoints, seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence, std::vector<float> keypoint_confidence) {
       int joint_id = 0;
       for (auto &c : keypoint_confidence) {
          float confidence = 0.0;
          if(isnan(c) == 0) confidence = c;
          person_keypoints_with_confidence.SetConfidenceWithId(joint_id, confidence);
          joint_id++;
       }
    }

    inline void SetDepthKeypoints(seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence, std::vector<std::vector<float>> depth_keypoints) {
       person_keypoints_with_confidence.SetDepthPoint(depth_keypoints);
    }

    inline void SetPersonId(seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence, int id){
       person_keypoints_with_confidence.SetId(id);
    }

    inline void SetPeopleKeypoint(int person_id, seamless::PeopleKeypoints& people_keypoints, int id, seamless::PersonKeypoints person_keypoints){
       people_keypoints[person_id].first = id;
       people_keypoints[person_id].second = person_keypoints;
    }

    inline void SetPeopleKeypointWithConfidence(int person_id, seamless::PeopleKeypointsWithConfidence& people_keypoints_with_confidence, seamless::PersonKeypointsWithConfidence& person_keypoints_with_confidence) {
       people_keypoints_with_confidence[person_id] = person_keypoints_with_confidence;
    }

    inline void SetPeopleBoundBox(int person_id, seamless::PeopleBoundBox& people_bound_box, seamless::PersonBoundBox person_bound_box) {
       people_bound_box[person_id] = person_bound_box;
    }

    inline void SetPeopleSkeleton(seamless::PeopleSkeleton& people_skeleton, seamless::PeopleBoundBox& people_bound_box, seamless::PeopleKeypointsWithConfidence& people_keypoints_with_confidence, seamless::TimestampMilliseconds timestamp, sl::Resolution display_resolution, int serial_number) {
       people_skeleton.SetPeopleBoundBox(people_bound_box);
       people_skeleton.SetPeopleKeypointsWithConfidence(people_keypoints_with_confidence);
       people_skeleton.SetTimestampMilliseconds(timestamp);
       people_skeleton.SetFrameSize({display_resolution.width, display_resolution.height});
       people_skeleton.SetCameraId(serial_number);
    }

 private:
    sl::Camera zed_;
    sl::InitParameters init_parameters_;
    sl::RuntimeParameters runtime_parameters_;
    sl::PositionalTrackingParameters positional_tracking_parameters_;
    //sl::ObjectDetectionParameters object_detection_parameters_;
    //sl::ObjectDetectionRuntimeParameters object_detection_runtime_parameters_;
    sl::BodyTrackingParameters object_detection_parameters_;
    sl::BodyTrackingRuntimeParameters object_detection_runtime_parameters_;
    bool is_playback_ = false;
    float fx_ = 0.0;
    float fy_ = 0.0;
    float cx_ = 0.0;
    float cy_ = 0.0;

   std::function<void(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints&)> viewer_handler = nullptr;
   std::function<void(const seamless::PeopleSkeleton&)> transfer_handler = nullptr;
};

#endif

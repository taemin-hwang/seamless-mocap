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
    virtual void SetTransferHandler(std::function<void(const seamless::PeopleKeypoints&)> f) { transfer_handler = f; };

 private:
    int OpenCamera();
    int EnablePositionalTracking();
    int EnableBodyTracking();
    std::tuple<cv::Mat, sl::float2> GetImageConfiguration();
    void Print(std::string msg_prefix, sl::ERROR_CODE err_code, std::string msg_suffix);
    template<typename T>
    inline cv::Point2f cvt(T pt, sl::float2 scale) {
       return cv::Point2f(pt.x * scale.x, pt.y * scale.y);
    }
    inline bool renderObject(const sl::ObjectData& i, const bool isTrackingON) {
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

 private:
    sl::Camera zed_;
    sl::InitParameters init_parameters_;
    sl::RuntimeParameters runtime_parameters_;
    sl::PositionalTrackingParameters positional_tracking_parameters_;
    sl::ObjectDetectionParameters object_detection_parameters_;
    sl::ObjectDetectionRuntimeParameters object_detection_runtime_parameters_;
    bool is_playback_ = false;

   std::function<void(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints&)> viewer_handler = nullptr;
   std::function<void(const seamless::PeopleKeypoints&)> transfer_handler = nullptr;
};

#endif
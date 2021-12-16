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

#include <opencv2/opencv.hpp>

// ZED includes
#include <sl/Camera.hpp>

// Sample includes
#include "viewer/gl_viewer.h"
#include "viewer/tracking_viewer.h"

#include "tracker/tracker_interface.h"

class ZedTracker {
 public:
    ZedTracker();
    virtual ~ZedTracker() = default;

    void Initialize();
    void Run();
    void Shutdown();

 public:
    int OpenCamera();
    int EnablePositionalTracking();
    int EnableBodyTracking();
    sl::float2 GetImageScale();
    void Print(std::string msg_prefix, ERROR_CODE err_code, std::string msg_suffix);
    template<typename T>
    inline cv::Point2f cvt(T pt, sl::float2 scale) {
       return cv::Point2f(pt.x * scale.x, pt.y * scale.y);
    }
 private:
    Camera zed_;
    PositionalTrackingParameters positional_tracking_parameters_;
    ObjectDetectionParameters object_detection_parameters_;
    ObjectDetectionRuntimeParameters object_detection_runtime_parameters_;

    bool is_playback_ = false;
};

#endif
#ifndef _TRACKER_INTERFACE_H_
#define _TRACKER_INTERFACE_H_

#include <vector>
#include <functional>

#include <opencv2/opencv.hpp>

#include "system/logger/logger.h"
#include "system/types.h"

enum class BodyFormat { kPose18, kPose34 };
enum class DetectionModel { kFast, kMedium, kAccurate};

class TrackerInterface {
 public:
    TrackerInterface(BodyFormat body_format, DetectionModel detection_model) {
       body_format_ = body_format;
       detection_model_ = detection_model;
    }
    virtual ~TrackerInterface() = default;

    virtual void Initialize() = 0;
    virtual void Run() = 0;
    virtual void Shutdown() = 0;
    virtual void SetViewerHandler(std::function<void(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints&)> f) { viewer_handler = f; };
    virtual void SetTransferHandler(std::function<void(const seamless::PeopleSkeleton&)> f) { transfer_handler = f; };

 protected:
    BodyFormat body_format_;
    DetectionModel detection_model_;

   // param1: OpenCV matrix including RGB image
   // param2: x, y scale for resolution
   // param3: a vector of 2D human skeleton
   std::function<void(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints&)> viewer_handler = nullptr;
   std::function<void(const seamless::PeopleSkeleton&)> transfer_handler = nullptr;
};

#endif
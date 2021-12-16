#ifndef _TRACKER_INTERFACE_H_
#define _TRACKER_INTERFACE_H_

#include <vector>
#include <functional>

#include "system/logger/logger.h"

enum class BodyFormat { kPose18, kPose34 };
enum class DetectionModel { kFast, kMedium, kAccurate};

using XYCoordinate = std::pair<float, float>;
using PersonKeypoints = std::vector<XYCoordinate>;
using PeopleKeypoints = std::vector<PersonKeypoints>;

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
    virtual void SetViewerHandler(std::function<void(const PeopleKeypoints&)> f) { viewer_handler = f; };
    virtual void SetTransferHandler(std::function<void(const PeopleKeypoints&)> f) { transfer_handler = f; };

 protected:
    BodyFormat body_format_;
    DetectionModel detection_model_;

   std::function<void(const PeopleKeypoints&)> viewer_handler = nullptr;
   std::function<void(const PeopleKeypoints&)> transfer_handler = nullptr;
};

#endif
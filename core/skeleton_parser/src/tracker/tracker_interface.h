#ifndef _TRACKER_INTERFACE_H_
#define _TRACKER_INTERFACE_H_

#include "system/logger/logger.h"

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
    virtual void GetHumanKeypoints() = 0;

 protected:
    BodyFormat body_format_;
    DetectionModel detection_model_;
};

#endif
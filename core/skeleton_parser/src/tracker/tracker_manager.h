#ifndef _TRACKER_MANAGER_H_
#define _TRACKER_MANAGER_H_

#include <memory>

#include "tracker/tracker_interface.h"
#include "tracker/zed/zed_tracker.h"

class TrackerManager : public TrackerInterface {
 public:
    TrackerManager(BodyFormat body_format, DetectionModel detection_model);
    virtual ~TrackerManager();

    void Initialize() override;
    void Run() override;
    void Shutdown() override;
    void GetHumanKeypoints() override;

 private:
    std::unique_ptr<ZedTracker> zed_tracker_;
};

#endif
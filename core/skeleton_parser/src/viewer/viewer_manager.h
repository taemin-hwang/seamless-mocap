#ifndef _VIEWER_MANAGER_H_
#define _VIEWER_MANAGER_H_

#include <vector>
#include <memory>

#include <opencv2/opencv.hpp>

#include "system/logger/logger.h"
#include "system/types.h"
#include "viewer/gui_2d_viewer.h"


class ViewerManager {
 public:
    ViewerManager();
    virtual ~ViewerManager() = default;

    void Initialize();
    void Run();
    void Shutdown();

    void DisplayPeopleKeypoints(const cv::Mat&, const seamless::PeopleKeypoints& people_keypoints);

 private:
    std::unique_ptr<Gui2DViewer> gui_2d_viewer_;
};

#endif

#include <string>

#include "viewer/gui_2d_viewer.h"

Gui2DViewer::Gui2DViewer()
{
    logDebug << __func__;
}

void Gui2DViewer::Display2DViewer(const cv::Mat &display, const seamless::PeopleKeypoints &people_keypoints)
{
    cv::Mat overlay = display.clone();
    char key = ' ';

    std::string window_name = "2D view";
    int person_id = 0;
    for (auto& person_keypoints : people_keypoints) {

        int person_tracking_id = person_keypoints.first;
       // auto clr_id = generateColorID(person_tracking_id);
        cv::Scalar color = generateColorID_u(person_tracking_id);
        int joint_id = 0;
        if(person_keypoints.second.size() == 18) {
            for (auto& keypoints : person_keypoints.second){
                logDebug << "[" << person_id << "] [" << joint_id << "] : " << keypoints.first << ", " << keypoints.second;
                joint_id++;

                cv::circle(display, {keypoints.first, keypoints.second}, 3, color, -1);
            }
            person_id++;
        } else if (person_keypoints.second.size() == 34) {
            for (auto& keypoints : person_keypoints.second){
                logDebug << "[" << person_id << "] [" << joint_id << "] : " << keypoints.first << ", " << keypoints.second;
                joint_id++;

                cv::circle(display, {keypoints.first, keypoints.second}, 3, color, -1);
            }
            person_id++;
        } else {
            logError << "Unsupported human-keypoint size : " << person_keypoints.second.size();
        }
    }
    cv::addWeighted(display, 0.9, overlay, 0.1, 0.0, display);
    cv::imshow(window_name, display);
    key = cv::waitKey(10);
}

float4 Gui2DViewer::generateColorID(int idx) {
    if (idx < 0) return make_float4(236.0f, 184.0f, 36.0f, 255.0f);
    else {
        int const offset = std::max(0, idx % 8);
        return  make_float4(id_colors[offset][2] / 255.0f, id_colors[offset][1] / 255.0f, id_colors[offset][0] / 255.0f, 1.f);
    }
}

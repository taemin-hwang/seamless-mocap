
#include <string>

#include "viewer/gui_2d_viewer.h"

Gui2DViewer::Gui2DViewer()
{
    logDebug << __func__;
}

// Display people keypoints on display
void Gui2DViewer::Display2DViewer(const cv::Mat &display, const std::pair<float, float>& scale, const seamless::PeopleKeypoints &people_keypoints)
{
    cv::Mat overlay = display.clone();
    // Rendering rectangular over region of interest
    cv::Rect roi_render(0, 0, display.size().width, display.size().height);
    char key = ' ';

    std::string window_name = "2D view";
    int person_id = 0;
    for (auto& person_keypoints : people_keypoints) {

        int person_tracking_id = person_keypoints.first;
        auto person_keypoint_list = person_keypoints.second;
        cv::Scalar color = generateColorID_u(person_tracking_id);
        int joint_id = 0;
        if(person_keypoint_list.size() == 18 || person_keypoint_list.size() == 34) {
            // Display lines between keypoints
            if(person_keypoint_list.size() == 18) { // seamless::BODY_FORMAT::POSE_18
                    for (const auto& parts : seamless::SKELETON_BONES) {
                        auto kp_a = person_keypoint_list[getIdx(parts.first)];
                        auto kp_b = person_keypoint_list[getIdx(parts.second)];
                        if (roi_render.contains(kp_a) && roi_render.contains(kp_b)) {
                            DisplayLinesBetweenKeypoints(display, color, kp_a, kp_b);
                        }
                    }
                    auto hip_left = person_keypoint_list[getIdx(seamless::BODY_PARTS::LEFT_HIP)];
                    auto hip_right = person_keypoint_list[getIdx(seamless::BODY_PARTS::RIGHT_HIP)];
                    auto spine = (hip_left + hip_right) / 2;
                    auto neck = person_keypoint_list[getIdx(seamless::BODY_PARTS::NECK)];
                    if (hip_left.x > 0 && hip_left.y > 0 && hip_right.x > 0 && hip_right.y > 0 && neck.x > 0 && neck.y > 0) {
                        auto kp_a = spine;
                        auto kp_b = person_keypoint_list[getIdx(seamless::BODY_PARTS::NECK)];
                        if (roi_render.contains(kp_a) && roi_render.contains(kp_b)) {
                            DisplayLinesBetweenKeypoints(display, color, kp_a, kp_b);
                        }
                    }
            } else { // seamless::BODY_FORMAT::POSE_34
                    for (const auto& parts : seamless::BODY_BONES_POSE_34) {
                        auto kp_a = person_keypoint_list[getIdx(parts.first)];
                        auto kp_b = person_keypoint_list[getIdx(parts.second)];
                        if (roi_render.contains(kp_a) && roi_render.contains(kp_b)) {
                            DisplayLinesBetweenKeypoints(display, color, kp_a, kp_b);
                        }
                    }
            }
            // Display circles on keypoints
            for (auto& keypoints : person_keypoint_list){
                logDebug << "[" << person_id << "] [" << joint_id << "] : " << keypoints.x << ", " << keypoints.y;
                joint_id++;
                DisplayCirclesOnKeypoints(display, color, {keypoints.x, keypoints.y});
            }
            person_id++;
        } else {
            logError << "Unsupported human-keypoint size : " << person_keypoint_list.size();
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


// Display a line between 'from' and 'to'
void Gui2DViewer::DisplayLinesBetweenKeypoints(const cv::Mat &display, const cv::Scalar& color, const cv::Point2f& from, const cv::Point2f& to) {
    // int from_x = static_cast<int>(from.x);
    // int from_y = static_cast<int>(from.y);
    // int to_x = static_cast<int>(to.x);
    // int to_y = static_cast<int>(to.y);

    #if (defined(CV_VERSION_EPOCH) && CV_VERSION_EPOCH == 2)
    cv::line(left_display, kp_a, kp_b, color, 1);
    #else
    cv::line(display, from, to, color, 1, cv::LINE_AA);
    #endif
}

// Display a circle of 'pos'
void Gui2DViewer::DisplayCirclesOnKeypoints(const cv::Mat &display, const cv::Scalar& color, const cv::Point2f& pos) {
    // int pos_x = static_cast<int>(pos.x);
    // int pos_y = static_cast<int>(pos.y);

    cv::circle(display, pos, 3, color, -1);
}

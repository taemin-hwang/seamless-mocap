#include "viewer/gui_2d_viewer.h"

Gui2DViewer::Gui2DViewer()
{
    logDebug << __func__;
}

void Gui2DViewer::Display2DViewer(const cv::Mat &display, const seamless::PeopleKeypoints &people_keypoints)
{
    // cv::Rect roi_render(0, 0, display.size().width, display.size().height);

    // for (unsigned int i = 0; i < people_keypoints.size(); i++) {
    //     // draw skeletons
    //     auto clr_id = generateColorID(people_keypoints[i].first);
    //     if (people_keypoints.second.size() >= 0 && people_keypoints[0].second.size() == 18) {
    //                 // skeleton bones
    //                 for (const auto& parts : SKELETON_BONES) {
    //                     auto kp_a = cvt(people_keypoints[i].second[getIdx(parts.first)], img_scale);
    //                     auto kp_b = cvt(people_keypoints[i].second[getIdx(parts.second)], img_scale);
    //                     if (roi_render.contains(kp_a) && roi_render.contains(kp_b)) {

    //                         #if (defined(CV_VERSION_EPOCH) && CV_VERSION_EPOCH == 2)
    //                         cv::line(left_display, kp_a, kp_b, color, 1);
    //                         #else
    //                         cv::line(left_display, kp_a, kp_b, color, 1, cv::LINE_AA);
    //                         #endif
    //                     }
    //                 }
    //                 auto hip_left = people_keypoints[i].second[getIdx(sl::BODY_PARTS::LEFT_HIP)];
    //                 auto hip_right = people_keypoints[i].second[getIdx(sl::BODY_PARTS::RIGHT_HIP)];
    //                 auto spine = (hip_left + hip_right) / 2;
    //                 auto neck = people_keypoints[i].second[getIdx(sl::BODY_PARTS::NECK)];

    //                 if (hip_left.x > 0 && hip_left.y > 0 && hip_right.x > 0 && hip_right.y > 0 && neck.x > 0 && neck.y > 0) {
    //                     auto kp_a = cvt(spine, img_scale);
    //                     auto kp_b = cvt(people_keypoints[i].second[getIdx(sl::BODY_PARTS::NECK)], img_scale);
    //                     if (roi_render.contains(kp_a) && roi_render.contains(kp_b)) {
    //                         #if (defined(CV_VERSION_EPOCH) && CV_VERSION_EPOCH == 2)
    //                         cv::line(left_display, kp_a, kp_b, color, 1);
    //                         #else
    //                         cv::line(left_display, kp_a, kp_b, color, 1, cv::LINE_AA);
    //                         #endif
    //                     }
    //                 }

    //                 // skeleton joints
    //                 for (auto& kp : people_keypoints[i].second) {
    //                     cv::Point2f cv_kp = cvt(kp, img_scale);
    //                     if (roi_render.contains(cv_kp))
    //                         cv::circle(left_display, cv_kp, 3, color, -1);
    //                 }
    //                 cv::Point2f cv_kp = cvt(spine, img_scale);
    //                 if (hip_left.x > 0 && hip_left.y > 0 && hip_right.x > 0 && hip_right.y > 0)
    //                     cv::circle(left_display, cv_kp, 3, color, -1);
    //     }
    //     else if (people_keypoints[0].size() == 34) {
    //         // skeleton bones
    //         for (const auto& parts : sl::BODY_BONES_POSE_34) {
    //             auto kp_a = cvt(people_keypoints[i].second[getIdx(parts.first)], img_scale);
    //             auto kp_b = cvt(people_keypoints[i].second[getIdx(parts.second)], img_scale);
    //             if (roi_render.contains(kp_a) && roi_render.contains(kp_b))
    //             {

    //                 #if (defined(CV_VERSION_EPOCH) && CV_VERSION_EPOCH == 2)
    //                 cv::line(left_display, kp_a, kp_b, color, 1);
    //                 #else
    //                 cv::line(left_display, kp_a, kp_b, color, 1, cv::LINE_AA);
    //                 #endif
    //             }
    //         }

    //         // skeleton joints
    //         for (auto& kp : people_keypoints[i].second) {
    //             cv::Point2f cv_kp = cvt(kp, img_scale);
    //             if (roi_render.contains(cv_kp))
    //                 cv::circle(left_display, cv_kp, 3, color, -1);
    //         }
    //     }
    //     else
    //     {
    //         logError << "Unsupported body format! : " << people_keypoints[0].second.size();
    //     }
    // }
}

// float4 generateColorID(int idx) {
//     if (idx < 0) return float4(236, 184, 36, 255);
//     else {
//         int const offset = std::max(0, idx % 8);
//         return  float4(id_colors[offset][2] / 255.0f, id_colors[offset][1] / 255.0f, id_colors[offset][0] / 255.0f, 1.f);
//     }
// }

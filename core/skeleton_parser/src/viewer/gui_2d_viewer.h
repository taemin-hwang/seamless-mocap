#ifndef _GUI_2D_VIEWER_H_
#define _GUI_2D_VIEWER_H_

#include <utility> // std::pair

#include <GL/glew.h>
#include <GL/freeglut.h>

#include <cuda.h>
#include <cuda_gl_interop.h>
#include <vector_types.h> // float4
#include <vector_functions.h> // make_float4

#include <opencv2/opencv.hpp>

#include "system/logger/logger.h"
#include "system/types.h"
#include "system/body_parts.h"

class Gui2DViewer {
 public:
    Gui2DViewer();
    void Display2DViewer(const cv::Mat&, const std::pair<float, float>&, const seamless::PeopleKeypoints& people_keypoints);

 private:
    float4 generateColorID(int idx);

    inline cv::Scalar generateColorID_u(int idx) {
        if (idx < 0) return cv::Scalar(236, 184, 36, 255);
        int color_idx = idx % 8;
        return cv::Scalar(id_colors[color_idx][0], id_colors[color_idx][1], id_colors[color_idx][2], 255);
    }

    template<typename T>
    inline cv::Point2f GetPointWithScale(T pt, const std::pair<float, float>& scale) {
       return cv::Point2f(pt.x * scale.first, pt.y * scale.second);
    }

    void DisplayLinesBetweenKeypoints(const cv::Mat &display, const cv::Scalar& color, const cv::Point2f& from, const cv::Point2f& to);
    void DisplayCirclesOnKeypoints(const cv::Mat &display, const cv::Scalar& color, const cv::Point2f& pos);

    float const id_colors[8][3] = {
        { 232.0f, 176.0f ,59.0f },
        { 175.0f, 208.0f ,25.0f },
        { 102.0f, 205.0f ,105.0f},
        { 185.0f, 0.0f   ,255.0f},
        { 99.0f, 107.0f  ,252.0f},
        {252.0f, 225.0f, 8.0f},
        {167.0f, 130.0f, 141.0f},
        {194.0f, 72.0f, 113.0f}
    };

};

#endif
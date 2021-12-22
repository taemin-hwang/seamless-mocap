#ifndef _SEAMLESS_TYPES_H_
#define _SEAMLESS_TYPES_H_

#include <opencv2/opencv.hpp>
#include <opencv2/cvconfig.h>

namespace seamless
{
    // Display 2D Skeleton (X, Y)
    using XYCoordinate = cv::Point2f;
    using PersonKeypoints = std::vector<XYCoordinate>;
    using PeopleKeypoints = std::vector<std::pair<int, PersonKeypoints>>;

    // Transfer 2D Skeleton (X, Y, Confidence)
    using XYZCoordinate = std::pair<std::pair<float, float>, float>;
    using PersonKeypointsWithConfidence = std::vector<XYZCoordinate>;
    using PeopleKeypointsWithConfidence = std::vector<std::pair<int, PersonKeypointsWithConfidence>>;
}

#endif /* _SEAMLESS_TYPES_H_ */
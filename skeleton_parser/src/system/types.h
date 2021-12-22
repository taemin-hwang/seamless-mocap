#ifndef _SEAMLESS_TYPES_H_
#define _SEAMLESS_TYPES_H_

#include <opencv2/opencv.hpp>
#include <opencv2/cvconfig.h>

namespace seamless
{
    // using XYCoordinate = std::pair<float, float>;
    using XYCoordinate = cv::Point2f;
    using PersonKeypoints = std::vector<XYCoordinate>;
    using PeopleKeypoints = std::vector<std::pair<int, PersonKeypoints>>;
}

#endif /* _SEAMLESS_TYPES_H_ */
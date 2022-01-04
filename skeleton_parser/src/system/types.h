#ifndef _SEAMLESS_TYPES_H_
#define _SEAMLESS_TYPES_H_

#include <cassert>

#include <opencv2/opencv.hpp>
#include <opencv2/cvconfig.h>

namespace seamless
{
    // Display 2D Skeleton (X, Y)
    using ObjectId = int;
    using XYCoordinate = cv::Point2f;
    using PersonKeypoints = std::vector<XYCoordinate>;
    using PeopleKeypoints = std::vector<std::pair<ObjectId, PersonKeypoints>>;

    // Transfer 2D Skeleton (X, Y, Confidence)
    class PersonKeypointsWithConfidence {
     public:
        PersonKeypointsWithConfidence() = default;
        virtual ~PersonKeypointsWithConfidence() = default;

        inline void resize(int size) { xy_keypoint_.resize(size); confidence_.resize(size); }
        inline int size() const { return xy_keypoint_.size(); }
        inline int GetId() const { return object_id_; }
        inline std::vector<std::pair<float, float>> GetKeypoint() const { return xy_keypoint_; }
        inline std::vector<float> GetConfidence() const { return confidence_; }
        inline void SetId(int id) { object_id_ = id; }
        inline void SetKeypointWithId(int id, std::pair<float, float> kp) {
            assert(xy_keypoint_.size() > id);
            xy_keypoint_[id] = kp;
        }
        inline void SetConfidenceWithId(int id, float confidence) {
            assert(confidence_.size() > id);
            confidence_[id] = confidence;
        }

     public:
        int object_id_;
        std::vector<std::pair<float, float>> xy_keypoint_;
        std::vector<float> confidence_;
    };

    // Transfer bounded box
    /* X ------ *
       | object |
       * ------ Y
    */
    class PersonBoundBox {
     public:
        PersonBoundBox() = default;
        virtual ~PersonBoundBox() = default;

        inline void SetLeftTop(const std::pair<int, int>& left_top) { left_top_ = left_top; }
        inline void SetRightBottom(const std::pair<int, int>& right_bottom) { right_bottom_ = right_bottom; }
        inline void SetConfidence(const float& confidence ) { confidence_ = confidence; }
        inline std::pair<int, int> GetLeftTop() const { return left_top_; }
        inline std::pair<int, int> GetRightBottom() const { return right_bottom_; }
        inline float GetConfidence() const { return confidence_; }

     private:
        std::pair<int, int> left_top_;
        std::pair<int, int> right_bottom_;
        float confidence_;
    };

    using PeopleKeypointsWithConfidence = std::vector<PersonKeypointsWithConfidence>;
    using PeopleBoundBox = std::vector<PersonBoundBox>;
    using TimestampMilliseconds = uint64_t;
    using FrameSize = std::pair<int, int>; //width, height

    class PeopleSkeleton {
     public:
        inline void SetPeopleKeypointsWithConfidence(const PeopleKeypointsWithConfidence& people_keypoints_with_confidence) { people_keypoints_with_confidence_ = people_keypoints_with_confidence; }
        inline void SetPeopleBoundBox(const PeopleBoundBox& people_bound_box) { people_bound_box_ = people_bound_box; }
        inline void SetTimestampMilliseconds(const TimestampMilliseconds& timestamp_ms) { timestamp_ms_ = timestamp_ms; }
        inline void SetFrameSize(const FrameSize& frame_size) { frame_size_ = frame_size; }
        inline void SetCameraId(const int& camera_id) { camera_id_ = camera_id; }
        inline PeopleKeypointsWithConfidence GetPeopleKeypointsWithConfidence() const { return people_keypoints_with_confidence_; }
        inline PeopleBoundBox GetPeopleBoundBox() const { return people_bound_box_; }
        inline TimestampMilliseconds GetTimestampMilliseconds() const { return timestamp_ms_; }
        inline FrameSize GetFrameSize() const { return frame_size_; }
        inline int GetCameraId() const {return camera_id_; }

     private:
        PeopleKeypointsWithConfidence people_keypoints_with_confidence_;
        PeopleBoundBox people_bound_box_;
        TimestampMilliseconds timestamp_ms_;
        FrameSize frame_size_;
        int camera_id_;
    };

}

#endif /* _SEAMLESS_TYPES_H_ */
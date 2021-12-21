#ifndef _SEAMLESS_BODY_PARTS_H_
#define _SEAMLESS_BODY_PARTS_H_

/*
 * Redefinition of enumeration in ZED Camera.hpp for systme's expandibility
 * url: https://www.stereolabs.com/developers/release/
 */

#include <vector>

template <typename Enumeration>
auto getIdx(Enumeration const value)
    -> typename std::underlying_type<Enumeration>::type
{
    return static_cast<typename std::underlying_type<Enumeration>::type>(value);
}

// Enumerate of 18 body parts same as openpose
namespace seamless {
enum class BODY_PARTS {
    NOSE = 0,
    NECK = 1,
    RIGHT_SHOULDER = 2,
    RIGHT_ELBOW = 3,
    RIGHT_WRIST = 4,
    LEFT_SHOULDER = 5,
    LEFT_ELBOW = 6,
    LEFT_WRIST = 7,
    RIGHT_HIP = 8,
    RIGHT_KNEE = 9,
    RIGHT_ANKLE = 10,
    LEFT_HIP = 11,
    LEFT_KNEE = 12,
    LEFT_ANKLE = 13,
    RIGHT_EYE = 14,
    LEFT_EYE = 15,
    RIGHT_EAR = 16,
    LEFT_EAR = 17,
    ///@cond SHOWHIDDEN
    LAST = 18
    ///@endcond
};

enum class BODY_PARTS_POSE_34
{
    PELVIS = 0,
    NAVAL_SPINE = 1,
    CHEST_SPINE = 2,
    NECK = 3,
    LEFT_CLAVICLE = 4,
    LEFT_SHOULDER = 5,
    LEFT_ELBOW = 6,
    LEFT_WRIST = 7,
    LEFT_HAND = 8,
    LEFT_HANDTIP = 9,
    LEFT_THUMB = 10,
    RIGHT_CLAVICLE = 11,
    RIGHT_SHOULDER = 12,
    RIGHT_ELBOW = 13,
    RIGHT_WRIST = 14,
    RIGHT_HAND = 15,
    RIGHT_HANDTIP = 16,
    RIGHT_THUMB = 17,
    LEFT_HIP = 18,
    LEFT_KNEE = 19,
    LEFT_ANKLE = 20,
    LEFT_FOOT = 21,
    RIGHT_HIP = 22,
    RIGHT_KNEE = 23,
    RIGHT_ANKLE = 24,
    RIGHT_FOOT = 25,
    HEAD = 26,
    NOSE = 27,
    LEFT_EYE = 28,
    LEFT_EAR = 29,
    RIGHT_EYE = 30,
    RIGHT_EAR = 31,
    LEFT_HEEL = 32,
    RIGHT_HEEL = 33,
    ///@cond SHOWHIDDEN
    LAST = 34
    ///@endcond
};

// Connection between each body part
const std::vector<std::pair< BODY_PARTS, BODY_PARTS>> SKELETON_BONES
{
    {BODY_PARTS::NOSE, BODY_PARTS::NECK},
    {BODY_PARTS::NECK, BODY_PARTS::RIGHT_SHOULDER},
    {BODY_PARTS::RIGHT_SHOULDER, BODY_PARTS::RIGHT_ELBOW},
    {BODY_PARTS::RIGHT_ELBOW, BODY_PARTS::RIGHT_WRIST},
    {BODY_PARTS::NECK, BODY_PARTS::LEFT_SHOULDER},
    {BODY_PARTS::LEFT_SHOULDER, BODY_PARTS::LEFT_ELBOW},
    {BODY_PARTS::LEFT_ELBOW, BODY_PARTS::LEFT_WRIST},
    {BODY_PARTS::RIGHT_HIP, BODY_PARTS::RIGHT_KNEE},
    {BODY_PARTS::RIGHT_KNEE, BODY_PARTS::RIGHT_ANKLE},
    {BODY_PARTS::LEFT_HIP, BODY_PARTS::LEFT_KNEE},
    {BODY_PARTS::LEFT_KNEE, BODY_PARTS::LEFT_ANKLE},
    {BODY_PARTS::RIGHT_SHOULDER, BODY_PARTS::LEFT_SHOULDER},
    {BODY_PARTS::RIGHT_HIP, BODY_PARTS::LEFT_HIP},
    {BODY_PARTS::NOSE, BODY_PARTS::RIGHT_EYE},
    {BODY_PARTS::RIGHT_EYE, BODY_PARTS::RIGHT_EAR},
    {BODY_PARTS::NOSE, BODY_PARTS::LEFT_EYE},
    {BODY_PARTS::LEFT_EYE, BODY_PARTS::LEFT_EAR}
};

const std::vector<std::pair<BODY_PARTS_POSE_34, BODY_PARTS_POSE_34>> BODY_BONES_POSE_34
{
    {BODY_PARTS_POSE_34::PELVIS, BODY_PARTS_POSE_34::NAVAL_SPINE},
    {BODY_PARTS_POSE_34::NAVAL_SPINE, BODY_PARTS_POSE_34::CHEST_SPINE},
    {BODY_PARTS_POSE_34::CHEST_SPINE, BODY_PARTS_POSE_34::LEFT_CLAVICLE},
    {BODY_PARTS_POSE_34::LEFT_CLAVICLE, BODY_PARTS_POSE_34::LEFT_SHOULDER},
    {BODY_PARTS_POSE_34::LEFT_SHOULDER, BODY_PARTS_POSE_34::LEFT_ELBOW},
    {BODY_PARTS_POSE_34::LEFT_ELBOW, BODY_PARTS_POSE_34::LEFT_WRIST},
    {BODY_PARTS_POSE_34::LEFT_WRIST, BODY_PARTS_POSE_34::LEFT_HAND},
    {BODY_PARTS_POSE_34::LEFT_HAND, BODY_PARTS_POSE_34::LEFT_HANDTIP},
    {BODY_PARTS_POSE_34::LEFT_WRIST, BODY_PARTS_POSE_34::LEFT_THUMB},
    {BODY_PARTS_POSE_34::CHEST_SPINE, BODY_PARTS_POSE_34::RIGHT_CLAVICLE},
    {BODY_PARTS_POSE_34::RIGHT_CLAVICLE, BODY_PARTS_POSE_34::RIGHT_SHOULDER},
    {BODY_PARTS_POSE_34::RIGHT_SHOULDER, BODY_PARTS_POSE_34::RIGHT_ELBOW},
    {BODY_PARTS_POSE_34::RIGHT_ELBOW, BODY_PARTS_POSE_34::RIGHT_WRIST},
    {BODY_PARTS_POSE_34::RIGHT_WRIST, BODY_PARTS_POSE_34::RIGHT_HAND},
    {BODY_PARTS_POSE_34::RIGHT_HAND, BODY_PARTS_POSE_34::RIGHT_HANDTIP},
    {BODY_PARTS_POSE_34::RIGHT_WRIST, BODY_PARTS_POSE_34::RIGHT_THUMB},
    {BODY_PARTS_POSE_34::PELVIS, BODY_PARTS_POSE_34::LEFT_HIP},
    {BODY_PARTS_POSE_34::LEFT_HIP, BODY_PARTS_POSE_34::LEFT_KNEE},
    {BODY_PARTS_POSE_34::LEFT_KNEE, BODY_PARTS_POSE_34::LEFT_ANKLE},
    {BODY_PARTS_POSE_34::LEFT_ANKLE, BODY_PARTS_POSE_34::LEFT_FOOT},
    {BODY_PARTS_POSE_34::PELVIS, BODY_PARTS_POSE_34::RIGHT_HIP},
    {BODY_PARTS_POSE_34::RIGHT_HIP, BODY_PARTS_POSE_34::RIGHT_KNEE},
    {BODY_PARTS_POSE_34::RIGHT_KNEE, BODY_PARTS_POSE_34::RIGHT_ANKLE},
    {BODY_PARTS_POSE_34::RIGHT_ANKLE, BODY_PARTS_POSE_34::RIGHT_FOOT},
    {BODY_PARTS_POSE_34::CHEST_SPINE, BODY_PARTS_POSE_34::NECK},
    {BODY_PARTS_POSE_34::NECK, BODY_PARTS_POSE_34::HEAD},
    {BODY_PARTS_POSE_34::HEAD, BODY_PARTS_POSE_34::NOSE},
    {BODY_PARTS_POSE_34::NOSE, BODY_PARTS_POSE_34::LEFT_EYE},
    {BODY_PARTS_POSE_34::LEFT_EYE, BODY_PARTS_POSE_34::LEFT_EAR},
    {BODY_PARTS_POSE_34::NOSE, BODY_PARTS_POSE_34::RIGHT_EYE},
    {BODY_PARTS_POSE_34::RIGHT_EYE, BODY_PARTS_POSE_34::RIGHT_EAR},
    {BODY_PARTS_POSE_34::LEFT_ANKLE, BODY_PARTS_POSE_34::LEFT_HEEL},
    {BODY_PARTS_POSE_34::RIGHT_ANKLE, BODY_PARTS_POSE_34::RIGHT_HEEL},
    {BODY_PARTS_POSE_34::LEFT_HEEL, BODY_PARTS_POSE_34::LEFT_FOOT},
    {BODY_PARTS_POSE_34::RIGHT_HEEL, BODY_PARTS_POSE_34::RIGHT_FOOT}
};

}

#endif /* _SEAMLESS_BODY_PARTS_H_ */

#include "transfer/transfer_manager.h"

void TransferManager::SendPeopleKeypoints(const seamless::PeopleKeypoints& people_keypoints) {
    int person_id = 0;
    for (auto& person_keypoints : people_keypoints) {
        int joint_id = 0;
        for (auto& keypoints : person_keypoints.second){
            //logDebug << "[" << person_id << "] [" << joint_id << "] : " << keypoints.first << ", " << keypoints.second;
            joint_id++;
        }
        person_id++;
    }
}

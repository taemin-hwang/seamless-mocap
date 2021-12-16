#ifndef _TRANSFER_INTERFACE_H_
#define _TRANSFER_INTERFACE_H_

struct HumanKeypoints {

};

class TransferInterface {
 public:
    TransferInterface() = default;
    virtual ~TransferInterface() = default;

    virtual void SendHumanKeypoints(HumanKeypoints human_keypoints) = 0;
};

#endif
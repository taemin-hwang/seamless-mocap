using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveSkeleton : MonoBehaviour
{
    public Animator animator;

    int NowFrame = 0;
    int MaxFrame = 799;

    Vector3 right_hand_pose, right_foot_pose, left_hand_pose, left_foot_pose;
    GameObject right_leg;
    GameObject sphere_right_hand, sphere_right_foot, sphere_right_leg, sphere_left_hand, sphere_left_foot;
    ReadSkeletonFromJson skeleton_reader;

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start Move Skeletons");
        transform.position = new Vector3(0, 0, 0);
        animator = GetComponent<Animator>();
        right_hand_pose = GameObject.Find("mixamorig:RightHand").transform.position;
        right_foot_pose = GameObject.Find("mixamorig:RightFoot").transform.position;
        left_hand_pose = GameObject.Find("mixamorig:LeftHand").transform.position;
        left_foot_pose = GameObject.Find("mixamorig:LeftFoot").transform.position;

        right_leg = GameObject.Find("mixamorig:RightLeg");

        sphere_right_hand = GameObject.Find("sphere_right_hand");
        sphere_right_foot = GameObject.Find("sphere_right_foot");
        sphere_right_leg = GameObject.Find("sphere_right_leg");
        sphere_left_hand = GameObject.Find("sphere_left_hand");
        sphere_left_foot = GameObject.Find("sphere_left_foot");

        skeleton_reader = new ReadSkeletonFromJson();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKey(KeyCode.RightArrow)) {
            if (NowFrame <= MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json";
                var skeletons = skeleton_reader.Get3DSkeletonFromJson(file_name);
                for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
                   Debug.Log("[" + i + "] : " + skeletons.keypoints3d[i][0] + ", " + skeletons.keypoints3d[i][1] + ", " + skeletons.keypoints3d[i][2] + ", " + skeletons.keypoints3d[i][3]);
                }
                right_hand_pose = new Vector3((float)skeletons.keypoints3d[4][0], (float)skeletons.keypoints3d[4][2], (float)skeletons.keypoints3d[4][1]);
                right_foot_pose = new Vector3((float)skeletons.keypoints3d[11][0], (float)skeletons.keypoints3d[11][2], (float)skeletons.keypoints3d[11][1]);
                left_hand_pose = new Vector3((float)skeletons.keypoints3d[7][0], (float)skeletons.keypoints3d[7][2], (float)skeletons.keypoints3d[7][1]);
                left_foot_pose = new Vector3((float)skeletons.keypoints3d[14][0], (float)skeletons.keypoints3d[14][2], (float)skeletons.keypoints3d[14][1]);

                right_leg.transform.position = new Vector3((float)skeletons.keypoints3d[10][0], (float)skeletons.keypoints3d[10][2], (float)skeletons.keypoints3d[10][1]);

                sphere_right_hand.transform.position = right_hand_pose;
                sphere_right_foot.transform.position = right_foot_pose;
                sphere_left_hand.transform.position = left_hand_pose;
                sphere_left_foot.transform.position = left_foot_pose;

                sphere_right_leg.transform.position = right_leg.transform.position;

                NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (NowFrame > 0) {
                NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json";
                var skeletons = skeleton_reader.Get3DSkeletonFromJson(file_name);
                for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
                   Debug.Log("[" + i + "] : " + skeletons.keypoints3d[i][0] + ", " + skeletons.keypoints3d[i][1] + ", " + skeletons.keypoints3d[i][2] + ", " + skeletons.keypoints3d[i][3]);
                }
                right_hand_pose = new Vector3((float)skeletons.keypoints3d[4][0], (float)skeletons.keypoints3d[4][2], (float)skeletons.keypoints3d[4][1]);
                right_foot_pose = new Vector3((float)skeletons.keypoints3d[11][0], (float)skeletons.keypoints3d[11][2], (float)skeletons.keypoints3d[11][1]);
                left_hand_pose = new Vector3((float)skeletons.keypoints3d[7][0], (float)skeletons.keypoints3d[7][2], (float)skeletons.keypoints3d[7][1]);
                left_foot_pose = new Vector3((float)skeletons.keypoints3d[14][0], (float)skeletons.keypoints3d[14][2], (float)skeletons.keypoints3d[14][1]);

                right_leg.transform.position = new Vector3((float)skeletons.keypoints3d[10][0], (float)skeletons.keypoints3d[10][2], (float)skeletons.keypoints3d[10][1]);

                sphere_right_hand.transform.position = right_hand_pose;
                sphere_right_foot.transform.position = right_foot_pose;
                sphere_left_hand.transform.position = left_hand_pose;
                sphere_left_foot.transform.position = left_foot_pose;

                sphere_right_leg.transform.position = right_leg.transform.position;
            }
        }
    }

    void OnAnimatorIK(int layerIndex) {
        //Debug.Log("Right Hand Pose : " + right_hand_pose.x + ", " + right_hand_pose.y + ", " + right_hand_pose.z);
        animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
        animator.SetIKPosition(AvatarIKGoal.RightHand, right_hand_pose);

        animator.SetIKPositionWeight(AvatarIKGoal.RightFoot, 1);
        animator.SetIKPosition(AvatarIKGoal.RightFoot, right_foot_pose);

        animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        animator.SetIKPosition(AvatarIKGoal.LeftHand, left_hand_pose);

        animator.SetIKPositionWeight(AvatarIKGoal.LeftFoot, 1);
        animator.SetIKPosition(AvatarIKGoal.LeftFoot, left_foot_pose);
    }
}

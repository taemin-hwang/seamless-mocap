using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveSkeleton : MonoBehaviour
{
    public Animator animator;

    int NowFrame = 0;
    int MaxFrame = 799;

    //Vector3 right_hand_pose, right_foot_pose, left_hand_pose, left_foot_pose;
    //GameObject right_leg;
    //GameObject sphere_right_hand, sphere_right_foot, sphere_right_leg, sphere_left_hand, sphere_left_foot;
    List<GameObject> spheres = new List<GameObject>(new GameObject[25]);
    List<GameObject> character = new List<GameObject>(new GameObject[25]);
    ReadSkeletonFromJson skeleton_reader;

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start Move Skeletons");
        transform.position = new Vector3(0, 0, 0);
        animator = GetComponent<Animator>();
        // right_hand_pose = GameObject.Find("mixamorig:RightHand").transform.position;
        // right_foot_pose = GameObject.Find("mixamorig:RightFoot").transform.position;
        // left_hand_pose = GameObject.Find("mixamorig:LeftHand").transform.position;
        // left_foot_pose = GameObject.Find("mixamorig:LeftFoot").transform.position;

        //right_leg = GameObject.Find("mixamorig:RightLeg");
        InitializeGameObject();
        // sphere_right_hand = GameObject.Find("sphere_right_wrist");
        // sphere_right_foot = GameObject.Find("sphere_right_ankle");
        // sphere_right_leg = GameObject.Find("sphere_right_knee");
        // sphere_left_hand = GameObject.Find("sphere_left_wrist");
        // sphere_left_foot = GameObject.Find("sphere_left_ankle");

        skeleton_reader = new ReadSkeletonFromJson();
    }

    void InitializeGameObject() {
        spheres[0] = GameObject.Find("sphere_nose");
        spheres[1] = GameObject.Find("sphere_neck");
        spheres[2] = GameObject.Find("sphere_right_shoulder");
        spheres[3] = GameObject.Find("sphere_right_elbow");
        spheres[4] = GameObject.Find("sphere_right_wrist");
        spheres[5] = GameObject.Find("sphere_left_shoulder");
        spheres[6] = GameObject.Find("sphere_left_elbow");
        spheres[7] = GameObject.Find("sphere_left_wrist");
        spheres[8] = GameObject.Find("sphere_mid_hip");
        spheres[9] = GameObject.Find("sphere_right_hip");
        spheres[10] = GameObject.Find("sphere_right_knee");
        spheres[11] = GameObject.Find("sphere_right_ankle");
        spheres[12] = GameObject.Find("sphere_left_hip");
        spheres[13] = GameObject.Find("sphere_left_knee");
        spheres[14] = GameObject.Find("sphere_left_ankle");
        spheres[15] = GameObject.Find("sphere_right_eye");
        spheres[16] = GameObject.Find("sphere_left_eye");
        spheres[17] = GameObject.Find("sphere_right_ear");
        spheres[18] = GameObject.Find("sphere_left_ear");
        spheres[19] = GameObject.Find("sphere_left_big_toe");
        spheres[20] = GameObject.Find("sphere_left_small_toe");
        spheres[21] = GameObject.Find("sphere_left_heel");
        spheres[22] = GameObject.Find("sphere_right_big_toe");
        spheres[23] = GameObject.Find("sphere_right_small_toe");
        spheres[24] = GameObject.Find("sphere_right_heel");


        character[0] = GameObject.Find("mixamorig:HeadTop_End");
        character[1] = GameObject.Find("mixamorig:Spine2");
        character[2] = GameObject.Find("mixamorig:RightArm");
        character[3] = GameObject.Find("mixamorig:RightForeArm");
        character[4] = GameObject.Find("mixamorig:RightHand");
        character[5] = GameObject.Find("mixamorig:LeftArm");
        character[6] = GameObject.Find("mixamorig:LeftForeArm");
        character[7] = GameObject.Find("mixamorig:LeftHand");
        character[8] = GameObject.Find("mixamorig:Hips");
        character[9] = GameObject.Find("mixamorig:RightUpLeg");
        character[10] = GameObject.Find("mixamorig:RightLeg");
        character[11] = GameObject.Find("mixamorig:RightFoot");
        character[12] = GameObject.Find("mixamorig:LeftUpLeg");
        character[13] = GameObject.Find("mixamorig:LeftLeg");
        character[14] = GameObject.Find("mixamorig:LeftFoot");
        character[15] = GameObject.Find("mixamorig:RightShoulder");
        character[16] = GameObject.Find("mixamorig:LeftShoulder");
        character[17] = null;
        character[18] = null;
        character[19] = null;
        character[20] = null;
        character[21] = null;
        character[22] = null;
        character[23] = null;
        character[24] = null;
    }


    // Update is called once per frame
    void Update()
    {
        if (Input.GetKey(KeyCode.RightArrow)) {
            if (NowFrame <= MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json";
                var skeletons = skeleton_reader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
                NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (NowFrame > 0) {
                NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json";
                var skeletons = skeleton_reader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
            }
        }
    }

    void Update3DPose(JsonElement skeletons) {
        for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
            Vector3 pos = new Vector3((float)skeletons.keypoints3d[i][0], (float)skeletons.keypoints3d[i][2], (float)skeletons.keypoints3d[i][1]);
            spheres[i].transform.position = pos * 0.9f;

            if (i <= 14) {
                if (i != 4 && i != 7 && i != 11 && i != 14 ) {
                    Debug.Log("[" + i + "] : " + skeletons.keypoints3d[i][0] + ", " + skeletons.keypoints3d[i][1] + ", " + skeletons.keypoints3d[i][2] + ", " + skeletons.keypoints3d[i][3]);
                    character[i].transform.position = pos * 0.9f;
                }
            }
        }

        transform.position = Vector3.Scale(spheres[8].transform.position, new Vector3(1.0f, 0.0f, 1.0f));
        //character[8].transform.position = character[8].transform.position * 0.66f + character[1].transform.position * 0.33f;
        //character[15].transform.position = character[2].transform.position * 0.33f + character[1].transform.position * 0.66f;
        //character[16].transform.position = character[5].transform.position * 0.33f + character[1].transform.position * 0.66f;
        // right_hand_pose = new Vector3((float)skeletons.keypoints3d[4][0], (float)skeletons.keypoints3d[4][2], (float)skeletons.keypoints3d[4][1]);
        // right_foot_pose = new Vector3((float)skeletons.keypoints3d[11][0], (float)skeletons.keypoints3d[11][2], (float)skeletons.keypoints3d[11][1]);
        // left_hand_pose = new Vector3((float)skeletons.keypoints3d[7][0], (float)skeletons.keypoints3d[7][2], (float)skeletons.keypoints3d[7][1]);
        // left_foot_pose = new Vector3((float)skeletons.keypoints3d[14][0], (float)skeletons.keypoints3d[14][2], (float)skeletons.keypoints3d[14][1]);

        //right_leg.transform.position = new Vector3((float)skeletons.keypoints3d[10][0], (float)skeletons.keypoints3d[10][2], (float)skeletons.keypoints3d[10][1]);

        // sphere_right_hand.transform.position = right_hand_pose;
        // sphere_right_foot.transform.position = right_foot_pose;
        // sphere_left_hand.transform.position = left_hand_pose;
        // sphere_left_foot.transform.position = left_foot_pose;

        //sphere_right_leg.transform.position = right_leg.transform.position;
    }

    void OnAnimatorIK(int layerIndex) {
        //Debug.Log("Right Hand Pose : " + right_hand_pose.x + ", " + right_hand_pose.y + ", " + right_hand_pose.z);
        animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
        animator.SetIKPosition(AvatarIKGoal.RightHand, spheres[4].transform.position);

        animator.SetIKPositionWeight(AvatarIKGoal.RightFoot, 1);
        animator.SetIKPosition(AvatarIKGoal.RightFoot, spheres[11].transform.position);

        animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        animator.SetIKPosition(AvatarIKGoal.LeftHand, spheres[7].transform.position);

        animator.SetIKPositionWeight(AvatarIKGoal.LeftFoot, 1);
        animator.SetIKPosition(AvatarIKGoal.LeftFoot, spheres[14].transform.position);
    }
}
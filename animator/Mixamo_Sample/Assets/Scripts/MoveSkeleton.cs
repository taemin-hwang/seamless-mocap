using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveSkeleton : MonoBehaviour
{
    public Animator animator;

    int NowFrame = 0;
    int MaxFrame = 799;

    List<GameObject> spheres = new List<GameObject>(new GameObject[25]);
    List<GameObject> character = new List<GameObject>(new GameObject[25]);
    GameObject aim;
    ReadSkeletonFromJson skeleton_reader;

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start Move Skeletons");
        skeleton_reader = new ReadSkeletonFromJson();
        transform.position = new Vector3(0, 0, 0);
        animator = GetComponent<Animator>();
        InitializeGameObject();
    }

    void InitializeGameObject() {
        aim = GameObject.Find("AimTarget");
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
        }

        // position
        transform.position = Vector3.Scale(spheres[8].transform.position, new Vector3(1.0f, 0.0f, 1.0f));

        // aim
        Vector3 head_pose = (spheres[17].transform.position + spheres[18].transform.position) * 0.5f;
        Vector3 nose_pose = spheres[0].transform.position;
        Vector3 direction = Vector3.Scale(nose_pose - head_pose, new Vector3(1.0f, 0.0f, 1.0f));
        aim.transform.position = nose_pose + 3 * direction;

        // rotation
        Vector3 body_axis = Vector3.Scale(spheres[9].transform.position - spheres[12].transform.position, new Vector3(1.0f, 0.0f, 1.0f));
        Vector3 z_axis = new Vector3(1.0f, 0.0f, 0.0f);
        float rotation_angle = Vector3.SignedAngle(body_axis, z_axis, new Vector3(0.0f, 1.0f, 0.0f));
        Debug.Log("Angle : " + -rotation_angle);
        transform.rotation = Quaternion.Euler(new Vector3(0, -rotation_angle, 0));
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
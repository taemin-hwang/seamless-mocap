using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveSkeleton : MonoBehaviour
{
    public Animator MainAnimator;
    public bool EnableDisplay;
    public float _BodyRatio = 0.25f;
    public float _MidHipOffset = 0.0f;

    int _NowFrame = 0;
    int _MaxFrame = 799;
    float _AvatarLegLength = 0.0f;
    float _MidHipYAxis = 0.0f;

    int _AverageCnt = 0;
    Queue<List<List<double>>> _SkeletonData = new Queue<List<List<double>>>();

    private bool spawned = false;
    private float decay;

    GameObject _Aim;
    ReceiveSkeleton _SkeletonReceiver;
    ReadSkeletonFromJson _SkeletonReader;
    SendRotation _RotationSender;
    JsonElement _Skeletons;

    List<GameObject> _Skeleton = new List<GameObject>(new GameObject[24]);
    List<GameObject> _Spheres = new List<GameObject>(new GameObject[25]);
    List<GameObject> _Show = new List<GameObject>(new GameObject[25]);

    Vector3 _HipPosition;
    List<Quaternion> _DifferentRotation = new List<Quaternion>(new Quaternion[24]);
    List<Quaternion> _InverseRotation = new List<Quaternion>(new Quaternion[24]);

    string _JsonPath = "/plask/";


    // Start is called before the first frame update
    async void Start()
    {
        Debug.Log("Start Move Skeletons : " + EnableDisplay);
        MainAnimator = GetComponent<Animator>();
        _SkeletonReader = new ReadSkeletonFromJson();
        _SkeletonReceiver = new ReceiveSkeleton("127.0.0.1", 50002);
        _RotationSender = new SendRotation();
        _SkeletonReceiver.Initialize();
        _SkeletonReceiver.SetMessageCallback(new CallbackMessage(ReceiveMessageHandler));
        InitializeGameObject();
        _MidHipYAxis = GameObject.Find("Bip001 Pelvis").transform.position.y + _MidHipOffset;
        SetObjectRendering(EnableDisplay);
        Debug.Log("Store JSON data to : " + Application.persistentDataPath + _JsonPath);
    }

    void InitializeGameObject() {
        // _Aim = GameObject.Find("HeadTarget");

        _Skeleton[0] = GameObject.Find("Bip001 Pelvis"); // Hips
        _Skeleton[1] = GameObject.Find("Bip001 L Thigh");  // Left Upper Leg
        _Skeleton[2] = GameObject.Find("Bip001 R Thigh"); // Right Upper Leg
        _Skeleton[3] = GameObject.Find("Bip001 Spine"); // Spine
        _Skeleton[4] = GameObject.Find("Bip001 L Calf"); // Left Lower Leg
        _Skeleton[5] = GameObject.Find("Bip001 R Calf"); // Right Lower Leg
        _Skeleton[6] = GameObject.Find("Bip001 Spine1"); // Chest
        _Skeleton[7] = GameObject.Find("Bip001 L Foot"); // Left Foot
        _Skeleton[8] = GameObject.Find("Bip001 R Foot"); // Right Foot
        _Skeleton[9] = GameObject.Find("Bip001 Spine2"); // Upper Chest
        _Skeleton[10] = GameObject.Find("Bip001 L Toe0"); // Left Toes
        _Skeleton[11] = GameObject.Find("Bip001 R Toe0"); // Right Toes
        _Skeleton[12] = GameObject.Find("Bip001 Neck"); // Neck
        _Skeleton[13] = GameObject.Find("Bip001 L Clavicle"); // Left Shoulder
        _Skeleton[14] = GameObject.Find("Bip001 R Clavicle"); // Right Shoulder
        _Skeleton[15] = GameObject.Find("Bip001 Head"); // Head
        _Skeleton[16] = GameObject.Find("Bip001 L UpperArm"); // Left Upper Arm
        _Skeleton[17] = GameObject.Find("Bip001 R UpperArm"); // Right Upper Arm
        _Skeleton[18] = GameObject.Find("Bip001 L Forearm"); // Left Lower Arm
        _Skeleton[19] = GameObject.Find("Bip001 R Forearm"); // Right Lower Arm
        _Skeleton[20] = GameObject.Find("Bip001 L Hand"); // Left Hand
        _Skeleton[21] = GameObject.Find("Bip001 R Hand"); // Right Hand
        _Skeleton[22] = GameObject.Find("Bip001 L Finger12"); // Left Index Distal
        _Skeleton[23] = GameObject.Find("Bip001 R Finger12"); // Right Index Distal

        for (int i = 0; i < 24; i++) {
            Debug.Log("Avatar Rotation " + i + " : " + _Skeleton[i].transform.localRotation);
            _InverseRotation[i] = new Quaternion(_Skeleton[i].transform.localRotation.x,
            _Skeleton[i].transform.localRotation.y,
            _Skeleton[i].transform.localRotation.z,
            _Skeleton[i].transform.localRotation.w);
            _InverseRotation[i] = Quaternion.Inverse(_InverseRotation[i]);
        }

        _Spheres[0] = GameObject.Find("sphere_nose");
        _Spheres[1] = GameObject.Find("sphere_neck");
        _Spheres[2] = GameObject.Find("sphere_right_shoulder");
        _Spheres[3] = GameObject.Find("sphere_right_elbow");
        _Spheres[4] = GameObject.Find("sphere_right_wrist");
        _Spheres[5] = GameObject.Find("sphere_left_shoulder");
        _Spheres[6] = GameObject.Find("sphere_left_elbow");
        _Spheres[7] = GameObject.Find("sphere_left_wrist");
        _Spheres[8] = GameObject.Find("sphere_mid_hip");
        _Spheres[9] = GameObject.Find("sphere_right_hip");
        _Spheres[10] = GameObject.Find("sphere_right_knee");
        _Spheres[11] = GameObject.Find("sphere_right_ankle");
        _Spheres[12] = GameObject.Find("sphere_left_hip");
        _Spheres[13] = GameObject.Find("sphere_left_knee");
        _Spheres[14] = GameObject.Find("sphere_left_ankle");
        _Spheres[15] = GameObject.Find("sphere_right_eye");
        _Spheres[16] = GameObject.Find("sphere_left_eye");
        _Spheres[17] = GameObject.Find("sphere_right_ear");
        _Spheres[18] = GameObject.Find("sphere_left_ear");
        _Spheres[19] = GameObject.Find("sphere_left_big_toe");
        _Spheres[20] = GameObject.Find("sphere_left_small_toe");
        _Spheres[21] = GameObject.Find("sphere_left_heel");
        _Spheres[22] = GameObject.Find("sphere_right_big_toe");
        _Spheres[23] = GameObject.Find("sphere_right_small_toe");
        _Spheres[24] = GameObject.Find("sphere_right_heel");

        _Show[0] = GameObject.Find("show_nose");
        _Show[1] = GameObject.Find("show_neck");
        _Show[2] = GameObject.Find("show_right_shoulder");
        _Show[3] = GameObject.Find("show_right_elbow");
        _Show[4] = GameObject.Find("show_right_wrist");
        _Show[5] = GameObject.Find("show_left_shoulder");
        _Show[6] = GameObject.Find("show_left_elbow");
        _Show[7] = GameObject.Find("show_left_wrist");
        _Show[8] = GameObject.Find("show_mid_hip");
        _Show[9] = GameObject.Find("show_right_hip");
        _Show[10] = GameObject.Find("show_right_knee");
        _Show[11] = GameObject.Find("show_right_ankle");
        _Show[12] = GameObject.Find("show_left_hip");
        _Show[13] = GameObject.Find("show_left_knee");
        _Show[14] = GameObject.Find("show_left_ankle");
        _Show[15] = GameObject.Find("show_right_eye");
        _Show[16] = GameObject.Find("show_left_eye");
        _Show[17] = GameObject.Find("show_right_ear");
        _Show[18] = GameObject.Find("show_left_ear");
        _Show[19] = GameObject.Find("show_left_big_toe");
        _Show[20] = GameObject.Find("show_left_small_toe");
        _Show[21] = GameObject.Find("show_left_heel");
        _Show[22] = GameObject.Find("show_right_big_toe");
        _Show[23] = GameObject.Find("show_right_small_toe");
        _Show[24] = GameObject.Find("show_right_heel");
    }

    void SetObjectRendering(bool enable_flag) {
        if (enable_flag == false) {
            // _Aim.SetActive(false);
            for (int i = 0; i < 25; i++) {
                _Spheres[i].SetActive(false);
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (_Skeletons != null && _Skeletons.keypoints3d.Count > 0) {
            Update3DPose(_Skeletons);
        }

        if (Input.GetKey(KeyCode.RightArrow)) {
            if (_NowFrame <= _MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d1/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
                _NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (_NowFrame > 0) {
                _NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d1/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
            }
        }
    }

    void ReceiveMessageHandler(JsonElement skeletons) {
        _Skeletons = skeletons;
    }

    void Update3DPose(JsonElement skeletons) {
        // sphere
        UpdateSpherePosition(skeletons);

        // position
        ChangeAvatarPosition(_Spheres[8].transform.position);

        // rotation
        Vector3 right_hip_pose = _Spheres[9].transform.position;
        Vector3 left_hip_pose = _Spheres[12].transform.position;
        ChangeAvatarRotation(right_hip_pose, left_hip_pose);

        // aim
        Vector3 head_pose = (_Spheres[17].transform.position + _Spheres[18].transform.position) * 0.5f;
        Vector3 nose_pose = _Spheres[0].transform.position;
        // SetHeadAim(head_pose, nose_pose);

        // send position and rotation
        UpdatePositionAndRotation();
    }

    void UpdateSpherePosition(JsonElement skeletons){
        for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
            if ((float)skeletons.keypoints3d[i][2] > 0.05f) {
                _Spheres[i].transform.position = new Vector3((float)skeletons.keypoints3d[i][0], (float)skeletons.keypoints3d[i][2], (float)skeletons.keypoints3d[i][1]) * _BodyRatio;
                _Show[i].transform.position = new Vector3((float)skeletons.keypoints3d[i][0]+1.0f, (float)skeletons.keypoints3d[i][2], (float)skeletons.keypoints3d[i][1]+1.0f) * _BodyRatio;
            }
        }
    }

    float GetBodyRatio(JsonElement skeletons) {
        Vector3 ForeArmPose = new Vector3((float)skeletons.keypoints3d[6][0], (float)skeletons.keypoints3d[6][2], (float)skeletons.keypoints3d[6][1]);
        Vector3 HandPose = new Vector3((float)skeletons.keypoints3d[7][0], (float)skeletons.keypoints3d[7][2], (float)skeletons.keypoints3d[7][1]);
        float SkeletonLegLength = Vector3.Distance(ForeArmPose, HandPose);

        return _AvatarLegLength / SkeletonLegLength;
    }

    void ChangeAvatarPosition(Vector3 hip_pose) {
        //transform.position = Vector3.Scale(hip_pose, new Vector3(1.0f, 0.0f, 1.0f));
        transform.position = new Vector3(hip_pose.x, hip_pose.y-_MidHipYAxis, hip_pose.z);
    }

    void SetHeadAim(Vector3 head_pose, Vector3 nose_pose) {
        Vector3 direction = Vector3.Scale(nose_pose - head_pose, new Vector3(1.0f, 0.0f, 1.0f));
        _Aim.transform.position = nose_pose + 5 * direction;
    }

    void ChangeAvatarRotation(Vector3 right_hip_pose, Vector3 left_hip_pose) {
        Vector3 body_axis = Vector3.Scale(right_hip_pose - left_hip_pose, new Vector3(1.0f, 0.0f, 1.0f));
        Vector3 z_axis = new Vector3(1.0f, 0.0f, 0.0f);
        float rotation_angle = Vector3.SignedAngle(body_axis, z_axis, new Vector3(0.0f, 1.0f, 0.0f));
        //Debug.Log("Right Hip : " + right_hip_pose + ", Left Hip : " + left_hip_pose + ", Angle : " + -rotation_angle);
        Debug.Log("Angle : " + -rotation_angle);
        transform.rotation = Quaternion.Euler(new Vector3(0, -rotation_angle, 0));
    }

    void UpdatePositionAndRotation() {
        Debug.Log("HipPosition : " + _Skeleton[0].transform.position);
        _HipPosition = new Vector3(_Skeleton[0].transform.position.x, _Skeleton[0].transform.position.y, _Skeleton[0].transform.position.z);
        for (int i = 0; i < 24; i++) {
            Quaternion CurrentRotation = new Quaternion(0f, 0f, 0f, 0f);
            if (i == 0) {
                CurrentRotation = new Quaternion(_Skeleton[i].transform.rotation.x,
                    _Skeleton[i].transform.rotation.y,
                    _Skeleton[i].transform.rotation.z,
                    _Skeleton[i].transform.rotation.w);
            } else {
                CurrentRotation = new Quaternion(_Skeleton[i].transform.localRotation.x,
                    _Skeleton[i].transform.localRotation.y,
                    _Skeleton[i].transform.localRotation.z,
                    _Skeleton[i].transform.localRotation.w);
            }

            _DifferentRotation[i] = CurrentRotation * _InverseRotation[i];
            // Debug.Log("Rotation " + i + " : " + _DifferentRotation[i]);
        }

        _RotationSender.SaveJsonStringFromRotation(Application.persistentDataPath + _JsonPath, 0, _HipPosition, _DifferentRotation);
    }


    void OnAnimatorIK(int layerIndex) {
        //Debug.Log("Right Hand Pose : " + _Spheres[4].transform.position.x + ", " + _Spheres[4].transform.position.y + ", " + _Spheres[4].transform.position.z);
        MainAnimator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.RightHand, _Spheres[4].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.RightFoot, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.RightFoot, _Spheres[11].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftHand, _Spheres[7].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftFoot, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftFoot, _Spheres[14].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightElbow, 0.0f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightElbow, _Spheres[3].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightKnee, 0.0f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightKnee, _Spheres[10].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftElbow, 0.0f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftElbow, _Spheres[6].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftKnee, 0.0f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftKnee, _Spheres[13].transform.position);
    }
}

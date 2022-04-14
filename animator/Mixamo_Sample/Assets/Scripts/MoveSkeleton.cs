using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class MoveSkeleton : MonoBehaviour
{
    public Animator MainAnimator;
    public bool EnableDisplay;
    public float _BodyRatio = 0.25f;
    public float _YOffset = 0.25f;
    public ToggleGroup _RightToggle;
    public ToggleGroup _LeftToggle;

    int _NowFrame = 0;
    int _MaxFrame = 799;
    float _AvatarLegLength = 0.0f;
    float _MidHipYAxis = 0.0f;

    int _CurrentRightToggleState = 0;
    int _CurrentLeftToggleState = 0;

    GameObject _Aim;
    ReceiveSkeleton _SkeletonReceiver;
    ReadSkeletonFromJson _SkeletonReader;
    JsonElement _Skeletons;

    List<GameObject> _Spheres = new List<GameObject>(new GameObject[25]);

    // Start is called before the first frame update
    async void Start()
    {
        Debug.Log("Start Move Skeletons : " + EnableDisplay);
        MainAnimator = GetComponent<Animator>();
        _SkeletonReader = new ReadSkeletonFromJson();
        _SkeletonReceiver = new ReceiveSkeleton("127.0.0.1", 50002);
        _SkeletonReceiver.Initialize();
        _SkeletonReceiver.SetMessageCallback(new CallbackMessage(ReceiveMessageHandler));
        _AvatarLegLength = GetAvatarLegLength();
        InitializeGameObject();
        _MidHipYAxis = GameObject.Find("mixamorig:Hips").transform.position.y + _YOffset;
        SetObjectRendering(EnableDisplay);
    }

    float GetAvatarLegLength() {
        // Vector3 UpLegPose = GameObject.Find("mixamorig:LeftUpLeg").transform.position;
        // Vector3 LegPose = GameObject.Find("mixamorig:LeftLeg").transform.position;
        // return Vector3.Distance(UpLegPose, LegPose);
        Vector3 ForeArmPose = GameObject.Find("mixamorig:LeftForeArm").transform.position;
        Vector3 HandPose = GameObject.Find("mixamorig:LeftHand").transform.position;
        return Vector3.Distance(ForeArmPose, HandPose);
    }

    void InitializeGameObject() {
        _Aim = GameObject.Find("HeadTarget");
        //_Stick = GameObject.Find("Stick");
        //_LeftHandMiddle1 = GameObject.Find("mixamorig:LeftHandMiddle1");
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
    }

    void SetObjectRendering(bool enable_flag) {
        if (enable_flag == false) {
            _Aim.SetActive(false);
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

        UpdateLeftHandAnimation();
        UpdateRightHandAnimation();

        if (Input.GetKey(KeyCode.RightArrow)) {
            if (_NowFrame <= _MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
                _NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (_NowFrame > 0) {
                _NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(skeletons);
            }
        }
    }

    void UpdateRightHandAnimation() {
        int TmpRightToggleState = 0;

        foreach( Toggle toggle in _RightToggle.ActiveToggles() ) {
            if (toggle.gameObject.name == "RightHandIdleToggle") {
                TmpRightToggleState = 0;
            } else if (toggle.gameObject.name == "RightHandFistToggle") {
                TmpRightToggleState = 1;
            } else if (toggle.gameObject.name == "RightHandPointingToggle") {
                TmpRightToggleState = 2;
            } else {
                TmpRightToggleState = 0;
            }
        }

        if (_CurrentRightToggleState != TmpRightToggleState) {
            _CurrentRightToggleState = TmpRightToggleState;
            if (_CurrentRightToggleState == 0) {
                MainAnimator.SetBool("IsRightIdle", true);
                MainAnimator.SetBool("IsRightFist", false);
                MainAnimator.SetBool("IsRightPointing", false);
                Debug.Log("RightHandIdleToggle");
            } else if (_CurrentRightToggleState == 1) {
                MainAnimator.SetBool("IsRightIdle", false);
                MainAnimator.SetBool("IsRightFist", true);
                MainAnimator.SetBool("IsRightPointing", false);
                Debug.Log("RightHandFistToggle");
            } else if (_CurrentRightToggleState == 2) {
                MainAnimator.SetBool("IsRightIdle", false);
                MainAnimator.SetBool("IsRightFist", false);
                MainAnimator.SetBool("IsRightPointing", true);
                Debug.Log("RightHandPointingToggle");
            } else {
                MainAnimator.SetBool("IsRightIdle", true);
            }
        }
    }

    void UpdateLeftHandAnimation() {
        int TmpLeftToggleState = 0;

        foreach( Toggle toggle in _LeftToggle.ActiveToggles() ) {
            if (toggle.gameObject.name == "LeftHandIdleToggle") {
                TmpLeftToggleState = 0;
            } else if (toggle.gameObject.name == "LeftHandFistToggle") {
                TmpLeftToggleState = 1;
            } else if (toggle.gameObject.name == "LeftHandPointingToggle") {
                TmpLeftToggleState = 2;
            } else {
                TmpLeftToggleState = 0;
            }
        }

        if (_CurrentLeftToggleState != TmpLeftToggleState) {
            _CurrentLeftToggleState = TmpLeftToggleState;
            if (_CurrentLeftToggleState == 0) {
                MainAnimator.SetBool("IsLeftIdle", true);
                MainAnimator.SetBool("IsLeftFist", false);
                MainAnimator.SetBool("IsLeftPointing", false);
                Debug.Log("LeftHandIdleToggle");
            } else if (_CurrentLeftToggleState == 1) {
                MainAnimator.SetBool("IsLeftIdle", false);
                MainAnimator.SetBool("IsLeftFist", true);
                MainAnimator.SetBool("IsLeftPointing", false);
                Debug.Log("LeftHandFistToggle");
            } else if (_CurrentLeftToggleState == 2) {
                MainAnimator.SetBool("IsLeftIdle", false);
                MainAnimator.SetBool("IsLeftFist", false);
                MainAnimator.SetBool("IsLeftPointing", true);
                Debug.Log("LeftHandPointingToggle");
            } else {
                MainAnimator.SetBool("IsLeftIdle", true);
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
        SetHeadAim(head_pose, nose_pose);
    }

    void UpdateSpherePosition(JsonElement skeletons){
        for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
            Vector3 pos = new Vector3((float)skeletons.keypoints3d[i][0], (float)skeletons.keypoints3d[i][2], (float)skeletons.keypoints3d[i][1]);
            _Spheres[i].transform.position = pos * _BodyRatio;
        }
    }

    float GetBodyRatio(JsonElement skeletons) {
        // Vector3 UpLegPose = new Vector3((float)skeletons.keypoints3d[12][0], (float)skeletons.keypoints3d[12][2], (float)skeletons.keypoints3d[12][1]);
        // Vector3 LegPose = new Vector3((float)skeletons.keypoints3d[13][0], (float)skeletons.keypoints3d[13][2], (float)skeletons.keypoints3d[13][1]);
        // float SkeletonLegLength = Vector3.Distance(UpLegPose, LegPose);

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
        _Aim.transform.position = nose_pose + 3 * direction;
    }

    void ChangeAvatarRotation(Vector3 right_hip_pose, Vector3 left_hip_pose) {
        Vector3 body_axis = Vector3.Scale(right_hip_pose - left_hip_pose, new Vector3(1.0f, 0.0f, 1.0f));
        Vector3 z_axis = new Vector3(1.0f, 0.0f, 0.0f);
        float rotation_angle = Vector3.SignedAngle(body_axis, z_axis, new Vector3(0.0f, 1.0f, 0.0f));
        //Debug.Log("Right Hip : " + right_hip_pose + ", Left Hip : " + left_hip_pose + ", Angle : " + -rotation_angle);
        Debug.Log("Angle : " + -rotation_angle);
        transform.rotation = Quaternion.Euler(new Vector3(0, -rotation_angle, 0));
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

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightElbow, 0.2f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightElbow, _Spheres[3].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightKnee, 0.2f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightKnee, _Spheres[10].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftElbow, 0.2f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftElbow, _Spheres[6].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftKnee, 0.2f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftKnee, _Spheres[13].transform.position);
    }
}

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class MoveSkeleton : MonoBehaviour
{
    public Animator MainAnimator;
    public int AvatarId = 0;

    public List<GameObject> _Skeleton = new List<GameObject>(new GameObject[24]);
    public List<GameObject> _Spheres = new List<GameObject>(new GameObject[25]);

    public List<Quaternion> _DifferentRotation = new List<Quaternion>(new Quaternion[24]);
    public List<Quaternion> _InverseRotation = new List<Quaternion>(new Quaternion[24]);

    public List<GameObject> _Gum = new List<GameObject>(new GameObject[2]);
    public List<GameObject> _Hansum = new List<GameObject>(new GameObject[2]);

    public List<double> _LeftRotation = new List<double>(new double[3]);
    public List<double> _RightRotation = new List<double>(new double[3]);

    public GameObject _HeadTarget;
    public GameObject _Avatar;

    public List<GameObject> _Collider = new List<GameObject>(new GameObject[6]);

    public int _HandStatus = -1;
    public bool _HandRotation = false;
    //public float HandLength = 0.0f;

    string _JsonPath = "/plask/";

    // Start is called before the first frame update
    async void Start()
    {
        MainAnimator = GetComponent<Animator>();
        MainAnimator.SetBool("IsRightIdle", true);
        InitializeGameObject();
        Debug.Log("Json Path : " + Application.persistentDataPath + _JsonPath);
    }

    string GetKeywordFromId(int id) {
        string keyword = "Bip001 ";
        return keyword;
    }

    void InitializeGameObject() {
        GameObject Avatar = GameObject.Find("CH_0" + Convert.ToString(AvatarId));
        _Avatar = Avatar;
        string keyword = GetKeywordFromId(AvatarId);

        Debug.Log("Keyword : " + keyword);
        if (keyword == "Bip001 ") {
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
        } else {
            _Skeleton[0] = Avatar.transform.Find(keyword + "Hips").gameObject;
            _Skeleton[1] = _Skeleton[0].transform.Find(keyword + "LeftUpLeg").gameObject;
            _Skeleton[2] = _Skeleton[0].transform.Find(keyword + "RightUpLeg").gameObject;
            _Skeleton[3] = _Skeleton[0].transform.Find(keyword + "Spine").gameObject;
            _Skeleton[4] = _Skeleton[1].transform.Find(keyword + "LeftLeg").gameObject;
            _Skeleton[5] = _Skeleton[2].transform.Find(keyword + "RightLeg").gameObject;
            _Skeleton[6] = _Skeleton[3].transform.Find(keyword + "Spine1").gameObject;
            _Skeleton[7] = _Skeleton[4].transform.Find(keyword + "LeftFoot").gameObject;
            _Skeleton[8] = _Skeleton[5].transform.Find(keyword + "RightFoot").gameObject;
            _Skeleton[9] = _Skeleton[6].transform.Find(keyword + "Spine2").gameObject;
            _Skeleton[10] = _Skeleton[7].transform.Find(keyword + "LeftToeBase").gameObject;
            _Skeleton[11] = _Skeleton[8].transform.Find(keyword + "RightToeBase").gameObject;
            _Skeleton[12] = _Skeleton[9].transform.Find(keyword + "Neck").gameObject;
            _Skeleton[13] = _Skeleton[9].transform.Find(keyword + "LeftShoulder").gameObject;
            _Skeleton[14] = _Skeleton[9].transform.Find(keyword + "RightShoulder").gameObject;
            _Skeleton[15] = _Skeleton[12].transform.Find(keyword + "Head").gameObject;
            _Skeleton[16] = _Skeleton[13].transform.Find(keyword + "LeftArm").gameObject;
            _Skeleton[17] = _Skeleton[14].transform.Find(keyword + "RightArm").gameObject;
            _Skeleton[18] = _Skeleton[16].transform.Find(keyword + "LeftForeArm").gameObject;
            _Skeleton[19] = _Skeleton[17].transform.Find(keyword + "RightForeArm").gameObject;
            _Skeleton[20] = _Skeleton[18].transform.Find(keyword + "LeftHand").gameObject;
            _Skeleton[21] = _Skeleton[19].transform.Find(keyword + "RightHand").gameObject;
            _Skeleton[22] = _Skeleton[20].transform.Find(keyword + "LeftHandIndex1").gameObject;
            _Skeleton[23] = _Skeleton[21].transform.Find(keyword + "RightHandIndex1").gameObject;
        }


        // for (int i = 0; i < 24; i++) {
        //     Debug.Log("Avatar Rotation " + i + " : " + _Skeleton[i].transform.localRotation);
        //     _InverseRotation[i] = new Quaternion(_Skeleton[i].transform.localRotation.x,
        //     _Skeleton[i].transform.localRotation.y,
        //     _Skeleton[i].transform.localRotation.z,
        //     _Skeleton[i].transform.localRotation.w);
        //     _InverseRotation[i] = Quaternion.Inverse(_InverseRotation[i]);
        // }

        GameObject Sphere = GameObject.Find("Sphere" + Convert.ToString(AvatarId));
        _Spheres[0] = Sphere.transform.Find("sphere_nose").gameObject;
        _Spheres[1] = Sphere.transform.Find("sphere_neck").gameObject;
        _Spheres[2] = Sphere.transform.Find("sphere_right_shoulder").gameObject;
        _Spheres[3] = Sphere.transform.Find("sphere_right_elbow").gameObject;
        _Spheres[4] = Sphere.transform.Find("sphere_right_wrist").gameObject;
        _Spheres[5] = Sphere.transform.Find("sphere_left_shoulder").gameObject;
        _Spheres[6] = Sphere.transform.Find("sphere_left_elbow").gameObject;
        _Spheres[7] = Sphere.transform.Find("sphere_left_wrist").gameObject;
        _Spheres[8] = Sphere.transform.Find("sphere_mid_hip").gameObject;
        _Spheres[9] = Sphere.transform.Find("sphere_right_hip").gameObject;
        _Spheres[10] = Sphere.transform.Find("sphere_right_knee").gameObject;
        _Spheres[11] = Sphere.transform.Find("sphere_right_ankle").gameObject;
        _Spheres[12] = Sphere.transform.Find("sphere_left_hip").gameObject;
        _Spheres[13] = Sphere.transform.Find("sphere_left_knee").gameObject;
        _Spheres[14] = Sphere.transform.Find("sphere_left_ankle").gameObject;
        _Spheres[15] = Sphere.transform.Find("sphere_right_eye").gameObject;
        _Spheres[16] = Sphere.transform.Find("sphere_left_eye").gameObject;
        _Spheres[17] = Sphere.transform.Find("sphere_right_ear").gameObject;
        _Spheres[18] = Sphere.transform.Find("sphere_left_ear").gameObject;
        _Spheres[19] = Sphere.transform.Find("sphere_left_big_toe").gameObject;
        _Spheres[20] = Sphere.transform.Find("sphere_left_small_toe").gameObject;
        _Spheres[21] = Sphere.transform.Find("sphere_left_heel").gameObject;
        _Spheres[22] = Sphere.transform.Find("sphere_right_big_toe").gameObject;
        _Spheres[23] = Sphere.transform.Find("sphere_right_small_toe").gameObject;
        _Spheres[24] = Sphere.transform.Find("sphere_right_heel").gameObject;
    }

    void OnAnimatorIK(int layerIndex) {
        MainAnimator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.RightHand, _Spheres[4].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.RightFoot, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.RightFoot, _Spheres[11].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftHand, _Spheres[7].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftFoot, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftFoot, _Spheres[14].transform.position);

        if (_HandRotation == true) {
            MainAnimator.SetIKRotationWeight(AvatarIKGoal.LeftHand, 0.8f);
            if (_LeftRotation.Count == 3) {
                MainAnimator.SetIKRotation(AvatarIKGoal.LeftHand, _Avatar.transform.rotation * Quaternion.Euler((float)_LeftRotation[0], (float)_LeftRotation[1], (float)_LeftRotation[2]));
            }

            MainAnimator.SetIKRotationWeight(AvatarIKGoal.RightHand, 0.8f);
            if (_RightRotation.Count == 3) {
                MainAnimator.SetIKRotation(AvatarIKGoal.RightHand, _Avatar.transform.rotation * Quaternion.Euler((float)_RightRotation[0], (float)_RightRotation[1], (float)_RightRotation[2]));
            }
        }

        // MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightElbow, 0.1f);
        // MainAnimator.SetIKHintPosition(AvatarIKHint.RightElbow, _Spheres[3].transform.position);

        // MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftElbow, 0.1f);
        // MainAnimator.SetIKHintPosition(AvatarIKHint.LeftElbow, _Spheres[6].transform.position);

        // MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightKnee, 0.8f);
        // MainAnimator.SetIKHintPosition(AvatarIKHint.RightKnee, _Spheres[10].transform.position);

        // MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftKnee, 0.4f);
        // MainAnimator.SetIKHintPosition(AvatarIKHint.LeftKnee, _Spheres[13].transform.position);
    }
}

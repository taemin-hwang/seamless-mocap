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

    List<Quaternion> _DifferentRotation = new List<Quaternion>(new Quaternion[24]);
    List<Quaternion> _InverseRotation = new List<Quaternion>(new Quaternion[24]);

    string _JsonPath = "/plask/";

    // Start is called before the first frame update
    async void Start()
    {
        MainAnimator = GetComponent<Animator>();
        InitializeGameObject();
        Debug.Log("Json Path : " + Application.persistentDataPath + _JsonPath);
    }

    string GetKeywordFromId(int id) {
        string keyword = "mixamorig";
        if (id == 1) {
            keyword = keyword + ":"; // mixamorig:
        } else if (id == 2) {
            keyword = keyword + "6:"; // mixamorig6:
        } else if (id == 3) {
            keyword = keyword + "1:"; // mixamorig1:
        } else {
            keyword = keyword + "0:"; // mixamorig0:
        }
        return keyword;
    }

    void InitializeGameObject() {
        GameObject Avatar = GameObject.Find("Avatar" + Convert.ToString(AvatarId));
        string keyword = GetKeywordFromId(AvatarId);

        Debug.Log("Keyword : " + keyword);
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

        for (int i = 0; i < 24; i++) {
            Debug.Log("Avatar Rotation " + i + " : " + _Skeleton[i].transform.localRotation);
            _InverseRotation[i] = new Quaternion(_Skeleton[i].transform.localRotation.x,
            _Skeleton[i].transform.localRotation.y,
            _Skeleton[i].transform.localRotation.z,
            _Skeleton[i].transform.localRotation.w);
            _InverseRotation[i] = Quaternion.Inverse(_InverseRotation[i]);
        }

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

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.RightFoot, 0.8f);
        MainAnimator.SetIKPosition(AvatarIKGoal.RightFoot, _Spheres[11].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftHand, _Spheres[7].transform.position);

        MainAnimator.SetIKPositionWeight(AvatarIKGoal.LeftFoot, 0.8f);
        MainAnimator.SetIKPosition(AvatarIKGoal.LeftFoot, _Spheres[14].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightElbow, 0.8f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightElbow, _Spheres[3].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.RightKnee, 0.8f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.RightKnee, _Spheres[10].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftElbow, 0.4f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftElbow, _Spheres[6].transform.position);

        MainAnimator.SetIKHintPositionWeight(AvatarIKHint.LeftKnee, 0.4f);
        MainAnimator.SetIKHintPosition(AvatarIKHint.LeftKnee, _Spheres[13].transform.position);
    }
}

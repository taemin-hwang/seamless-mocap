using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveCharacters : MonoBehaviour
{
    ReceiveSkeleton _SkeletonReceiver;
    public GameObject Avatar1;
    public GameObject Avatar2;
    public GameObject Avatar3;
    //public GameObject Avatar4;

    public float Ratio1 = 0.5f;
    public float Ratio2 = 0.7f;
    public float Ratio3 = 0.5f;

    public float _YOffset = -0.25f;

    private MoveSkeleton _MoveSkeleton1;
    private MoveSkeleton _MoveSkeleton2;
    private MoveSkeleton _MoveSkeleton3;
    // private MoveSkeleton _MoveSkeleton1;

    private PeopleKeypoints _PeopleKeypoints = null;
    ReadSkeletonFromJson _SkeletonReader;

    int _NowFrame = 0;
    int _MaxFrame = 799;
    float _MidHipYAxis = 0.0f;

    // Start is called before the first frame update
    void Start()
    {
        _SkeletonReceiver = new ReceiveSkeleton("192.168.0.13", 50002);
        _SkeletonReceiver.Initialize();
        _SkeletonReceiver.SetMessageCallback(new CallbackMessage(ReceiveMessageHandler));

        _SkeletonReader = new ReadSkeletonFromJson();

        Initialize();
    }

    void Initialize() {
        _MoveSkeleton1 = Avatar1.GetComponent<MoveSkeleton>();
        _MoveSkeleton2 = Avatar2.GetComponent<MoveSkeleton>();
        _MoveSkeleton3 = Avatar3.GetComponent<MoveSkeleton>();
        //_MoveSkeleton4 = Avatar4.GetComponent<MoveSkeleton>();
        _MidHipYAxis = _MoveSkeleton1._Skeleton[0].transform.position.y + _YOffset;
    }

    // Update is called once per frame
    void Update()
    {
        if (_PeopleKeypoints != null) {
            for (int i = 0; i < _PeopleKeypoints.annots.Count; i++) {
                int id = _PeopleKeypoints.annots[i].id;
                List<List<double>> skeletons = _PeopleKeypoints.annots[i].keypoints3d;
                if (id % 4 == 0) {
                    // Update3DPose(_MoveSkeleton2, skeletons);
                } else if (id % 4 == 1) {
                    Update3DPose(_MoveSkeleton1, 1, skeletons);
                } else if (id % 4 == 2) {
                    Update3DPose(_MoveSkeleton2, 2, skeletons);
                } else if (id % 4 == 3) {
                    Update3DPose(_MoveSkeleton3, 3, skeletons);
                }
            }
        }

        if (Input.GetKey(KeyCode.RightArrow)) {
            if (_NowFrame <= _MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(_MoveSkeleton3, 3, skeletons.keypoints3d);
                _NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (_NowFrame > 0) {
                _NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                Update3DPose(_MoveSkeleton3, 3, skeletons.keypoints3d);
            }
        }
    }

   void Update3DPose(MoveSkeleton avatar, int person_id, List<List<double>> keypoints3d) {
        // sphere
        UpdateSpherePosition(avatar, person_id, keypoints3d);

        // position
        ChangeAvatarPosition(avatar, avatar._Spheres[8].transform.position);

        // rotation
        Vector3 right_hip_pose = avatar._Spheres[9].transform.position;
        Vector3 left_hip_pose = avatar._Spheres[12].transform.position;
        ChangeAvatarRotation(avatar, right_hip_pose, left_hip_pose);

        // aim
        Vector3 head_pose = (avatar._Spheres[17].transform.position + avatar._Spheres[18].transform.position) * 0.5f;
        Vector3 nose_pose = avatar._Spheres[0].transform.position;
        SetHeadAim(head_pose, nose_pose);

        // send position and rotation
        UpdatePositionAndRotation(avatar);
    }

    void UpdatePositionAndRotation(MoveSkeleton avatar) {
        Debug.Log("HipPosition : " + avatar._Skeleton[0].transform.position);
        // _HipPosition = new Vector3(avatar._Skeleton[0].transform.position.x, avatar._Skeleton[0].transform.position.y, avatar._Skeleton[0].transform.position.z);
        for (int i = 0; i < 24; i++) {
            Quaternion CurrentRotation = new Quaternion(0f, 0f, 0f, 0f);
            if (i == 0) {
                CurrentRotation = new Quaternion(avatar._Skeleton[i].transform.rotation.x,
                    avatar._Skeleton[i].transform.rotation.y,
                    avatar._Skeleton[i].transform.rotation.z,
                    avatar._Skeleton[i].transform.rotation.w);
            } else {
                CurrentRotation = new Quaternion(avatar._Skeleton[i].transform.localRotation.x,
                    avatar._Skeleton[i].transform.localRotation.y,
                    avatar._Skeleton[i].transform.localRotation.z,
                    avatar._Skeleton[i].transform.localRotation.w);
            }

            // _DifferentRotation[i] = CurrentRotation * _InverseRotation[i];
            // Debug.Log("Rotation " + i + " : " + _DifferentRotation[i]);
        }

        // _RotationSender.SaveJsonStringFromRotation(Application.persistentDataPath + _JsonPath, 0, _HipPosition, _DifferentRotation);
    }

    void UpdateSpherePosition(MoveSkeleton avatar, int person_id, List<List<double>> keypoints3d){
        float ratio = 1.0f;
        if (person_id == 1) {
            ratio = Ratio1;
        } else if (person_id == 2) {
            ratio = Ratio2;
        } else if (person_id == 3) {
            ratio = Ratio3;
        }

        for (int i = 0; i < keypoints3d.Count; i++) {
            avatar._Spheres[i].transform.position = new Vector3((float)keypoints3d[i][0], (float)keypoints3d[i][2], (float)keypoints3d[i][1]) * ratio;
            // _Show[i].transform.position = new Vector3((float)keypoints3d[i][0]+0.7f, (float)keypoints3d[i][2], (float)keypoints3d[i][1]+0.7f) * _BodyRatio;
        }
    }

    void ChangeAvatarPosition(MoveSkeleton avatar, Vector3 hip_pose) {
        avatar.transform.position = new Vector3(hip_pose.x, hip_pose.y-_MidHipYAxis, hip_pose.z);
    }

    void SetHeadAim(Vector3 head_pose, Vector3 nose_pose) {
        Vector3 direction = Vector3.Scale(nose_pose - head_pose, new Vector3(1.0f, 0.0f, 1.0f));
        // _Aim.transform.position = nose_pose + 3 * direction;
    }

    void ChangeAvatarRotation(MoveSkeleton avatar, Vector3 right_hip_pose, Vector3 left_hip_pose) {
        Vector3 body_axis = Vector3.Scale(right_hip_pose - left_hip_pose, new Vector3(1.0f, 0.0f, 1.0f));
        Vector3 z_axis = new Vector3(1.0f, 0.0f, 0.0f);
        float rotation_angle = Vector3.SignedAngle(body_axis, z_axis, new Vector3(0.0f, 1.0f, 0.0f));
        Debug.Log("Angle : " + -rotation_angle);
        avatar.transform.rotation = Quaternion.Euler(new Vector3(0, -rotation_angle, 0));
    }

    void ReceiveMessageHandler(PeopleKeypoints people_keypoints) {
        _PeopleKeypoints = people_keypoints;
    }
}

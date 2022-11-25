using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Client : MonoBehaviour
{
    ReceiveSkeleton _SkeletonReceiver;
    public int PeopleNum = 4;
    public int Visible = 0;
    public bool Copyable = false;
    public bool HandRotation = false;
    public float Distance = 1.5f;
    public int Mode = 0;
    public float HandLength = 0.0f;
    public float Rotation = 0.0f;

    public List<GameObject> Avatar = new List<GameObject>(new GameObject[4]);
    public List<float> Ratio = new List<float>(new float[4]);
    public List<float> _YOffset = new List<float>(new float[4]);
    public List<MoveSkeleton> _MoveSkeleton = new List<MoveSkeleton>(new MoveSkeleton[4]);

    private PeopleKeypoints _PeopleKeypoints = null;
    ReadSkeletonFromJson _SkeletonReader;

    private int _Visible = -1;
    private bool _Copyable = false;
    private int _Mode = -1;
    private bool _IsUpdated = false;
    private bool _HandRotation = false;

    int _NowFrame = 0;
    int _MaxFrame = 799;
    List<float> _MidhipHight = new List<float>(new float[4]);
    List<Vector3> _HipPosition = new List<Vector3>(new Vector3[4]);

    string _JsonPath = "/plask/";

    void Awake() {
        Application.targetFrameRate = 20;
    }

    // Start is called before the first frame update
    void Start()
    {
        // SkeletonReceiver
        _SkeletonReceiver = new ReceiveSkeleton();

        // SkeletonReader
        _SkeletonReader = new ReadSkeletonFromJson();

        // Set Renderer
        for (int i = 0; i < 4 - PeopleNum; i++) {
            Avatar[PeopleNum + i].SetActive(false);
        }

        Initialize();
    }

    void Initialize() {
        for (int i = 0; i < 4; i++) {
            _MoveSkeleton[i] = Avatar[i].GetComponent<MoveSkeleton>();
            _MidhipHight[i] = _MoveSkeleton[i]._Skeleton[0].transform.position.y + _YOffset[i];
            //_MoveSkeleton[i].HandLength = HandLength;
        }
        Debug.Log("Json Path : " + Application.persistentDataPath + _JsonPath);

        _Mode = -1;
        _Visible = -1;
        UpdateMode();
        // InvokeRepeating("DisableClothCollider", 0.0f, 5f);
        // InvokeRepeating("EnableClothCollider", 0.3f, 5f);
    }

    // Update is called once per frame
    void Update()
    {
        UpdateMode();

        if (_PeopleKeypoints != null && _IsUpdated == true) {
            _IsUpdated = false;
            for (int i = 0; i < _PeopleKeypoints.annots.Count; i++) {
                int id = _PeopleKeypoints.annots[i].id;
                List<List<double>> skeletons = _PeopleKeypoints.annots[i].keypoints3d;
                if (id % 4 == 0) {
                    // UpdateWithoutCopyMode(_MoveSkeleton[0], 0, skeletons, 0);
                    Update3DPose(PeopleNum, _MoveSkeleton[0], 0, skeletons);
                } else if (id % 4 == 1) {
                    // UpdateWithoutCopyMode(_MoveSkeleton[1], 1, skeletons, 0);
                    Update3DPose(PeopleNum, _MoveSkeleton[1], 1, skeletons);
                } else if (id % 4 == 2) {
                    // UpdateWithoutCopyMode(_MoveSkeleton[2], 2, skeletons, 0);
                    Update3DPose(PeopleNum, _MoveSkeleton[2], 2, skeletons);
                } else if (id % 4 == 3) {
                    // UpdateWithoutCopyMode(_MoveSkeleton[3], 3, skeletons, 0);
                    Update3DPose(PeopleNum, _MoveSkeleton[3], 3, skeletons);
                }
            }
            if ( _PeopleKeypoints.annots.Count > 0) {
                int hand = _PeopleKeypoints.annots[0].hand;
                List<double> left_rotation = _PeopleKeypoints.annots[0].left_rotation;
                List<double> right_rotation = _PeopleKeypoints.annots[0].right_rotation;
                for (int i = 0; i < 4; i++) {
                    if (HandRotation == false) {
                        if (HandRotation != _MoveSkeleton[i]._HandRotation) {
                            _MoveSkeleton[i]._HandRotation = false;
                            _Mode = -1;
                        }
                    } else {
                        _MoveSkeleton[i]._HandRotation = true;
                        UpdateHandRotation(_MoveSkeleton[i], left_rotation, right_rotation);
                        UpdateHandPose(_MoveSkeleton[i], i, hand);
                    }
                }
            }
        }

        if (Input.GetKey(KeyCode.RightArrow)) {
            if (_NowFrame <= _MaxFrame) {
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
                    skeletons.keypoints3d[i][0] *= 1.0f;
                    skeletons.keypoints3d[i][1] *= 1.0f;
                    skeletons.keypoints3d[i][2] *= 1.0f;
                }
                Update3DPose(PeopleNum, _MoveSkeleton[0], 0, skeletons.keypoints3d);
                _NowFrame++;
            }
        }
        if (Input.GetKey(KeyCode.LeftArrow)) {
            if (_NowFrame > 0) {
                _NowFrame--;
                string file_name = Application.dataPath + "/Data/keypoints3d/" + _NowFrame.ToString("D6") + ".json";
                var skeletons = _SkeletonReader.Get3DSkeletonFromJson(file_name);
                for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
                    skeletons.keypoints3d[i][0] *= 1.0f;
                    skeletons.keypoints3d[i][1] *= 1.0f;
                    skeletons.keypoints3d[i][2] *= 1.0f;
                }
                Update3DPose(PeopleNum, _MoveSkeleton[0], 0, skeletons.keypoints3d);
            }
        }
    }

    public void SendWebsocketData(string websocketData) {
        PeopleKeypoints JsonData = _SkeletonReceiver.Get3DSkeletonFromWebsocket(websocketData);
        ReceiveMessageHandler(JsonData);
    }

    void Update3DPose(int person_num, MoveSkeleton avatar, int person_id, List<List<double>> skeletons) {
        if (_Copyable == true) {
            UpdateWithCopyMode(person_num, avatar, person_id, skeletons);
        }
        else {
            UpdateWithoutCopyMode(avatar, person_id, skeletons, 0);
        }
    }

    void UpdateWithCopyMode(int person_num, MoveSkeleton avatar, int person_id, List<List<double>> skeletons) {
        if (person_num == 1) {
            UpdateWithoutCopyMode(_MoveSkeleton[0], 0, skeletons, 0);
            for (int i = 0; i < skeletons.Count; i++) {
                skeletons[i][0] -= 1.0f * Distance;
                skeletons[i][1] += 1.0f * Distance;
            }
            UpdateWithoutCopyMode(_MoveSkeleton[1], 1, skeletons, 0);
            for (int i = 0; i < skeletons.Count; i++) {
                skeletons[i][1] -= 2.0f * Distance;
            }
            UpdateWithoutCopyMode(_MoveSkeleton[2], 2, skeletons, 0);
            for (int i = 0; i < skeletons.Count; i++) {
                skeletons[i][1] += 1.0f * Distance;
                skeletons[i][0] -= 1.0f * Distance;
            }
            UpdateWithoutCopyMode(_MoveSkeleton[3], 3, skeletons, 0);
        } else if (person_num == 2) {
            if (person_id == 0) {
                UpdateWithoutCopyMode(_MoveSkeleton[0], 0, skeletons, 0);
                for (int i = 0; i < skeletons.Count; i++) {
                    skeletons[i][0] -= 1.0f * Distance;
                    skeletons[i][1] += 1.0f * Distance;
                }
                UpdateWithoutCopyMode(_MoveSkeleton[2], 2, skeletons, 0);
            } else if (person_id == 1) {
                UpdateWithoutCopyMode(_MoveSkeleton[1], 1, skeletons, 0);
                for (int i = 0; i < skeletons.Count; i++) {
                    skeletons[i][0] -= 1.0f * Distance;
                    skeletons[i][1] += 1.0f * Distance;
                }
                UpdateWithoutCopyMode(_MoveSkeleton[3], 3, skeletons, 0);
            }
        } else {
            // do noting
        }
    }

    void UpdateWithoutCopyMode(MoveSkeleton avatar, int person_id, List<List<double>> keypoints3d, float angle) {
        Debug.Log("UpdateWithoutCopyMode");
        // sphere
        UpdateSpherePosition(avatar, person_id, keypoints3d, angle);

        // position
        ChangeAvatarPosition(avatar, person_id, avatar._Spheres[8].transform.position);

        // rotation
        Vector3 right_hip_pose = avatar._Spheres[9].transform.position;
        Vector3 left_hip_pose = avatar._Spheres[12].transform.position;
        ChangeAvatarRotation(avatar, right_hip_pose, left_hip_pose);

        // aim
        Vector3 head_pose = (avatar._Spheres[2].transform.position + avatar._Spheres[5].transform.position) * 0.5f;
        Vector3 nose_pose = avatar._Spheres[0].transform.position;
        SetHeadAim(avatar, head_pose, nose_pose);

        // send position and rotation
        // UpdatePositionAndRotation(avatar, person_id);
    }

    void UpdateHandRotation(MoveSkeleton avatar, List<double> left_rotation, List<double> right_rotation) {
        avatar._LeftRotation = left_rotation;
        avatar._RightRotation = right_rotation;
    }

    void DisableClothCollider() {
        Debug.Log("DisableClothCollider");
        for (int i = 0; i < 4; i++) {
            if (Avatar[i].activeSelf == false) {
                continue;
            }
            for (int j = 0; j < 6; j++) {
                Avatar[i].GetComponent<MoveSkeleton>()._Collider[j].SetActive(false);
            }
        }
    }

    void EnableClothCollider() {
        Debug.Log("EnableClothCollider");
        for (int i = 0; i < 4; i++) {
            if (Avatar[i].activeSelf == false) {
                continue;
            }
            for (int j = 0; j < 6; j++) {
                Avatar[i].GetComponent<MoveSkeleton>()._Collider[j].SetActive(true);
            }
        }
    }

    void UpdateMode() {
        //for (int i = 0; i < 4; i++) {
        //    _MoveSkeleton[i] = Avatar[i].GetComponent<MoveSkeleton>();
        //    //_MoveSkeleton[i].HandLength = HandLength;
        //}
        if ((_Copyable != Copyable) || (_Mode != Mode) || (_Visible != Visible)) {
            // UpdateHandPose(_MoveSkeleton[0], 0, 1);

            Debug.Log("Update Copyable : " + Copyable);
            _Copyable = Copyable;
            if (Copyable == true) {
                for (int i = 0; i < 4; i++) {
                    Avatar[i].SetActive(true);
                }
            } else {
                for (int i = 0; i < 4 - PeopleNum; i++) {
                    Avatar[PeopleNum + i].SetActive(false);
                }
            }

            _Mode = Mode;
            Debug.Log("Update Mode : " + Mode);
            for (int i = 0; i < 4; i++) {
                if (Avatar[i].activeSelf == false) {
                    continue;
                }
                // Disable Gum and Hansum
                for (int j = 0; j < 2; j++) {
                    if (Mode == 0) {
                        Avatar[i].GetComponent<MoveSkeleton>()._Gum[j].SetActive(false);
                        Avatar[i].GetComponent<MoveSkeleton>()._Hansum[j].SetActive(false);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 0);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 3);
                    } else if (Mode == 1) {
                        Avatar[i].GetComponent<MoveSkeleton>()._Gum[j].SetActive(true);
                        Avatar[i].GetComponent<MoveSkeleton>()._Hansum[j].SetActive(false);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 1);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 4);
                    } else {
                        Avatar[i].GetComponent<MoveSkeleton>()._Gum[j].SetActive(false);
                        Avatar[i].GetComponent<MoveSkeleton>()._Hansum[j].SetActive(true);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 1);
                        UpdateHandPose(Avatar[i].GetComponent<MoveSkeleton>(), i, 4);
                    }
                }
            }

            _Visible = Visible;
            Debug.Log("Update Visible : " + Visible);
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 25; j++) {
                    if (Visible == 1) {
                        Renderer rend = Avatar[i].GetComponent<MoveSkeleton>()._Spheres[j].GetComponent<Renderer>();
                        rend.enabled = true;
                    } else {
                        Renderer rend = Avatar[i].GetComponent<MoveSkeleton>()._Spheres[j].GetComponent<Renderer>();
                        rend.enabled = false;
                    }
                }
            }
        }
    }

    void UpdateHandPose(MoveSkeleton avatar, int person_id, int hand_status) {
        Debug.Log("Update Hand Pose : " + hand_status);
        if (avatar._HandStatus == hand_status) {
            return;
        }
        avatar._HandStatus = hand_status;

        if (hand_status < 3) {
            avatar.MainAnimator.SetBool("IsRightIdle", false);
            avatar.MainAnimator.SetBool("IsRightFist", false);
            avatar.MainAnimator.SetBool("IsRightPointing", false);
        } else {
            avatar.MainAnimator.SetBool("IsLeftIdle", false);
            avatar.MainAnimator.SetBool("IsLeftFist", false);
            avatar.MainAnimator.SetBool("IsLeftPointing", false);
        }

        switch (hand_status) {
            case 0:
                avatar.MainAnimator.SetBool("IsRightIdle", true);
                break;
            case 1:
                avatar.MainAnimator.SetBool("IsRightFist", true);
                break;
            case 2:
                avatar.MainAnimator.SetBool("IsRightPointing", true);
                break;
            case 3:
                avatar.MainAnimator.SetBool("IsLeftIdle", true);
                break;
            case 4:
                avatar.MainAnimator.SetBool("IsLeftFist", true);
                break;
            case 5:
                avatar.MainAnimator.SetBool("IsLeftPointing", true);
                break;
        }
    }

    void UpdatePositionAndRotation(MoveSkeleton avatar, int person_id) {
        Debug.Log("HipPosition : " + avatar._Skeleton[0].transform.position);
        _HipPosition[person_id] = new Vector3(avatar._Skeleton[0].transform.position.x, avatar._Skeleton[0].transform.position.y, avatar._Skeleton[0].transform.position.z);
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

            avatar._DifferentRotation[i] = CurrentRotation * avatar._InverseRotation[i];
            Debug.Log("Rotation " + i + " : " + avatar._DifferentRotation[i]);
        }

    }

    void UpdateSpherePosition(MoveSkeleton avatar, int person_id, List<List<double>> keypoints3d, float angle){
        Debug.Log("Start to UpdateSpherePosition : " + person_id + ", " + keypoints3d.Count);

        float ratio = 1.0f;
        ratio = Ratio[person_id];
        for (int i = 0; i < keypoints3d.Count; i++) {
            avatar._Spheres[i].transform.position = new Vector3((float)keypoints3d[i][0], (float)keypoints3d[i][2], (float)keypoints3d[i][1]) * ratio;
            Debug.Log("keypoints3d[" + i + "] : " + (float)keypoints3d[i][0] + ", " + (float)keypoints3d[i][1] + ", " + (float)keypoints3d[i][2]);
        }
        avatar._Spheres[8].transform.position = (avatar._Spheres[9].transform.position + avatar._Spheres[12].transform.position) / 2.0f;

        for (int i = 0; i < keypoints3d.Count; i++) {
            avatar._Spheres[i].transform.RotateAround(avatar._Spheres[8].transform.position, Vector3.up, angle);
        }

        Debug.Log("Finish to UpdateSpherePosition");
    }

    void ChangeAvatarPosition(MoveSkeleton avatar, int person_id, Vector3 hip_pose) {
        avatar.transform.position = new Vector3(hip_pose.x, hip_pose.y - _MidhipHight[person_id], hip_pose.z);
        // avatar.transform.position = Vector3.Lerp(avatar.transform.position, new Vector3(hip_pose.x, hip_pose.y - _MidhipHight[person_id], hip_pose.z), 2f * Time.deltaTime);
    }

    void SetHeadAim(MoveSkeleton avatar, Vector3 head_pose, Vector3 nose_pose) {
        Vector3 direction = Vector3.Scale(nose_pose - head_pose, new Vector3(1.0f, 0.0f, 1.0f));
        if (avatar._HeadTarget != null) {
            avatar._HeadTarget.transform.position = head_pose + 30 * direction;
            avatar._HeadTarget.transform.position = new Vector3(avatar._HeadTarget.transform.position.x, avatar._HeadTarget.transform.position.y + 0.05f, avatar._HeadTarget.transform.position.z);
            // avatar._HeadTarget.transform.position = nose_pose + 3 * direction;
        }
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
        _IsUpdated = true;
    }
}

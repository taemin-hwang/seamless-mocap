using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
//using System.Text;
using System.Threading;

using Newtonsoft.Json;

[System.Serializable]
public class DataElement
{
    public List<double> values = new List<double>();
    public string property { get; set; }
    public string name { get; set; }
}

[System.Serializable]
public class RotationElement
{
    public List<DataElement> data = new List<DataElement>(new DataElement[25]);
    public int id { get; set; }
    public string key { get; set; }
}

public class SendRotation
{
    int _FileNumber = 0;
    string[] DataElementName = {
    "hips",
    "hips",
    "leftUpLeg",
    "rightUpLeg",
    "spine",
    "leftLeg",
    "rightLeg",
    "spine1",
    "leftFoot",
    "rightFoot",
    "spine2",
    "leftToeBase",
    "rightToeBase",
    "neck",
    "leftShoulder",
    "rightShoulder",
    "head",
    "leftArm",
    "rightArm",
    "leftForeArm",
    "rightForeArm",
    "leftHand",
    "rightHand",
    "leftHandIndex1",
    "rightHandIndex1"
     };

    public string GetJsonStringFromRotation(int id, Vector3 Position, List<Quaternion> Rotation) {
        RotationElement RotationElement = new RotationElement();
        RotationElement.key = "plask";
        RotationElement.id = id;
        RotationElement.data[0] = new DataElement();
        RotationElement.data[0].name = DataElementName[0];
        RotationElement.data[0].property = "position";
        RotationElement.data[0].values = new List<double>(new double[] { Position.x, Position.y, Position.z });
        for (int i = 0; i < 24; i++) {
            RotationElement.data[i+1] = new DataElement();
            RotationElement.data[i+1].name = DataElementName[i+1];
            RotationElement.data[i+1].property = "quaternion";
            RotationElement.data[i+1].values = new List<double>(new double[] { Rotation[i].x, Rotation[i].y, Rotation[i].z, Rotation[i].w });
        }

        string JsonData = JsonConvert.SerializeObject(RotationElement);
        Debug.Log("JsonData : \n" + JsonData);
        return JsonData;
    }

    public void SaveJsonStringFromRotation(string Path, int id, Vector3 Position, List<Quaternion> Rotation) {
        if (Directory.Exists(Path) == false) {
            Directory.CreateDirectory(Path);
        }
        string FilePath = Path + _FileNumber.ToString("D6") + ".json";
        string JsonData = GetJsonStringFromRotation(id, Position, Rotation);

        System.IO.File.WriteAllText(FilePath, JsonData);
        _FileNumber++;
    }

}

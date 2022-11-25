using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
//using System.Text;
using System.Threading;
using Newtonsoft.Json;

[System.Serializable]
public class PersonKeypoints
{
    public int id { get; set; }
    public int hand { get; set; }
    public int face { get; set; }
    public List<List<double>> keypoints3d = new List<List<double>>();
    public List<double> left_rotation = new List<double>();
    public List<double> right_rotation = new List<double>();
}

public class PeopleKeypoints
{
    public List<PersonKeypoints> annots = new List<PersonKeypoints>();
}

public class ReceiveSkeleton
{
    public PeopleKeypoints Get3DSkeletonFromClient(byte[] data) {
        string JsonString = Encoding.UTF8.GetString(data);
        Debug.Log(JsonString);
        // JsonString = RemoveArrayFromJson(JsonString);
        var JsonData = Newtonsoft.Json.JsonConvert.DeserializeObject<PeopleKeypoints>(JsonString);
        // Debug.Log("ID : "+ JsonData.id);
        // Debug.Log("Keypoints : "+ JsonData.keypoints3d.Count);
        return JsonData;
    }

    public PeopleKeypoints Get3DSkeletonFromWebsocket(string JsonString) {
        Debug.Log("JSON STRING: \n" + JsonString);
        // JsonString = RemoveArrayFromJson(JsonString);
        var JsonData = Newtonsoft.Json.JsonConvert.DeserializeObject<PeopleKeypoints>(JsonString);
        Debug.Log("ID : "+ JsonData.annots[0].id);
        Debug.Log("Keypoints : "+ JsonData.annots[0].keypoints3d.Count);
        return JsonData;
    }
}

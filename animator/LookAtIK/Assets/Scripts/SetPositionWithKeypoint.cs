using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using Newtonsoft.Json;

// [System.Serializable]
// public class JsonElement
// {
//     public int id;
//     public List<Vector4> keypoints3d;
// }

// Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse);
[System.Serializable]
public class JsonElement
{
    public int id { get; set; }
    public List<List<double>> keypoints3d = new List<List<double>>();
}



public class SetPositionWithKeypoint : MonoBehaviour
{
    int NowFrame = 0;
    int MaxFrame = 0;

    void Start()
    {

    }

    async void Update()
    {
        if (NowFrame <= MaxFrame) {
            string file_name = Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json";
            var skeletons = Get3DSkeletonFromJson(file_name);
            // for (int i = 0; i < skeletons.keypoints3d.Count; i++) {
            //     Debug.Log("[" + i + "] : " + skeletons.keypoints3d[i][0] + ", " + skeletons.keypoints3d[i][1] + ", " + skeletons.keypoints3d[i][2] + ", " + skeletons.keypoints3d[i][3]);
            // }
            NowFrame++;
        }
    }

    JsonElement Get3DSkeletonFromJson(string path) {
        // Debug.Log(Application.dataPath + "/Data/keypoints3d/" + NowFrame.ToString("D6") + ".json");
        FileStream file_stream = new FileStream(path, FileMode.Open);
        byte[] data = new byte[file_stream.Length];
        file_stream.Read(data, 0, data.Length);
        file_stream.Close();
        string json_string = Encoding.UTF8.GetString(data);
        // Debug.Log(json_string);
        // Debug.Log("ID : "+ json_data.id);
        // Debug.Log("Keypoints : "+ json_data.keypoints3d.Count);
        json_string = RemoveArrayFromJson(json_string);
        var json_data = Newtonsoft.Json.JsonConvert.DeserializeObject<JsonElement>(json_string);
        return json_data;
    }

    string RemoveArrayFromJson(string json) {
            json = json.Substring(1, json.Length - 1);
            int index = json.LastIndexOf("]");
            json = json.Substring(0, index);
            return json;
    }
}

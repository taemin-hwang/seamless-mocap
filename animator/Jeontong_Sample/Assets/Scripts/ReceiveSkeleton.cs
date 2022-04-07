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

public delegate void CallbackMessage(JsonElement message);

public class ReceiveSkeleton
{
    public string _IpAddr = "127.0.0.1";
    public int _Port = 50001;
    CallbackMessage _CallbackMessage;


    #region private members
    private Thread ListenerThread;
    #endregion

    public ReceiveSkeleton(string IpAddr, int Port) {
        _IpAddr = IpAddr;
        _Port = Port;
    }

    public void Initialize() {
        // Start TcpServer background thread
        ListenerThread = new Thread(new ThreadStart(ListenForIncommingRequest));
        ListenerThread.IsBackground = true;
        ListenerThread.Start();

    }

    void ListenForIncommingRequest() {
        Debug.Log("Start Server : " + _IpAddr + ", " + _Port);
        UdpClient listener = new UdpClient(_Port);
        IPEndPoint groupEP = new IPEndPoint(IPAddress.Any, _Port);
        try {
            while (true){
                byte[] bytes = listener.Receive(ref groupEP);
                Debug.Log(Encoding.ASCII.GetString(bytes, 0, bytes.Length));
                var JsonData = Get3DSkeletonFromClient(bytes);
                MessageHandler(JsonData);
            }
        } catch (SocketException e) {
            Debug.Log("SocketException " + e.ToString());
        } finally {
            listener.Close();
        }
    }

    public JsonElement Get3DSkeletonFromClient(byte[] data) {
        string JsonString = Encoding.UTF8.GetString(data);
        Debug.Log(JsonString);
        JsonString = RemoveArrayFromJson(JsonString);
        var JsonData = Newtonsoft.Json.JsonConvert.DeserializeObject<JsonElement>(JsonString);
        Debug.Log("ID : "+ JsonData.id);
        Debug.Log("Keypoints : "+ JsonData.keypoints3d.Count);
        return JsonData;
    }

    public void SetMessageCallback(CallbackMessage callback)
    {
        if (_CallbackMessage == null) {
            _CallbackMessage = callback;
        } else {
            _CallbackMessage += callback;
        }
    }

    private void MessageHandler(JsonElement JsonData)
    {
        if (_CallbackMessage != null) {
            _CallbackMessage(JsonData);
        }
    }

    string RemoveArrayFromJson(string json) {
            json = json.Substring(1, json.Length - 1);
            int index = json.LastIndexOf("]");
            json = json.Substring(0, index);
            return json;
    }
}

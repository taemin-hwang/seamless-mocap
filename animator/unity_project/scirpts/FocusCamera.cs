using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

public class FocusCamera : MonoBehaviour
{
    public GameObject target;
    // public GameObject black;

    private Camera mainCamera;

    private float xRotateMove, yRotateMove;
    public float rotateSpeed = 500.0f;
    public float zoomSpeed = 10.0f;

    float offsetX = 0.0f;
    float offsetY = 1.5f;
    float offsetZ = 4.5f;
    float CameraSpeed = 10.0f;
    Vector3 CameraPose;
    Vector4 currentScreen = new Vector4(0.0f, 0.0f, 0.0f, 1.0f);
    private bool isFadeIn = true;
    Vector4 blackScreen = new Vector4(0.0f, 0.0f, 0.0f, 1.0f);
    Vector4 whiteScreen = new Vector4(0.0f, 0.0f, 0.0f, 0.0f);

    void Start(){
        mainCamera = GetComponent<Camera>();
        Vector3 target_pos = new Vector3(0.0f, 0.2f, 0.0f);
        transform.LookAt(target_pos);
        // black.SetActive(true);
        Invoke("FadeIn", 0f);
        Invoke("FadeOut", 251f);
    }

    void Update(){

        // if(isFadeIn) {
        //     currentScreen = Vector4.Lerp(currentScreen, whiteScreen, Time.deltaTime / 3);
        //     var blackRenderer = black.GetComponent<Renderer>();
        //     blackRenderer.material.SetColor("_Color", new Color(currentScreen.x, currentScreen.y, currentScreen.z, currentScreen.w));
        // } else {
        //     currentScreen = Vector4.Lerp(currentScreen, blackScreen, Time.deltaTime / 3);
        //     var blackRenderer = black.GetComponent<Renderer>();
        //     blackRenderer.material.SetColor("_Color", new Color(currentScreen.x, currentScreen.y, currentScreen.z, currentScreen.w));
        // }

        Zoom();
        if (Input.GetMouseButton(0)){
            Rotate();
        } else if (Input.GetMouseButton(2)) {
            Move();
        } else {
            Look();
        }
    }

    private void Zoom(){
        float distance = Input.GetAxis("Mouse ScrollWheel") * -1 * zoomSpeed;
        if(distance != 0) {
            mainCamera.fieldOfView += distance;
        }
    }

    private void Rotate(){
        xRotateMove = Input.GetAxis("Mouse X") * Time.deltaTime * rotateSpeed;
        // yRotateMove = Input.GetAxis("Mouse Y") * Time.deltaTime * rotateSpeed;
        // Vector3 target_pos = target.transform.position;
        Vector3 target_pos = new Vector3(target.transform.position.x, target.transform.position.y + 0.2f, target.transform.position.z);
        transform.RotateAround(target_pos, Vector3.up, xRotateMove);
        // transform.RotateAround(target_pos, Vector3.right, yRotateMove);
        transform.LookAt(target_pos);
        offsetX = transform.position.x - target.transform.position.x;
        offsetY = transform.position.y - target.transform.position.y;
        offsetZ = transform.position.z - target.transform.position.z;
    }

    private void Move() {
        float keyH = Input.GetAxis("Mouse X");
        float keyV = Input.GetAxis("Mouse Y");
        keyH = keyH * -1.0f * Time.deltaTime;
        keyV = keyV * -1.0f * Time.deltaTime;
        transform.Translate(Vector3.right * keyH);
        transform.Translate(Vector3.up * keyV);
        offsetX = transform.position.x - target.transform.position.x;
        offsetY = transform.position.y - target.transform.position.y;
        offsetZ = transform.position.z - target.transform.position.z;
    }

    private void Look() {
        CameraPose = new Vector3(
            target.transform.position.x + offsetX,
            target.transform.position.y + offsetY,
            target.transform.position.z + offsetZ
        );

        // transform.position = Vector3.Lerp(transform.position, CameraPose, Time.deltaTime * CameraSpeed);
        transform.position = CameraPose;
        Vector3 target_pos = new Vector3(target.transform.position.x, target.transform.position.y + 0.2f, target.transform.position.z);
        transform.LookAt(target_pos);
    }

    private void FadeIn() {
        isFadeIn = true;
    }

    private void FindOut() {
        isFadeIn = false;
    }
}

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveCamera : MonoBehaviour
{
    public bool EnableRotation;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (EnableRotation == true) {
            transform.RotateAround(Vector3.zero, Vector3.up, 30 * Time.deltaTime);
            transform.LookAt(Vector3.zero);
        }

    }
}

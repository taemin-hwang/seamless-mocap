using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeadAimIdle : MonoBehaviour
{

    public Vector3 minLocalTransformation;
    public Vector3 maxLocalTransformation;
    public float lerpSpeed;
    public Vector3 targetPosition;
    public Vector2Int minMaxTime = new Vector2Int(3, 7);

    private Vector3 origin;

    void Start()
    {
        //Set the origin to the starting position
        origin = transform.localPosition;
        targetPosition = transform.localPosition;

        StartCoroutine(ChangeTargetPosition());
    }

    void Update()
    {
        
        if(transform.localPosition != targetPosition)
        {
            float speed = lerpSpeed / 10; 
            //gradually move the transform to the target position
            transform.localPosition = Vector3.Lerp(transform.localPosition, targetPosition, Time.deltaTime * speed);
        }

    }

    IEnumerator ChangeTargetPosition()
    {
        //Randomise an amount of time to wait before changing the position
        yield return new WaitForSeconds(Random.Range(minMaxTime.x, minMaxTime.y));

        float x = Random.Range(minLocalTransformation.x, maxLocalTransformation.x);
        float y = Random.Range(minLocalTransformation.y, maxLocalTransformation.y);
        float z = Random.Range(minLocalTransformation.z, maxLocalTransformation.z);

        //Update the target position, by offsetting the origin point.
        targetPosition = origin + new Vector3(x, y, z);

        //Loop
        StartCoroutine(ChangeTargetPosition());
    }
}

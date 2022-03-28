using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LookAtNearby : MonoBehaviour
{
    public Transform headTransform;
    public Transform aimTargetTransform;
    public PointOfInterest pointOfInterest;

    public Vector3 origin;
    public float visionRadius;
    public float lerpSpeed;

    private void Start()
    {
        origin = aimTargetTransform.position;
    }
    // Update is called once per frame
    void Update()
    {
        Collider[] cols = Physics.OverlapSphere(headTransform.position + transform.forward, visionRadius);
        
        pointOfInterest = null;
       
        foreach (Collider col in cols) {

            if (col.GetComponent<PointOfInterest>())
            {
                pointOfInterest = col.GetComponent<PointOfInterest>();
                break;
            }
        }

        Vector3 targetPosition;
        if (pointOfInterest != null)
        {
            targetPosition = pointOfInterest.GetLookTarget().position;
        }
        else
        {
            targetPosition = origin;
        }

        float speed = lerpSpeed / 10;
        aimTargetTransform.position = Vector3.Lerp(aimTargetTransform.position, targetPosition, Time.deltaTime * speed);


    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.green * 0.5f;
        Gizmos.DrawWireSphere(headTransform.position + transform.forward, visionRadius);
    }


}

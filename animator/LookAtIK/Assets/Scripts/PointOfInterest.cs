using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PointOfInterest : MonoBehaviour
{

    public Transform lookTarget;

    public Transform GetLookTarget()
    {
        if(lookTarget != null)
        {
            return lookTarget;
        }
        else
        {
            return transform;
        }
    }
}

import cv2
import logging
import pyzed.sl as sl
from src.visualizer.utils import *

class VisualManager:
    def __init__(self):
        pass

    def show_keypoint(self, image, keypoint):
        annots = keypoint['annots']

        for person in annots:
            bbox = person['bbox']
            person_id = person['personID']
            color = generate_color_id_u(person_id)

            print(image.shape)
            print([bbox[0], bbox[1], bbox[2], bbox[3]])

            cv2.rectangle(image, [int(bbox[0]), int(bbox[1])], [int(bbox[2]), int(bbox[3])], color)

            keypoints = person['keypoints']

            if len(keypoints) == 34:
                keypoints = convert_25_from_34(np.array(keypoints))

            if len(keypoints) == 18:
                #print('keypoint format: 18')
                # Draw skeleton bones
                for part in SKELETON_BONES:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < image.shape[1] and kp_a[1] < image.shape[0]
                    and kp_b[0] < image.shape[1] and kp_b[1] < image.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(image, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 3, cv2.LINE_AA)

                # Get spine base coordinates to create backbone
                left_hip = keypoints[BODY_PARTS.LEFT_HIP.value]
                right_hip = keypoints[BODY_PARTS.RIGHT_HIP.value]
                spine = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
                kp_spine = spine
                kp_neck = keypoints[BODY_PARTS.NECK.value]

                # Check that the keypoints are inside the image
                if(kp_spine[0] < image.shape[1] and kp_spine[1] < image.shape[0]
                and kp_neck[0] < image.shape[1] and kp_neck[1] < image.shape[0]
                and kp_spine[0] > 0 and kp_spine[1] > 0 and kp_neck[0] > 0 and kp_neck[1] > 0
                and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                    cv2.line(image, (int(kp_spine[0]), int(kp_spine[1])), (int(kp_neck[0]), int(kp_neck[1])), color, 3, cv2.LINE_AA)

                # Skeleton joints for spine
                if(kp_spine[0] < image.shape[1] and kp_spine[1] < image.shape[0]
                and left_hip[0] > 0 and left_hip[1] > 0 and right_hip[0] > 0 and right_hip[1] > 0 ):
                    cv2.circle(image, (int(kp_spine[0]), int(kp_spine[1])), 6, color, -1)

            elif len(keypoints) == 25:
                #print('keypoint format: 25')
                # Draw skeleton bones
                for part in BODY_BONES_POSE_25:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < image.shape[1] and kp_a[1] < image.shape[0]
                    and kp_b[0] < image.shape[1] and kp_b[1] < image.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(image, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 5, cv2.LINE_AA)

                color_left = generate_color_id_u(person_id + 4)
                color_right = generate_color_id_u(person_id + 5)

                for part in BODY_PARTS_POSE_25:
                    if part is BODY_PARTS_POSE_25.LAST:
                        break
                    kp = keypoints[part.value]
                    cv2.circle(image, (int(kp[0]), int(kp[1])), 10, color, -1)


            elif len(keypoints) == 34:
                #print('keypoint format: 34')
                # Draw skeleton bones
                for part in BODY_BONES_POSE_34:
                    kp_a = keypoints[part[0].value]
                    kp_b = keypoints[part[1].value]
                    # Check that the keypoints are inside the image
                    if(kp_a[0] < image.shape[1] and kp_a[1] < image.shape[0]
                    and kp_b[0] < image.shape[1] and kp_b[1] < image.shape[0]
                    and kp_a[0] > 0 and kp_a[1] > 0 and kp_b[0] > 0 and kp_b[1] > 0 ):
                        cv2.line(image, (int(kp_a[0]), int(kp_a[1])), (int(kp_b[0]), int(kp_b[1])), color, 1, cv2.LINE_AA)

                color_left = generate_color_id_u(person_id + 4)
                color_right = generate_color_id_u(person_id + 5)

                for part in BODY_PARTS_POSE_34:
                    kp = keypoints[part.value]
                    # Check that the keypoints are inside the image
                    if(kp[0] < image.shape[1] and kp[1] < image.shape[0]):
                        if (part == BODY_PARTS_POSE_34.LEFT_CLAVICLE or
                                part == BODY_PARTS_POSE_34.LEFT_SHOULDER or
                                part == BODY_PARTS_POSE_34.LEFT_ELBOW or
                                part == BODY_PARTS_POSE_34.LEFT_WRIST or
                                part == BODY_PARTS_POSE_34.LEFT_HAND or
                                part == BODY_PARTS_POSE_34.LEFT_HANDTIP or
                                part == BODY_PARTS_POSE_34.LEFT_THUMB or
                                part == BODY_PARTS_POSE_34.LEFT_HIP or
                                part == BODY_PARTS_POSE_34.LEFT_KNEE or
                                part == BODY_PARTS_POSE_34.LEFT_ANKLE or
                                part == BODY_PARTS_POSE_34.LEFT_FOOT or
                                part == BODY_PARTS_POSE_34.LEFT_HEEL or
                                part == BODY_PARTS_POSE_34.LEFT_EYE or
                                part == BODY_PARTS_POSE_34.LEFT_EAR):
                            cv2.circle(image, (int(kp[0]), int(kp[1])), 3, color_left, -1)
                        elif (part == BODY_PARTS_POSE_34.RIGHT_CLAVICLE or
                                part == BODY_PARTS_POSE_34.RIGHT_SHOULDER or
                                part == BODY_PARTS_POSE_34.RIGHT_ELBOW or
                                part == BODY_PARTS_POSE_34.RIGHT_WRIST or
                                part == BODY_PARTS_POSE_34.RIGHT_HAND or
                                part == BODY_PARTS_POSE_34.RIGHT_HANDTIP or
                                part == BODY_PARTS_POSE_34.RIGHT_THUMB or
                                part == BODY_PARTS_POSE_34.RIGHT_HIP or
                                part == BODY_PARTS_POSE_34.RIGHT_KNEE or
                                part == BODY_PARTS_POSE_34.RIGHT_ANKLE or
                                part == BODY_PARTS_POSE_34.RIGHT_FOOT or
                                part == BODY_PARTS_POSE_34.RIGHT_HEEL or
                                part == BODY_PARTS_POSE_34.RIGHT_EYE or
                                part == BODY_PARTS_POSE_34.RIGHT_EAR):
                            cv2.circle(image, (int(kp[0]), int(kp[1])), 3, color_right, -1)
                        else:
                            cv2.circle(image, (int(kp[0]), int(kp[1])), 3, color, -1)

        image_resized = cv2.resize(image, dsize=(1280, 720), interpolation=cv2.INTER_AREA)
        cv2.imshow("2D Viewer: Skeleton", image_resized)
        cv2.waitKey(1)

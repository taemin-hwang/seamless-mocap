import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class PoseEstimator:
    def __init__(self, args):
        if args.camera:
            self.pose = mp_pose.Pose(
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)
        else:
            self.pose = mp_pose.Pose(
                smooth_landmarks=True,
                model_complexity=2,
                static_image_mode=True,
                enable_segmentation=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)

    def get_2d_pose_from_image(self, image):
        image.flags.writeable = False
        pose_results = self.pose.process(image)
        return pose_results

    def get_pose_image(self, image, pose_results):
        # Draw the pose annotation on the image.
        image.flags.writeable = True
        mp_drawing.draw_landmarks(
            image,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        return image
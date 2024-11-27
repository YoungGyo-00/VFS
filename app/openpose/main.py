import cv2
import os


class PoseEstimator:
    BODY_PARTS_COCO = {
        0: "Nose",
        1: "Neck",
        2: "RShoulder",
        3: "RElbow",
        4: "RWrist",
        5: "LShoulder",
        6: "LElbow",
        7: "LWrist",
        8: "RHip",
        9: "RKnee",
        10: "RAnkle",
        11: "LHip",
        12: "LKnee",
        13: "LAnkle",
        14: "REye",
        15: "LEye",
        16: "REar",
        17: "LEar",
        18: "Background",
    }

    def __init__(
        self,
    ):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.proto_file = os.path.join(current_dir, "pose_deploy_linevec.prototxt")
        self.weights_file = os.path.join(current_dir, "../pose_iter_440000.caffemodel")
        self.threshold = 0.1

        if not os.path.exists(self.proto_file):
            raise FileNotFoundError(f"Proto file not found: {self.proto_file}")
        if not os.path.exists(self.weights_file):
            raise FileNotFoundError(f"Weights file not found: {self.weights_file}")

        self.net = cv2.dnn.readNetFromCaffe(self.proto_file, self.weights_file)

    def estimate_pose(self, frame):
        image_height, image_width = 368, 368
        input_blob = cv2.dnn.blobFromImage(
            frame,
            1.0 / 255,
            (image_width, image_height),
            (0, 0, 0),
            swapRB=False,
            crop=False,
        )
        self.net.setInput(input_blob)
        out = self.net.forward()
        out_height, out_width = out.shape[2], out.shape[3]
        frame_height, frame_width = frame.shape[:2]

        pose_keypoints = []
        for i in range(len(self.BODY_PARTS_COCO)):
            prob_map = out[0, i, :, :]

            _, prob, _, point = cv2.minMaxLoc(prob_map)

            x = int((frame_width * point[0]) / out_width)
            y = int((frame_height * point[1]) / out_height)

            if prob > self.threshold:
                pose_keypoints.extend([float(x), float(y), float(prob)])
            else:
                pose_keypoints.extend([0.0, 0.0, 0.0])

        return pose_keypoints

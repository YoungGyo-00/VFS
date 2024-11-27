import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import torch
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request
from flask_cors import CORS
import time
import base64


from openpose.main import PoseEstimator
from graphonomy.exp.inference.inference import GraphonomyModel

app = Flask(__name__)
CORS(app)

pose_estimator = PoseEstimator()
graphonomy_model = GraphonomyModel()


@app.route("/process_frame", methods=["POST"])
def process_frame():
    data = request.data

    try:
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print("Error: Failed to decode image.", e)
        return "Failed to decode image", 400

    if frame is None:
        print("Error: Frame is None after decoding.")
        return "Failed to decode image", 400

    # 여기 부분에 모델로 변환하는 코드 작성할 예정이야
    try:
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # 1. openpose 를 통한 몸의 좌표 찾기
        keypoints = pose_estimator.estimate_pose(frame)

        # 2. Graphonomy를 사용하여 세그멘테이션 수행
        segmentation_result, gray_result = graphonomy_model.inference(pil_image)
        _, buffer_segmentation = cv2.imencode(".jpg", segmentation_result)
        _, buffer_gray = cv2.imencode(".jpg", gray_result)
        segmentation_b64 = base64.b64encode(buffer_segmentation).decode("utf-8")
        gray_b64 = base64.b64encode(buffer_gray).decode("utf-8")

        _, buffer = cv2.imencode(".jpg", frame)

        response_data = base64.b64encode(buffer).decode("utf-8")

        return segmentation_b64

    except Exception as e:
        print(f"Error processing frame: {e}")
        return "Error processing frame", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

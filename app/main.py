import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import torch
import cv2
import numpy as np
from flask import Flask, Response
from flask_cors import CORS
from torchvision import transforms
from unet import model
from openpose.main import PoseEstimator


app = Flask(__name__)
CORS(app)

# DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
# model_path = "unet/output/models/unet_epoch_40.pth"
# model = model.UNet(in_channels=3, out_channels=1)
# model.load_state_dict(torch.load(model_path, map_location=DEVICE))
# model.to(DEVICE)
# model.eval()

pose_estimator = PoseEstimator()

preprocess = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ]
)


def postprocess(output):
    output = output.squeeze().cpu().detach().numpy()
    output = (output * 255).astype(np.uint8)
    return output


def generate_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open video.")
        return

    while camera.isOpened():
        success, frame = camera.read()
        if not success:
            break

        output_image, _ = pose_estimator.estimate_pose(frame)
        # input_image = preprocess(frame).unsqueeze(0).to(DEVICE)

        # with torch.no_grad():
        #     output = model(input_image)

        # output_image = postprocess(output)
        print("프레임 생성")

        ret, buffer = cv2.imencode(".jpg", output_image)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    camera.release()


@app.route("/video")
def video():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

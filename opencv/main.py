import cv2
from flask import Flask, Response
from time import localtime, strftime
import os


FILEPATH = "data/images/"


# 프레임 단위로 동영상 분할
def get_image():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다")
        exit()

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    current_time = localtime()
    timestamp = strftime("%Y_%m_%d_%H_%M_%S", current_time)

    print("length :", length)
    print("width :", width)
    print("height :", height)
    print("fps :", fps, "\n")

    try:
        if not os.path.exists(timestamp):
            os.makedirs(FILEPATH + timestamp)
    except OSError:
        print("Directory is already exists : " + timestamp)

    count = 0
    while True:
        # 프레임 읽기
        ret, image = cap.read()

        if ret:
            # 0.1초에 1번씩 캡처
            if cv2.waitKey(100):
                count += 1
                current_time = localtime()
                filename = str(count) + ".jpg"
                filepath = os.path.join(FILEPATH, timestamp, filename)
                cv2.imwrite(filepath, image)
            cv2.imshow("Camera", image)
            if cv2.waitKey(1) != -1:
                break
        else:
            print("프레임을 읽을 수 없습니다")
            break

    cap.release()
    cv2.destroyAllWindows()


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


app = Flask(__name__)


@app.route("/video")
def video():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

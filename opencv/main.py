import cv2
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


get_image()

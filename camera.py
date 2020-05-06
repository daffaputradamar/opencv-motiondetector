import time
import cv2
import os
from datetime import datetime
from base_camera import BaseCamera

class Camera(BaseCamera):
    # video_source = "http://192.168.1.5:8080/video"
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        frame_width = int(camera.get(3))
        frame_height = int(camera.get(4))

        first_frame = None
        status_list = [None, None]
        out = None

        start_time = None
        elapsed_time = 0

        is_recording = False

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, frame = camera.read()
            frame_detected = frame.copy()
            status = 0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if first_frame is None:
                first_frame = gray
                continue

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            delta_frame = cv2.absdiff(first_frame, gray)
            thresh_data = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
            thresh_data = cv2.dilate(thresh_data, None, iterations=0)
            (_, cnts, _) = cv2.findContours(thresh_data.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in cnts:
                if cv2.contourArea(contour) < 1000:
                    continue
                status = 1
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame_detected, (x, y), (x + w, y + h), (0, 255, 0), 3)

            status_list.append(status)
            status_list = status_list[-2:]

            if status_list[-1] == 1 and status_list[-2] == 0:
                if out is None:
                    now = datetime.now();
                    date_time = now.strftime("%d-%m-%Y_%I-%M-%S_%p");
                    file_name = ''.join([os.getcwd(), "\\static\\videos\\", date_time, '.mp4'])
                    out = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc(*'MP4V'), 10,
                                          (frame_width, frame_height))
                is_recording = True

            if status_list[-1] == 0 and status_list[-2] == 1:
                start_time = time.time()

            if is_recording:
                out.write(frame)

            if start_time is not None:
                elapsed_time = time.time() - start_time
                if elapsed_time >= 3:
                    is_recording = False
                    out.release()
                    out = None
                    start_time = None

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', frame_detected)[1].tobytes()

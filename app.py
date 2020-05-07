from flask import Flask, Response, render_template
from camera import Camera
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/videos')
def portfolio():
    videos = os.listdir(os.path.join(app.static_folder, "videos"))
    videos.sort(reverse=True)
    return render_template('videos.html', videos=videos)


if __name__ == '__main__':
    app.run(debug=True)

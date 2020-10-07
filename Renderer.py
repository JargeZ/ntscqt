import os
import time

import cv2
from PyQt5 import QtCore
import ffmpeg

from funcs import resize_to_height


class Renderer(QtCore.QObject):
    running = False
    mainEffect = True
    pause = False
    liveView = False
    newFrame = QtCore.pyqtSignal(object)
    frameMoved = QtCore.pyqtSignal(int)
    renderStateChanged = QtCore.pyqtSignal(bool)
    sendStatus = QtCore.pyqtSignal(str)
    render_data = {}

    def run(self):
        self.running = True
        tmp_output_filename = list(os.path.split(self.render_data["target_file"]))
        tmp_output_filename[1] = "tmp_" + tmp_output_filename[1]
        tmp_output_filename = os.path.join(*tmp_output_filename)
        print(f"Temp render: {tmp_output_filename}")

        orig_wh = (self.render_data["input_video"]["width"], self.render_data["input_video"]["height"])
        render_wh = resize_to_height(orig_wh, self.render_data["input_heigth"])

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(
            tmp_output_filename,
            fourcc,
            self.render_data["input_video"]["orig_fps"],
            render_wh
        )

        frame_index = 0
        self.renderStateChanged.emit(True)
        while self.render_data["input_video"]["cap"].isOpened():
            if self.pause:
                self.sendStatus.emit(f"{status_string} [P]")
                time.sleep(0.3)
                continue

            # Capture frame-by-frame
            frame_index += 1
            self.render_data["input_video"]["cap"].set(1, frame_index)
            ret, frame = self.render_data["input_video"]["cap"].read()
            if not ret or not self.running:
                break

            if orig_wh != render_wh:
                frame = cv2.resize(frame, render_wh)

            if self.mainEffect:
                frame = self.render_data["nt"].composite_layer(frame, frame, field=2, fieldno=2)
                frame = cv2.convertScaleAbs(frame)
                frame[1:-1:2] = frame[0:-2:2] / 2 + frame[2::2] / 2

            if frame_index % 10 == 0 or self.liveView:
                self.frameMoved.emit(frame_index)
                self.newFrame.emit(frame)

            status_string = f'Progress: {frame_index}/{self.render_data["input_video"]["frames_count"]}'
            self.sendStatus.emit(status_string)
            print(status_string)
            video.write(frame)

        video.release()

        audio_orig = (
            ffmpeg
                .input(self.render_data["input_video"]["path"])
        )
        video = ffmpeg.input(tmp_output_filename)
        (
            ffmpeg
                .output(video.video, audio_orig.audio, self.render_data["target_file"], shortest=None, vcodec='copy')
                .overwrite_output()
                .run()
        )
        os.remove(tmp_output_filename)
        self.renderStateChanged.emit(False)

    def stop(self):
        self.running = False

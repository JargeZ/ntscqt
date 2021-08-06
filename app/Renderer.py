import time

import cv2
from PyQt5 import QtCore
import ffmpeg
from imutils.video import FileVideoStream

from app.logs import logger
from app.funcs import resize_to_height, trim_to_4width


class Renderer(QtCore.QObject):
    running = False
    mainEffect = True
    pause = False
    liveView = False
    newFrame = QtCore.pyqtSignal(object)
    frameMoved = QtCore.pyqtSignal(int)
    renderStateChanged = QtCore.pyqtSignal(bool)
    sendStatus = QtCore.pyqtSignal(str)
    increment_progress = QtCore.pyqtSignal()
    render_data = {}

    def run(self):
        self.running = True

        tmp_output = self.render_data['target_file'].parent / f'tmp_{self.render_data["target_file"].name}'

        upscale_2x = self.render_data["upscale_2x"]

        orig_wh = (self.render_data["input_video"]["width"], self.render_data["input_video"]["height"])
        render_wh = resize_to_height(orig_wh, self.render_data["input_heigth"])
        container_wh = render_wh
        if upscale_2x:
            container_wh = (
                render_wh[0] * 2,
                render_wh[1] * 2,
            )

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(
            str(tmp_output.resolve()),
            fourcc,
            self.render_data["input_video"]["orig_fps"],
            # create container as amended with fix crash when frame not divided by 4
            container_wh
        )

        logger.debug(f'Input video: {str(self.render_data["input_video"]["path"].resolve())}')
        logger.debug(f'Temp output: {str(tmp_output.resolve())}')
        logger.debug(f'Output video: {str(self.render_data["target_file"].resolve())}')

        frame_index = 0
        self.renderStateChanged.emit(True)
        cap = FileVideoStream(
            path=str(self.render_data["input_video"]["path"]),
            queue_size=322
        ).start()

        while cap.more():

            if self.pause:
                self.sendStatus.emit(f"{status_string} [P]")
                time.sleep(0.3)
                continue

            # cap.set(1, frame_index)
            frame_index += 1
            frame = cap.read()
            if frame is None or not self.running:
                self.sendStatus.emit(f'Render stopped. ret(debug):')
                break

            self.increment_progress.emit()
            if orig_wh != render_wh:
                frame = cv2.resize(frame, render_wh)

            #  crash workaround
            if render_wh[0] % 4 != 0:
                frame = trim_to_4width(frame)

            if self.mainEffect:
                frame = self.render_data["nt"].composite_layer(frame, frame, field=2, fieldno=2)
                frame = cv2.convertScaleAbs(frame)
                frame[1:-1:2] = frame[0:-2:2] / 2 + frame[2::2] / 2

            if frame_index % 10 == 0 or self.liveView:
                self.frameMoved.emit(frame_index)
                self.newFrame.emit(frame)

            if upscale_2x:
                frame = cv2.resize(frame, dsize=container_wh, interpolation=cv2.INTER_NEAREST)

            status_string = f'Progress: {frame_index}/{self.render_data["input_video"]["frames_count"]}'
            self.sendStatus.emit(status_string)
            video.write(frame)

        video.release()
        audio_orig = (
            ffmpeg
                .input(str(self.render_data["input_video"]["path"].resolve()))
        )
        self.sendStatus.emit('Original audio extracted')
        video = ffmpeg.input(str(tmp_output.resolve()))
        (
            ffmpeg
                .output(video.video, audio_orig.audio, str(self.render_data["target_file"].resolve()),
                        shortest=None, vcodec='copy', acodec='copy')
                .overwrite_output()
                .run()
        )
        self.sendStatus.emit('Audio copy done')
        tmp_output.unlink()
        self.renderStateChanged.emit(False)
        self.sendStatus.emit('Render done')

    def stop(self):
        self.running = False

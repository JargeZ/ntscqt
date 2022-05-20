import time

import cv2
from PyQt5 import QtCore
import ffmpeg
from imutils.video import FileVideoStream

from app.logs import logger
from app.funcs import resize_to_height, trim_to_4width, expand_to_4width


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

        if self.render_data["input_video"]["suffix"] == '.gif':
            suffix = '.mkv'
        else:
            suffix = self.render_data["input_video"]["suffix"]

        tmp_output = self.render_data['target_file'].parent / f'tmp_{self.render_data["target_file"].stem}{suffix}'

        upscale_2x = self.render_data["upscale_2x"]

        orig_wh = (self.render_data["input_video"]["width"], self.render_data["input_video"]["height"])
        render_wh = resize_to_height(orig_wh, self.render_data["input_heigth"])
        container_wh = render_wh
        if upscale_2x:
            container_wh = (
                render_wh[0] * 2,
                render_wh[1] * 2,
            )

        fourccs = [
            cv2.VideoWriter_fourcc(*'mp4v'),  # doesn't work on mac os
            cv2.VideoWriter_fourcc(*'H264')
        ]
        video = cv2.VideoWriter()

        open_result = False
        while not open_result:
            open_result = video.open(
                filename=str(tmp_output.resolve()),
                fourcc=fourccs.pop(0),
                fps=self.render_data["input_video"]["orig_fps"],
                frameSize=container_wh,
            )
            logger.debug(f'Output video open result: {open_result}')

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
                frame = expand_to_4width(frame)

            if self.mainEffect:
                frame = self.render_data["nt"].composite_layer(frame, frame, field=2, fieldno=2)
                frame = cv2.convertScaleAbs(frame)
                frame[1:-1:2] = frame[0:-2:2] / 2 + frame[2::2] / 2

            frame = frame[:, 0:render_wh[0]]

            if frame_index % 10 == 0 or self.liveView:
                self.frameMoved.emit(frame_index)
                self.newFrame.emit(frame)

            if upscale_2x:
                frame = cv2.resize(frame, dsize=container_wh, interpolation=cv2.INTER_NEAREST)

            status_string = f'Progress: {frame_index}/{self.render_data["input_video"]["frames_count"]}'
            self.sendStatus.emit(status_string)
            video.write(frame)

        video.release()

        orig_path = str(self.render_data["input_video"]["path"].resolve())
        orig_suffix = self.render_data["input_video"]["suffix"]
        result_path = str(self.render_data["target_file"].resolve())

        # FIXME beautify file render and audio detection

        orig = ffmpeg.input(orig_path)
        temp_video_stream = ffmpeg.input(str(tmp_output.resolve()))
        # render_streams.append(temp_video_stream.video)

        ff_command = ffmpeg.output(orig.audio, temp_video_stream.video, result_path,
                                   shortest=None, vcodec='copy', acodec='copy')
        logger.debug(ff_command)
        logger.debug(' '.join(ff_command.compile()))
        try:
            ff_command.overwrite_output().run()
        except ffmpeg.Error as e:
            if orig_suffix == '.gif':
                ff_command = ffmpeg.output(temp_video_stream.video, result_path, shortest=None)
            else:
                ff_command = ffmpeg.output(temp_video_stream.video, result_path, shortest=None, vcodec='copy')
            ff_command.overwrite_output().run()

        self.sendStatus.emit('Audio copy done')
        tmp_output.unlink()
        self.renderStateChanged.emit(False)
        self.sendStatus.emit('Render done')

    def stop(self):
        self.running = False

import time
import os

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

    lossless = False

    process_audio = False
    audio_sat_beforevol = 4.5
    audio_lowpass = 10896
    audio_noise_volume = 0.03

    def run(self):
        self.running = True

        suffix = '.mkv'

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

        if(self.lossless):
            fourcc_choice = cv2.VideoWriter_fourcc(*'FFV1')
        else:
            fourcc_choice = fourccs.pop(0)

        video = cv2.VideoWriter()

        open_result = False
        while not open_result:
            open_result = video.open(
                filename=str(tmp_output.resolve()),
                fourcc=fourcc_choice,
                fps=self.render_data["input_video"]["orig_fps"],
                frameSize=container_wh,
            )
            logger.debug(f'Output video open result: {open_result}')

        logger.debug(f'Input video: {str(self.render_data["input_video"]["path"].resolve())}')
        logger.debug(f'Temp output: {str(tmp_output.resolve())}')
        logger.debug(f'Output video: {str(self.render_data["target_file"].resolve())}')
        #logger.debug(f'Process audio: {self.process_audio}')

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

            status_string = f'[CV2] Render progress: {frame_index}/{self.render_data["input_video"]["frames_count"]}'
            self.sendStatus.emit(status_string)
            video.write(frame)

        video.release()

        orig_path = str(self.render_data["input_video"]["path"].resolve())
        orig_suffix = self.render_data["input_video"]["suffix"]
        result_path = str(self.render_data["target_file"].resolve())

        # FIXME beautify file render and audio detection

        #self.sendStatus.emit(f'[FFMPEG] Copying audio to {result_path}')

        orig = ffmpeg.input(orig_path)

        final_audio = orig.audio

        if(self.process_audio == True):
            self.sendStatus.emit(f'[FFMPEG] Preparing audio filtering')

            #tmp_audio = self.render_data['target_file'].parent / f'tmp_audio_{self.render_data["target_file"].stem}.wav'
            tmp_audio = f"{self.render_data['target_file'].parent}/tmp_audio_{self.render_data['target_file'].stem}.wav"

            aud_ff_probe = ffmpeg.probe(orig_path)

            #aud_ff_video_stream = next((stream for stream in aud_ff_probe['streams'] if stream['codec_type'] == 'video'), None)
            #aud_ff_duration = aud_ff_video_stream['duration']
            aud_ff_duration = aud_ff_probe["format"]["duration"]

            aud_ff_audio_stream = next((stream for stream in aud_ff_probe['streams'] if stream['codec_type'] == 'audio'), None)
            aud_ff_srate = aud_ff_audio_stream['sample_rate']
            aud_ff_clayout = aud_ff_audio_stream['channel_layout']

            aud_ff_noise = ffmpeg.input(f'aevalsrc=-2+random(0):sample_rate={aud_ff_srate}:channel_layout=mono',f="lavfi",t=aud_ff_duration)
            aud_ff_noise = ffmpeg.filter((aud_ff_noise, aud_ff_noise), 'join', inputs=2, channel_layout='stereo')
            aud_ff_noise = aud_ff_noise.filter('volume', self.audio_noise_volume)

            aud_ff_fx = final_audio.filter("volume",self.audio_sat_beforevol).filter("alimiter",limit="0.5").filter("volume",0.8)
            aud_ff_fx = aud_ff_fx.filter("firequalizer",gain=f'if(lt(f,{self.audio_lowpass}), 0, -INF)')

            aud_ff_mix = ffmpeg.filter([aud_ff_fx, aud_ff_noise], 'amix').filter("firequalizer",gain='if(lt(f,13301), 0, -INF)')

            aud_ff_command = aud_ff_mix.output(tmp_audio,acodec='pcm_s24le',shortest=None)

            self.sendStatus.emit(f'[FFMPEG] Prepared audio filtering')
            logger.debug(aud_ff_command)
            logger.debug(' '.join(aud_ff_command.compile()))

            self.sendStatus.emit(f'[FFMPEG] Starting audio filtering into {tmp_audio}')
            aud_ff_command.overwrite_output().global_args('-v', 'verbose').run()

            final_audio = ffmpeg.input(tmp_audio)
            final_audio = final_audio.audio

            self.sendStatus.emit(f'[FFMPEG] Finished audio filtering')
        else:
            self.sendStatus.emit(f'[FFMPEG] Copying audio to {result_path}')

        temp_video_stream = ffmpeg.input(str(tmp_output.resolve()))
        # render_streams.append(temp_video_stream.video)

        if self.process_audio:
            ff_command = ffmpeg.output(temp_video_stream.video, final_audio, result_path, shortest=None, vcodec='copy', acodec='flac')
        else:
            ff_command = ffmpeg.output(temp_video_stream.video, final_audio, result_path, shortest=None, vcodec='copy', acodec='copy')
        
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

        self.sendStatus.emit('[FFMPEG] Audio copy done')

        tmp_output.unlink()
        if self.process_audio:
            if os.path.exists(tmp_audio):
                os.remove(tmp_audio)

        self.renderStateChanged.emit(False)
        self.sendStatus.emit('[DONE] Render done')

    def stop(self):
        self.running = False

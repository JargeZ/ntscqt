from pathlib import Path
import cv2
import numpy
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel, QCheckBox, QInputDialog
from numpy import ndarray

from app.Renderer import Renderer
from app.funcs import resize_to_height, pick_save_file, trim_to_4width
from app.ntsc import random_ntsc, Ntsc
from ui import mainWindow
from ui.DoubleSlider import DoubleSlider


class NtscApp(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    def __init__(self):
        self.current_frame = False
        self.input_video = {}
        self.orig_wh = (0, 0)
        self.compareMode = False
        self.isRenderActive = False
        self.mainEffect = True
        self.nt_controls = {}
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.supported_video_type = ['.mp4', '.mkv', '.avi', '.webm', '.mpg']
        self.supported_image_type = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.strings = {
            "_composite_preemphasis": self.tr("Composite preemphasis"),
            "_vhs_out_sharpen": self.tr("VHS out sharpen"),
            "_vhs_edge_wave": self.tr("Edge wave"),
            "_output_vhs_tape_speed": self.tr("VHS tape speed"),
            "_ringing": self.tr("Ringing"),
            "_ringing_power": self.tr("Ringing power"),
            "_ringing_shift": self.tr("Ringing shift"),
            "_freq_noise_size": self.tr("Freq noise size"),
            "_freq_noise_amplitude": self.tr("Freq noise amplitude"),
            "_color_bleed_horiz": self.tr("Color bleed horiz"),
            "_color_bleed_vert": self.tr("Color bleed vert"),
            "_video_chroma_noise": self.tr("Video chroma noise"),
            "_video_chroma_phase_noise": self.tr("Video chroma phase noise"),
            "_video_chroma_loss": self.tr("Video chroma loss"),
            "_video_noise": self.tr("Video noise"),
            "_video_scanline_phase_shift": self.tr("Video scanline phase shift"),
            "_video_scanline_phase_shift_offset": self.tr("Video scanline phase shift offset"),
            "_head_switching_speed": self.tr("Head switch move speed"),
            "_vhs_head_switching": self.tr("Head switching"),
            "_color_bleed_before": self.tr("Color bleed before"),
            "_enable_ringing2": self.tr("Enable ringing2"),
            "_composite_in_chroma_lowpass": self.tr("Composite in chroma lowpass"),
            "_composite_out_chroma_lowpass": self.tr("Composite out chroma lowpass"),
            "_composite_out_chroma_lowpass_lite": self.tr("Composite out chroma lowpass lite"),
            "_emulating_vhs": self.tr("VHS emulating"),
            "_nocolor_subcarrier": self.tr("Nocolor subcarrier"),
            "_vhs_chroma_vert_blend": self.tr("VHS chroma vert blend"),
            "_vhs_svideo_out": self.tr("VHS svideo out"),
            "_output_ntsc": self.tr("NTSC output"),
        }
        self.add_slider("_composite_preemphasis", 0, 10, float)
        self.add_slider("_vhs_out_sharpen", 1, 5)
        self.add_slider("_vhs_edge_wave", 0, 10)
        # self.add_slider("_output_vhs_tape_speed", 0, 10)
        self.add_slider("_ringing", 0, 1, float)
        self.add_slider("_ringing_power", 0, 10)
        self.add_slider("_ringing_shift", 0, 3, float)
        self.add_slider("_freq_noise_size", 0, 2, float)
        self.add_slider("_freq_noise_amplitude", 0, 5)
        self.add_slider("_color_bleed_horiz", 0, 10)
        self.add_slider("_color_bleed_vert", 0, 10)
        self.add_slider("_video_chroma_noise", 0, 16384)
        self.add_slider("_video_chroma_phase_noise", 0, 50)
        self.add_slider("_video_chroma_loss", 0, 100_000)
        self.add_slider("_video_noise", 0, 4200)
        self.add_slider("_video_scanline_phase_shift", 0, 270)
        self.add_slider("_video_scanline_phase_shift_offset", 0, 3)

        self.add_slider("_head_switching_speed", 0, 100)

        self.add_checkbox("_vhs_head_switching", (1, 1))
        self.add_checkbox("_color_bleed_before", (1, 2))
        self.add_checkbox("_enable_ringing2", (2, 1))
        self.add_checkbox("_composite_in_chroma_lowpass", (2, 2))
        self.add_checkbox("_composite_out_chroma_lowpass", (3, 1))
        self.add_checkbox("_composite_out_chroma_lowpass_lite", (3, 2))
        self.add_checkbox("_emulating_vhs", (4, 1))
        self.add_checkbox("_nocolor_subcarrier", (4, 2))
        self.add_checkbox("_vhs_chroma_vert_blend", (5, 1))
        self.add_checkbox("_vhs_svideo_out", (5, 2))
        self.add_checkbox("_output_ntsc", (6, 1))

        self.previewHeightBox.valueChanged.connect(
            lambda: self.set_current_frame(self.current_frame)
        )
        self.openFile.clicked.connect(self.open_file)
        self.renderVideoButton.clicked.connect(self.render_video)
        self.saveImageButton.clicked.connect(self.render_image)
        self.stopRenderButton.clicked.connect(self.stop_render)
        self.compareModeButton.stateChanged.connect(self.toggle_compare_mode)
        self.toggleMainEffect.stateChanged.connect(self.toggle_main_effect)
        self.pauseRenderButton.clicked.connect(self.toggle_pause_render)
        self.livePreviewCheckbox.stateChanged.connect(self.toggle_live_preview)
        self.refreshFrameButton.clicked.connect(self.nt_update_preview)
        self.openImageUrlButton.clicked.connect(self.open_image_by_url)

        self.seedSpinBox.valueChanged.connect(self.update_seed)
        self.seedSpinBox.setValue(3)

    def setup_renderer(self):
        try:
            self.update_status("Terminating prev renderer")
            print("Terminating prev renderer")
            self.thread.quit()
            self.update_status("Waiting prev renderer")
            print("Waiting prev renderer")
            self.thread.wait()
        except AttributeError:
            print("Setup first renderer")
        # создадим поток
        self.thread = QtCore.QThread()
        # создадим объект для выполнения кода в другом потоке
        self.videoRenderer = Renderer()
        # перенесём объект в другой поток
        self.videoRenderer.moveToThread(self.thread)
        # после чего подключим все сигналы и слоты
        self.videoRenderer.newFrame.connect(self.render_preview)
        self.videoRenderer.frameMoved.connect(self.videoTrackSlider.setValue)
        self.videoRenderer.renderStateChanged.connect(self.set_render_state)
        self.videoRenderer.sendStatus.connect(self.update_status)
        # подключим сигнал старта потока к методу run у объекта, который должен выполнять код в другом потоке
        self.thread.started.connect(self.videoRenderer.run)

    @QtCore.pyqtSlot()
    def stop_render(self):
        self.videoRenderer.stop()

    @QtCore.pyqtSlot()
    def toggle_compare_mode(self):
        state = self.sender().isChecked()
        self.compareMode = state
        self.nt_update_preview()

    @QtCore.pyqtSlot()
    def toggle_pause_render(self):
        button = self.sender()
        if not self.isRenderActive:
            self.update_status("Render is not running")
            button.setChecked(False)
            return None
        state = button.isChecked()
        self.videoRenderer.pause = state

    def toggle_live_preview(self):
        button = self.sender()
        state = button.isChecked()
        try:
            self.videoRenderer.liveView = state
        except AttributeError:
            pass

    @QtCore.pyqtSlot()
    def toggle_main_effect(self):
        state = self.toggleMainEffect.isChecked()
        self.mainEffect = state
        try:
            self.videoRenderer.mainEffect = state
        except AttributeError:
            pass
        self.nt_update_preview()

    @QtCore.pyqtSlot(int)
    def update_seed(self, seed):
        self.nt = random_ntsc(seed)
        self.nt._enable_ringing2 = True
        self.sync_nt_to_sliders()

    @QtCore.pyqtSlot(str)
    def update_status(self, string):
        self.statusLabel.setText(string)

    @QtCore.pyqtSlot(bool)
    def set_render_state(self, is_render_active):
        self.isRenderActive = is_render_active

        self.videoTrackSlider.blockSignals(is_render_active)

        self.openFile.setEnabled(not is_render_active)
        self.renderVideoButton.setEnabled(not is_render_active)
        self.stopRenderButton.setEnabled(is_render_active)

        # todo: сделать реассигн параметров во время рендера
        self.seedSpinBox.setEnabled(not is_render_active)

    def sync_nt_to_sliders(self):
        for parameter_name, element in self.nt_controls.items():
            value = getattr(self.nt, parameter_name)

            element.blockSignals(True)
            if isinstance(value, bool):
                element.setChecked(value)
            elif isinstance(value, (int, float)):
                element.setValue(value)
            element.blockSignals(False)

            related_label = element.parent().findChild(QLabel, parameter_name)
            if related_label:
                related_label.setText(str(value)[:7])

            print(f"set {type(value)} {parameter_name} slider to {value}")
        self.nt_update_preview()

    def value_changed_slot(self):
        element = self.sender()
        parameter_name = element.objectName()
        if isinstance(element, (QSlider, DoubleSlider)):
            value = element.value()
            related_label = element.parent().findChild(QLabel, parameter_name)
            if related_label:
                related_label.setText(str(value)[:7])
        elif isinstance(element, QCheckBox):
            value = element.isChecked()

        self.update_status(f"Set {parameter_name} to {value}")
        print(f"Set {parameter_name} to {value}")
        setattr(self.nt, parameter_name, value)
        self.nt_update_preview()

    def add_checkbox(self, param_name, pos):
        checkbox = QCheckBox()
        checkbox.setText(self.strings[param_name])
        checkbox.setObjectName(param_name)
        checkbox.stateChanged.connect(self.value_changed_slot)
        # checkbox.mouseReleaseEvent(lambda: self.controls_set())
        self.nt_controls[param_name] = checkbox
        self.checkboxesLayout.addWidget(checkbox, pos[0], pos[1])

    def add_slider(self, param_name, min_val, max_val, slider_value_type=int):
        slider_layout = QHBoxLayout()
        if slider_value_type is int:
            slider = QSlider()
            # box = QSpinBox()
            slider.valueChanged.connect(self.value_changed_slot)
        elif slider_value_type is float:
            # box = QDoubleSpinBox()
            # box.setSingleStep(0.1)
            slider = DoubleSlider()
            slider.mouseRelease.connect(self.value_changed_slot)

        slider.blockSignals(True)
        slider.setEnabled(True)
        slider.setMaximum(max_val)
        slider.setMinimum(min_val)
        slider.setMouseTracking(False)
        if max_val < 100 and slider_value_type == int:
            slider.setTickPosition(QSlider.TicksLeft)
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.setObjectName(f"{param_name}")
        slider.blockSignals(False)

        label = QLabel()
        # label.setText(description or name)
        label.setText(self.strings[param_name])

        # todo: сделать рандомайзер вместо бокса
        # box.setMinimum(min_val)
        # box.setMaximum(max_val)
        # box.valueChanged.connect(slider.setValue)
        # slider.valueChanged.connect(box.setValue)
        value_label = QLabel()
        value_label.setObjectName(param_name)
        # slider.valueChanged.connect(lambda intval: value_label.setText(str(intval)))

        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)
        # slider_layout.addWidget(box)
        slider_layout.addWidget(value_label)

        self.nt_controls[param_name] = slider
        self.controlLayout.addLayout(slider_layout)

    def get_current_video_frame(self):
        preview_h = self.previewHeightBox.value()
        if not self.input_video or preview_h < 10:
            return None
        frame_no = self.videoTrackSlider.value()
        self.input_video["cap"].set(1, frame_no)
        ret, frame = self.input_video["cap"].read()
        return frame

    def set_current_frame(self, frame):
        current_frame_valid = isinstance(frame, ndarray)
        preview_h = self.previewHeightBox.value()
        if not current_frame_valid or preview_h < 10:
            self.update_status("Trying to set invalid current frame")
            return None

        self.current_frame = frame
        try:
            crop_wh = resize_to_height(self.orig_wh, preview_h)
            self.preview = cv2.resize(frame, crop_wh)
        except ZeroDivisionError:
            self.update_status("ZeroDivisionError :DDDDDD")
            pass

        if self.preview.shape[1] % 4 != 0:
            self.preview = trim_to_4width(self.preview)

        self.nt_update_preview()

    @QtCore.pyqtSlot()
    def open_image_by_url(self):
        url, ok = QInputDialog.getText(self, self.tr('Open image by url'), self.tr('Image url:'))
        if ok:
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                ret, img = cap.read()
                self.set_image_mode()
                self.open_image(img)
            else:
                self.update_status(self.tr('Error opening image url :('))
                return None

    def open_file(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Select File")
        if file:
            path = Path(file[0])
        else:
            return None
        file_suffix = path.suffix.lower()
        if file_suffix in self.supported_video_type:
            self.set_video_mode()
            self.open_video(path)
        elif file_suffix in self.supported_image_type:
            self.set_image_mode()
            img = cv2.imread(str(path.resolve()))
            self.open_image(img)
        else:
            self.update_status(f"Unsopported file type {file_suffix}")

    def set_video_mode(self):
        self.videoTrackSlider.blockSignals(False)
        self.videoTrackSlider.show()
        self.pauseRenderButton.show()
        self.stopRenderButton.show()
        self.livePreviewCheckbox.show()
        self.renderVideoButton.show()

    def set_image_mode(self):
        self.videoTrackSlider.blockSignals(True)
        self.videoTrackSlider.hide()
        self.pauseRenderButton.hide()
        self.stopRenderButton.hide()
        self.livePreviewCheckbox.hide()
        self.renderVideoButton.hide()

    def open_image(self, img: numpy.ndarray):
        height, width, channels = img.shape
        self.orig_wh = width, height
        if height > 1337:
            self.renderHeightBox.setValue(600)
            self.update_status(
                self.tr('The image resolution is large. For the best effect, the output height is set to 600'))
        else:
            self.renderHeightBox.setValue(height)
        self.set_current_frame(img)

    def open_video(self, path: Path):
        print(f"file: {path}")
        cap = cv2.VideoCapture(str(path))
        print(f"cap: {cap} isOpened: {cap.isOpened()}")
        self.input_video = {
            "cap": cap,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "frames_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "orig_fps": int(cap.get(cv2.CAP_PROP_FPS)),
            "path": path
        }
        print(f"selfinput: {self.input_video}")
        self.orig_wh = (int(self.input_video["width"]), int(self.input_video["height"]))
        self.set_current_frame(self.get_current_video_frame())
        self.renderHeightBox.setValue(self.input_video["height"])
        self.videoTrackSlider.setMinimum(1)
        self.videoTrackSlider.setMaximum(self.input_video["frames_count"])
        self.videoTrackSlider.valueChanged.connect(
            lambda: self.set_current_frame(self.get_current_video_frame())
        )

    def render_image(self):
        target_file = pick_save_file(self, title='Save frame as', suffix='.png')
        render_h = self.renderHeightBox.value()
        crop_wh = resize_to_height(self.orig_wh, render_h)
        image = cv2.resize(self.current_frame, crop_wh)
        if image.shape[1] % 4 != 0:
            image = trim_to_4width(image)
        image = self.nt_process(image)
        cv2.imwrite(str(target_file.resolve()), image)

    def render_video(self):
        target_file = pick_save_file(self, title='Render video as', suffix='.mp4')

        render_data = {
            "target_file": target_file,
            "nt": self.nt,
            "input_video": self.input_video,
            "input_heigth": self.renderHeightBox.value()
        }
        self.setup_renderer()
        self.toggle_main_effect()
        self.videoRenderer.render_data = render_data
        self.thread.start()

    def nt_process(self, frame) -> ndarray:
        _ = self.nt.composite_layer(frame, frame, field=2, fieldno=2)
        ntsc_out_image = cv2.convertScaleAbs(_)
        ntsc_out_image[1:-1:2] = ntsc_out_image[0:-2:2] / 2 + ntsc_out_image[2::2] / 2
        return ntsc_out_image

    def nt_update_preview(self):
        current_frame_valid = isinstance(self.current_frame, ndarray)
        render_on_pause = self.pauseRenderButton.isChecked()
        if not current_frame_valid or (self.isRenderActive and not render_on_pause):
            return None

        if not self.mainEffect:
            self.render_preview(self.preview)
            return None

        ntsc_out_image = self.nt_process(self.preview)

        if self.compareMode:
            ntsc_out_image = numpy.concatenate(
                (self.preview[:self.preview.shape[0] // 2], ntsc_out_image[ntsc_out_image.shape[0] // 2:])
            )

        self.render_preview(ntsc_out_image)

    @QtCore.pyqtSlot(object)
    def render_preview(self, img):
        image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image))


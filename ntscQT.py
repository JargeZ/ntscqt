import sys
from pathlib import Path
import cv2
import numpy
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel, QCheckBox, QFileDialog
from numpy import ndarray

from Renderer import Renderer
from funcs import resize_to_height
from ntsc import random_ntsc
from ui import mainWindow
from ui.DoubleSlider import DoubleSlider


class ExampleApp(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    def __init__(self):
        self.current_frame = False
        self.input_video = {}
        self.compareMode = False
        self.isRenderActive = False
        self.mainEffect = True
        self.nt_controls = {}
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

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

        self.previewHeightBox.valueChanged.connect(self.set_current_frame)

        self.openFile.clicked.connect(self.open_video)
        self.renderVideoButton.clicked.connect(self.render)
        self.stopRenderButton.clicked.connect(self.stop_render)
        self.compareModeButton.stateChanged.connect(self.toggle_compare_mode)
        self.toggleMainEffect.stateChanged.connect(self.toggle_main_effect)
        self.pauseRenderButton.clicked.connect(self.toggle_pause_render)
        self.livePreviewCheckbox.stateChanged.connect(self.toggle_live_preview)

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
        self.videoRenderer.newFrame.connect(self.update_preview)
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

    def add_checkbox(self, name, pos):
        checkbox = QCheckBox()
        checkbox.setText(name)
        checkbox.setObjectName(name)
        checkbox.stateChanged.connect(self.value_changed_slot)
        # checkbox.mouseReleaseEvent(lambda: self.controls_set())
        self.nt_controls[name] = checkbox
        self.checkboxesLayout.addWidget(checkbox, pos[0], pos[1])

    def add_slider(self, name, min_val, max_val, slider_value_type=int):
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
        slider.setTickPosition(QSlider.TicksLeft)
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.setObjectName(f"{name}")
        slider.blockSignals(False)

        label = QLabel()
        label.setText(name)

        # todo: сделать рандомайзер вместо бокса
        # box.setMinimum(min_val)
        # box.setMaximum(max_val)
        # box.valueChanged.connect(slider.setValue)
        # slider.valueChanged.connect(box.setValue)
        value_label = QLabel()
        value_label.setObjectName(name)
        # slider.valueChanged.connect(lambda intval: value_label.setText(str(intval)))

        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)
        # slider_layout.addWidget(box)
        slider_layout.addWidget(value_label)

        self.nt_controls[name] = slider
        self.controlLayout.addLayout(slider_layout)

    def set_current_frame(self):
        preview_h = self.previewHeightBox.value()
        if not self.input_video or preview_h < 10:
            return None
        frame_no = self.videoTrackSlider.value()
        self.input_video["cap"].set(1, frame_no)
        ret, frame = self.input_video["cap"].read()

        orig_wh = (int(self.input_video["width"]), int(self.input_video["height"]))
        try:
            crop_wh = resize_to_height(orig_wh, preview_h)
            self.current_frame = cv2.resize(frame, crop_wh)
        except ZeroDivisionError:
            self.update_status("ZeroDivisionError :DDDDDD")
            pass
        self.nt_update_preview()

    def open_video(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Select File")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории
        if file:
            norm_path = Path(file[0])
            print(f"file: {norm_path}")
            cap = cv2.VideoCapture(str(norm_path))
            print(f"cap: {cap} isOpened: {cap.isOpened()}")
            self.input_video = {
                "cap": cap,
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "frames_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "orig_fps": int(cap.get(cv2.CAP_PROP_FPS)),
                "path": norm_path
            }
            print(f"selfinput: {self.input_video}")
            self.set_current_frame()
            self.renderHeightBox.setValue(self.input_video["height"])
            self.videoTrackSlider.setMinimum(1)
            self.videoTrackSlider.setMaximum(self.input_video["frames_count"])
            self.videoTrackSlider.valueChanged.connect(self.set_current_frame)

    def render(self):
        # file_dialog = QtWidgets.QFileDialog()
        # file_dialog.setNameFilters([self.tr('MP4 file (*.mp4)'), self.tr('All Files (*)')])
        # file_dialog.setDefaultSuffix('.mp4')
        target_file = QFileDialog.getSaveFileName(self, 'Render As', '', "Video mp4 (*.mp4);;All Files (*)")
        print(f"Save picked as: {target_file}")
        if not target_file[0]:
            return None
        if target_file[1] == 'Video mp4 (*.mp4)' and target_file[0][-4:] != '.mp4':
            target_file = target_file[0] + '.mp4'
        else:
            target_file = target_file[0]
        target_file = Path(target_file)
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

    def nt_update_preview(self):
        current_frame_valid = isinstance(self.current_frame, ndarray)
        render_on_pause = self.pauseRenderButton.isChecked()
        if not current_frame_valid or (self.isRenderActive and not render_on_pause):
            return None

        if not self.mainEffect:
            self.update_preview(self.current_frame)
            return None

        frame = self.nt.composite_layer(self.current_frame, self.current_frame, field=2, fieldno=2)
        norm_image = cv2.convertScaleAbs(frame)
        norm_image[1:-1:2] = norm_image[0:-2:2] / 2 + norm_image[2::2] / 2
        if self.compareMode:
            norm_image = numpy.concatenate(
                (self.current_frame[:self.current_frame.shape[0] // 2], norm_image[norm_image.shape[0] // 2:])
            )

        self.update_preview(norm_image)

    @QtCore.pyqtSlot(object)
    def update_preview(self, img):
        image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image))


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()

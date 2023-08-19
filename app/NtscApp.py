import json
from pathlib import Path
from random import randint
from typing import Tuple, Union, List, Dict, Any, TypeVar, Generic, Callable, Type
import requests
import cv2
import numpy
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel, QCheckBox, QInputDialog, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QFrame
from numpy import ndarray
from abc import abstractmethod

from app.InterlacedRenderer import InterlacedRenderer
from app.config_dialog import ConfigDialog
from app.logs import logger
from app.Renderer import DefaultRenderer
from app.funcs import resize_to_height, pick_save_file, trim_to_4width
from app.ntsc import random_ntsc, Ntsc, VHSSpeed
from ui import mainWindow
from ui.DoubleSlider import DoubleSlider

T = TypeVar("T")

class Control(Generic[T]):
    _param_name: str
    _on_change: Callable[[str, T], Any]

    def __init__(self, param_name: str, on_change: Callable[[str, T], Any]):
        self._param_name = param_name
        self._on_change = on_change

    def _on_value_change(self):
        self._on_change(self._param_name, self.get_value())

    @abstractmethod
    def get_value(self) -> T:
        pass

    @abstractmethod
    def set_value(self, value: Any, block_signals=False) -> None:
        pass

    @abstractmethod
    def set_visible(self, visible: bool) -> None:
        pass


class CheckboxControl(Control[bool]):
    checkbox: QCheckBox

    def __init__(self, param_name: str, text: str, on_change: Callable[[str, bool], Any]):
        super().__init__(param_name, on_change)

        self.checkbox = QCheckBox()
        self.checkbox.setText(text)
        self.checkbox.setObjectName(param_name)
        self.checkbox.stateChanged.connect(self._on_value_change)

    def get_value(self):
        return self.checkbox.isChecked()

    def set_value(self, value, block_signals=False):
        if block_signals:
            self.checkbox.blockSignals(True)
        self.checkbox.setChecked(bool(value))
        self.checkbox.blockSignals(False)

    def set_visible(self, visible):
        self.checkbox.setVisible(visible)


Num = TypeVar("Num", bound=Union[int, float])

class SliderControl(Control[Num]):
    _slider_value_type: Type[Num]

    label: QLabel
    slider: Union[QSlider, DoubleSlider]
    box: Union[QSpinBox, QDoubleSpinBox]
    slider_frame: QFrame

    def __init__(
        self,
        param_name: str,
        text: str,
        on_change: Callable[[str, Num], Any],
        min_val: Num,
        max_val: Num,
        slider_value_type: Type[Num]
    ):
        super().__init__(param_name, on_change)

        self._slider_value_type = slider_value_type

        self.label = QLabel()
        self.label.setText(text)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        ly = QHBoxLayout()
        ly.setContentsMargins(0, 0, 0, 0)
        self.slider_frame = QFrame()
        self.slider_frame.setLayout(ly)

        if slider_value_type is int:
            self.slider = QSlider()
            self.box = QSpinBox()
        elif slider_value_type is float:
            self.box = QDoubleSpinBox()
            self.box.setSingleStep(0.1)
            self.slider = DoubleSlider()
        else:
            raise ValueError(f"Invalid slider value type: {slider_value_type.__name__}")

        self.slider.blockSignals(True)
        self.box.blockSignals(True)

        self.box.setMinimum(min_val)
        self.box.setMaximum(max_val)
        self.box.setFixedWidth(64)
        self.slider.valueChanged.connect(self.box.setValue)
        self.box.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self._on_value_change)

        self.slider.setMaximum(max_val)
        self.slider.setMinimum(min_val)
        self.slider.setMouseTracking(False)
        if max_val < 100 and slider_value_type == int:
            self.slider.setTickPosition(QSlider.TicksLeft)
            self.slider.setTickInterval(1)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName(param_name)

        self.slider.blockSignals(False)
        self.box.blockSignals(False)

        ly.addWidget(self.slider)
        ly.addWidget(self.box)

    def get_value(self):
        return self._slider_value_type(self.slider.value())

    def set_value(self, value, block_signals=False):
        if block_signals:
            self.slider.blockSignals(True)
            self.box.blockSignals(True)
        self.slider.setValue(self._slider_value_type(value))
        self.box.setValue(self._slider_value_type(value))
        self.slider.blockSignals(False)
        self.box.blockSignals(False)

    def set_visible(self, visible):
        self.label.setVisible(visible)
        self.slider_frame.setVisible(visible)

class ComboBoxControl(Control[T]):
    _values: List[T]
    _values_to_indices: Dict[T, int]

    label: QLabel
    box: QComboBox
    slider_frame: QFrame

    def __init__(
        self,
        param_name: str,
        text: str,
        on_change: Callable[[str, T], Any],
        values: List[Tuple[str, T]]
    ):
        super().__init__(param_name, on_change)

        self._values = [value[1] for value in values]

        self.label = QLabel()
        self.label.setText(text)
        self.box = QComboBox()

        # map values back to indices for use in sync_nt_to_sliders
        self._values_to_indices = {}

        for index, (text, data) in enumerate(values):
            self.box.addItem(text, data)
            self._values_to_indices[data] = index
        self.box.setObjectName(param_name)

        self.box.currentIndexChanged.connect(self._on_value_change)

    def get_value(self):
        index = self.box.currentIndex()
        return None if index == -1 else self._values[index]

    def set_value(self, value, block_signals=False):
        if block_signals:
            self.box.blockSignals(True)
        self.box.setCurrentIndex(self._values_to_indices.get(value, -1))
        self.box.blockSignals(False)

    def set_visible(self, visible):
        self.label.setVisible(visible)
        self.box.setVisible(visible)


class NtscApp(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    render_thread: QtCore.QThread
    def __init__(self):
        self.videoRenderer: DefaultRenderer = None
        self.current_frame: numpy.ndarray = False
        self.next_frame: numpy.ndarray = False
        self.scale_pixmap = False
        self.input_video = {}
        self.templates = {}
        self.orig_wh: Tuple[int, int] = (0, 0)
        self.compareMode: bool = False
        self.isRenderActive: bool = False
        self.mainEffect: bool = True
        self.lossless_mode: bool = False
        self.__video_output_suffix = ".mp4"  # or .mkv for FFV1
        self.ProcessAudio: bool = False
        self.nt_controls: Dict[str, Control] = {}
        self.nt: Ntsc = None
        self.pro_mode_elements: List[Control] = []
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.supported_video_type = ['.mp4', '.mkv', '.avi', '.webm', '.mpg', '.gif']
        self.supported_image_type = ['.png', '.jpg', '.jpeg', '.webp']
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.strings = {
            "_composite_preemphasis": self.tr("Composite preemphasis"),
            "_vhs_out_sharpen": self.tr("VHS out sharpen"),
            "_vhs_edge_wave": self.tr("Edge wave"),
            "_output_vhs_tape_speed": self.tr("VHS tape speed"),
            "_output_vhs_tape_speed_sp": self.tr("SP (Standard Play)"),
            "_output_vhs_tape_speed_lp": self.tr("LP (Long Play)"),
            "_output_vhs_tape_speed_ep": self.tr("EP (Extended Play)"),
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
            "_black_line_cut": self.tr("Cut 2% black line"),
        }
        self.add_slider("_composite_preemphasis", 0, 10, float)
        self.add_slider("_vhs_out_sharpen", 1, 5)
        self.add_slider("_vhs_edge_wave", 0, 10)
        self.add_menu("_output_vhs_tape_speed", [
            (self.strings["_output_vhs_tape_speed_sp"], VHSSpeed.VHS_SP),
            (self.strings["_output_vhs_tape_speed_lp"], VHSSpeed.VHS_LP),
            (self.strings["_output_vhs_tape_speed_ep"], VHSSpeed.VHS_EP)
        ])
        self.add_slider("_ringing", 0, 1, float, pro=True)
        self.add_slider("_ringing_power", 0, 10)
        self.add_slider("_ringing_shift", 0, 3, float, pro=True)
        self.add_slider("_freq_noise_size", 0, 2, float, pro=True)
        self.add_slider("_freq_noise_amplitude", 0, 5, pro=True)
        self.add_slider("_color_bleed_horiz", 0, 10)
        self.add_slider("_color_bleed_vert", 0, 10)
        self.add_slider("_video_chroma_noise", 0, 16384)
        self.add_slider("_video_chroma_phase_noise", 0, 50)
        self.add_slider("_video_chroma_loss", 0, 800)
        self.add_slider("_video_noise", 0, 4200)
        self.add_slider("_video_scanline_phase_shift", 0, 270, pro=True)
        self.add_slider("_video_scanline_phase_shift_offset", 0, 3, pro=True)

        self.add_slider("_head_switching_speed", 0, 100)

        self.add_checkbox("_vhs_head_switching", (1, 1))
        self.add_checkbox("_color_bleed_before", (6, 2), pro=True)
        self.add_checkbox("_enable_ringing2", (2, 1), pro=True)
        self.add_checkbox("_composite_in_chroma_lowpass", (2, 2), pro=True)
        self.add_checkbox("_composite_out_chroma_lowpass", (3, 1), pro=True)
        self.add_checkbox("_composite_out_chroma_lowpass_lite", (3, 2), pro=True)
        self.add_checkbox("_emulating_vhs", (4, 1))
        self.add_checkbox("_nocolor_subcarrier", (4, 2), pro=True)
        self.add_checkbox("_vhs_chroma_vert_blend", (5, 1), pro=True)
        self.add_checkbox("_vhs_svideo_out", (5, 2), pro=True)
        self.add_checkbox("_output_ntsc", (6, 1), pro=True)
        self.add_checkbox("_black_line_cut", (1, 2), pro=False)

        self.renderHeightBox.valueChanged.connect(
            lambda: self.set_current_frames(*self.get_current_video_frames())
        )
        self.openFile.clicked.connect(self.open_file)
        self.renderVideoButton.clicked.connect(self.render_video)
        self.saveImageButton.clicked.connect(self.render_image)
        self.stopRenderButton.clicked.connect(self.stop_render)
        self.compareModeButton.stateChanged.connect(self.toggle_compare_mode)
        self.toggleMainEffect.stateChanged.connect(self.toggle_main_effect)
        self.LossLessCheckBox.stateChanged.connect(self.lossless_exporting)
        # self.ProcessAudioCheckBox.stateChanged.connect(self.audio_filtering)
        self.pauseRenderButton.clicked.connect(self.toggle_pause_render)
        self.livePreviewCheckbox.stateChanged.connect(self.toggle_live_preview)
        self.refreshFrameButton.clicked.connect(self.nt_update_preview)
        self.openImageUrlButton.clicked.connect(self.open_image_by_url)
        self.exportImportConfigButton.clicked.connect(self.export_import_config)

        # TEMP HIDE WHILE FFPROBE ISSUE ISNT FIX
        # self.ProcessAudioCheckBox.hide()
        # Waiting for another branch

        self.ProMode.clicked.connect(
            lambda: self.set_pro_mode(self.ProMode.isChecked())
        )

        self.presetFromSeedButton.clicked.connect(self.update_preset_seed)
        presets = [18, 31, 38, 44]
        self.presetSeedSpinBox.setValue(presets[randint(0, len(presets) - 1)])
        self.update_preset_seed()


        self.noiseSeedSpinBox.valueChanged.connect(self.update_noise_seed)

        self.progressBar.setValue(0)
        self.progressBar.setMinimum(1)
        self.progressBar.hide()

        self.add_builtin_templates()

    def add_builtin_templates(self):

        try:
            # TODO: if online not available, then load from file (it need file to be included in build spec)
            res = requests.get('https://raw.githubusercontent.com/JargeZ/vhs/master/builtin_templates.json')
            if not res.ok:
                return
            self.templates = json.loads(res.content)
        except Exception as e:
            logger.exception(f'json not loaded: {e}')

        for name, values in self.templates.items():
            button = QPushButton()
            button.setText(name)
            set_values = (
                lambda v: lambda: self.nt_set_config(v)
            )(values)
            button.clicked.connect(set_values)
            self.templatesLayout.addWidget(button)

    def get_render_class(self):
        is_interlaced = False  # Get state from UI choice
        if is_interlaced:
            return InterlacedRenderer
        else:
            return DefaultRenderer

    def setup_renderer(self):
        try:
            self.update_status("Terminating prev renderer")
            logger.debug("Terminating prev renderer")
            self.render_thread.quit()
            self.update_status("Waiting prev renderer")
            logger.debug("Waiting prev renderer")
            self.render_thread.wait()
        except AttributeError:
            logger.debug("Setup first renderer")
        # создадим поток
        self.render_thread = QtCore.QThread()
        # создадим объект для выполнения кода в другом потоке
        RendererClass = self.get_render_class()
        self.videoRenderer = RendererClass()
        # перенесём объект в другой поток
        self.videoRenderer.moveToThread(self.render_thread)
        # после чего подключим все сигналы и слоты
        self.videoRenderer.newFrame.connect(self.render_preview)
        self.videoRenderer.frameMoved.connect(self.videoTrackSlider.setValue)
        self.videoRenderer.renderStateChanged.connect(self.set_render_state)
        self.videoRenderer.sendStatus.connect(self.update_status)
        self.videoRenderer.increment_progress.connect(self.increment_progress)
        # подключим сигнал старта потока к методу run у объекта, который должен выполнять код в другом потоке
        self.render_thread.started.connect(self.videoRenderer.run)

    @QtCore.pyqtSlot()
    def stop_render(self):
        self.videoRenderer.stop()

    @QtCore.pyqtSlot()
    def increment_progress(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

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

    @QtCore.pyqtSlot()
    def lossless_exporting(self):
        lossless_state = self.LossLessCheckBox.isChecked()

        self.lossless_mode = lossless_state
        try:
            self.videoRenderer.config['lossless'] = lossless_state
            logger.debug(f"Lossless: {str(lossless_state)}")
        except AttributeError:
            pass

    def audio_filtering(self):
        # state = self.ProcessAudioCheckBox.isChecked()
        state = False # Workaround
        self.ProcessAudio = state
        try:
            self.videoRenderer.config['audio_process'] = state
            logger.debug(f"Process audio: {str(state)}")
        except AttributeError:
            pass

    @QtCore.pyqtSlot()
    def update_preset_seed(self):
        self.nt = random_ntsc(self.presetSeedSpinBox.value())
        self.nt._enable_ringing2 = True
        self.sync_nt_to_sliders()

    @QtCore.pyqtSlot(int)
    def update_noise_seed(self):
        self.nt._noise_seed = self.noiseSeedSpinBox.value()
        self.nt_update_preview()

    @QtCore.pyqtSlot(str)
    def update_status(self, string):
        logger.info('[GUI STATUS] ' + string)
        self.statusLabel.setText(string)

    @QtCore.pyqtSlot(bool)
    def set_render_state(self, is_render_active):
        self.isRenderActive = is_render_active

        self.videoTrackSlider.blockSignals(is_render_active)

        self.openFile.setEnabled(not is_render_active)
        self.renderVideoButton.setEnabled(not is_render_active)
        self.stopRenderButton.setEnabled(is_render_active)

        # todo: сделать реассигн параметров во время рендера
        self.presetSeedSpinBox.setEnabled(not is_render_active)

        self.progressBar.setVisible(is_render_active)

        self.NearestUpScale.setEnabled(not is_render_active)

    def sync_nt_to_sliders(self):
        for parameter_name, control in self.nt_controls.items():
            value = getattr(self.nt, parameter_name)

            control.set_value(value, block_signals=True)
            logger.debug(f"set {type(value)} {parameter_name} {type(control).__name__} to {value}")
        self.nt_update_preview()

    def value_changed(self, parameter_name, value):
        logger.debug(f"Set {parameter_name} to {value}")
        setattr(self.nt, parameter_name, value)
        self.nt_update_preview()

    def add_checkbox(self, param_name, pos, pro=False):
        checkbox = CheckboxControl(param_name, self.strings[param_name], self.value_changed)
        self.nt_controls[param_name] = checkbox
        self.checkboxesLayout.addWidget(checkbox.checkbox, pos[0], pos[1])

        if pro:
            self.pro_mode_elements.append(checkbox)
            checkbox.set_visible(False)

    @QtCore.pyqtSlot(bool)
    def set_pro_mode(self, state):
        for frame in self.pro_mode_elements:
            frame.set_visible(state)

    def add_menu(self, param_name, values: List[Tuple[str, Any]], pro=False):
        menu = ComboBoxControl(param_name, self.strings[param_name], self.value_changed, values)
        self.nt_controls[param_name] = menu
        self.slidersLayout.addRow(menu.label, menu.box)

        if pro:
            self.pro_mode_elements.append(menu)
            menu.set_visible(False)

    def add_slider(self, param_name, min_val, max_val, slider_value_type: Union[Type[int], Type[float]] = int, pro=False):
        slider = SliderControl(
            param_name,
            self.strings[param_name],
            self.value_changed,
            min_val,
            max_val,
            slider_value_type
        )
        self.nt_controls[param_name] = slider
        self.slidersLayout.addRow(slider.label, slider.slider_frame)

        if pro:
            self.pro_mode_elements.append(slider)
            slider.set_visible(False)

    def get_current_video_frames(self):
        preview_h = self.renderHeightBox.value()
        if not self.input_video or preview_h < 10:
            return None, None
        frame_no = self.videoTrackSlider.value()
        self.input_video["cap"].set(1, frame_no)
        ret, frame1 = self.input_video["cap"].read()

        # Read next frame
        ret, frame2 = self.input_video["cap"].read()
        if not ret:
            frame2 = frame1

        return frame1, frame2

    def resize_to_preview_frame(self, frame):
        preview_h = self.renderHeightBox.value()
        try:
            crop_wh = resize_to_height(self.orig_wh, preview_h)
            frame = cv2.resize(frame, crop_wh)
        except ZeroDivisionError:
            self.update_status("ZeroDivisionError :DDDDDD")

        if frame.shape[1] % 4 != 0:
            frame = trim_to_4width(frame)

        return frame

    def set_current_frames(self, frame1: ndarray, frame2=None):

        current_frame_valid = isinstance(frame1, ndarray)
        preview_h = self.renderHeightBox.value()
        if not current_frame_valid or preview_h < 10:
            self.update_status("Trying to set invalid current frame")
            return None

        if frame2 is None:
            frame2 = frame1.copy()

        self.current_frame = self.resize_to_preview_frame(frame1)
        self.next_frame = self.resize_to_preview_frame(frame2)

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
        image_filters, video_filters = (
            " ".join(f"*{extension}" for extension in extension_list)
                for extension_list
                in (self.supported_image_type, self.supported_video_type)
        )
        filters = f"All supported files ({image_filters} {video_filters});;Images ({image_filters});;Videos ({video_filters});;All files (*)"
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", filter=filters)
        if file:
            path = Path(file[0])
        else:
            return None
        file_suffix = path.suffix.lower()
        if file_suffix in self.supported_video_type:
            self.set_video_mode()
            self.open_video(path)
        elif file_suffix in self.supported_image_type:
            img = cv2.imdecode(numpy.fromfile(path, dtype=numpy.uint8), cv2.IMREAD_COLOR)
            self.set_image_mode()
            self.open_image(img)
        else:
            self.update_status(f"Unsupported file type {file_suffix}")

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

    def set_render_heigth(self, height):
        if height > 600:
            self.renderHeightBox.setValue(600)
            self.update_status(
                self.tr('The image resolution is large. For the best effect, the output height is set to 600'))
        else:
            self.renderHeightBox.setValue(height // 120 * 120)

    def open_image(self, img: numpy.ndarray):
        self.setup_renderer()
        height, width, channels = img.shape
        self.orig_wh = width, height

        self.set_render_heigth(height)

        self.set_current_frames(img)

    def nt_get_config(self):
        values = {}
        for parameter_name, control in self.nt_controls.items():
            values[parameter_name] = control.get_value()

        return values

    def nt_set_config(self, values: Dict[str, Union[int, float]]):
        for parameter_name, value in values.items():
            setattr(self.nt, parameter_name, value)

        self.sync_nt_to_sliders()

    def open_video(self, path: Path):
        self.setup_renderer()
        logger.debug(f"file: {path}")
        cap = cv2.VideoCapture(str(path.resolve()))
        logger.debug(f"cap: {cap} isOpened: {cap.isOpened()}")
        self.input_video = {
            "cap": cap,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "frames_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "orig_fps": cap.get(cv2.CAP_PROP_FPS),
            "path": path,
            "suffix": path.suffix.lower(),
        }
        logger.debug(f"selfinput: {self.input_video}")
        self.orig_wh = (int(self.input_video["width"]), int(self.input_video["height"]))
        self.set_render_heigth(self.input_video["height"])
        self.set_current_frames(*self.get_current_video_frames())
        self.videoTrackSlider.setMinimum(1)
        self.videoTrackSlider.setMaximum(self.input_video["frames_count"])
        self.videoTrackSlider.valueChanged.connect(
            lambda: self.set_current_frames(*self.get_current_video_frames())
        )
        self.progressBar.setMaximum(self.input_video["frames_count"])

    def render_image(self):
        target_file = pick_save_file(self, title='Save frame as', suffix='.png')
        if target_file is None or not isinstance(self.current_frame, ndarray):
            return None
        render_h = self.renderHeightBox.value()
        crop_wh = resize_to_height(self.orig_wh, render_h)
        image = cv2.resize(self.current_frame, crop_wh)
        if image.shape[1] % 4 != 0:
            image = trim_to_4width(image)
        image = self.videoRenderer.apply_main_effect(self.nt, image, image, self.videoTrackSlider.value())
        is_success, im_buf_arr = cv2.imencode(".png", image)
        if not is_success:
            self.update_status("Error while saving (!is_success)")
            return None
        im_buf_arr.tofile(target_file)

    def render_video(self):
        if self.input_video['suffix'] == ".gif":
            suffix = self.input_video['suffix']
        else:
            suffix = '.mkv' if self.lossless_mode else '.mp4'
        target_file = pick_save_file(self, title='Render video as', suffix=suffix)
        if not target_file:
            return None
        render_data = {
            "target_file": target_file,
            "nt": self.nt,
            "input_video": self.input_video,
            "input_height": self.renderHeightBox.value(),
            "upscale_2x": self.NearestUpScale.isChecked(),
        }
        self.setup_renderer()
        self.toggle_main_effect()
        self.lossless_exporting()
        self.audio_filtering()
        self.progressBar.setValue(1)
        self.videoRenderer.render_data = render_data
        self.render_thread.start()

    def nt_update_preview(self):
        current_frame_valid = isinstance(self.current_frame, ndarray)
        render_on_pause = self.pauseRenderButton.isChecked()
        if not current_frame_valid or (self.isRenderActive and not render_on_pause):
            return None

        if not self.mainEffect:
            self.render_preview(self.current_frame)
            return None

        ntsc_out_image = self.videoRenderer.apply_main_effect(self.nt, self.current_frame, self.next_frame, self.videoTrackSlider.value())

        if self.compareMode:
            ntsc_out_image = numpy.concatenate(
                (self.current_frame[:self.current_frame.shape[0] // 2], ntsc_out_image[ntsc_out_image.shape[0] // 2:])
            )

        self.render_preview(ntsc_out_image)

    def export_import_config(self):
        config = self.nt_get_config()
        config_json = json.dumps(config, indent=2)

        dialog = ConfigDialog()
        dialog.configJsonTextField.setPlainText(config_json)
        dialog.configJsonTextField.selectAll()

        code = dialog.exec_()
        if code:
            config_json = dialog.configJsonTextField.toPlainText()
            config = json.loads(config_json)
            self.nt_set_config(config)

    @QtCore.pyqtSlot(object)
    def render_preview(self, img: ndarray):
        # https://stackoverflow.com/questions/41596940/qimage-skews-some-images-but-not-others

        height, width, _ = img.shape
        # calculate the total number of bytes in the frame
        totalBytes = img.nbytes
        # divide by the number of rows
        bytesPerLine = int(totalBytes / height)

        image = QtGui.QImage(img.tobytes(), width, height, bytesPerLine, QtGui.QImage.Format_RGB888) \
            .rgbSwapped()

        max_h = self.image_frame.height()
        if height > max_h:
            self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image).scaledToHeight(max_h))
        else:
            self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image))

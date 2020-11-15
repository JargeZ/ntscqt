from PyQt5 import QtWidgets, QtCore

from ui.DoubleSlider import DoubleSlider


class CustomSlider(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(CustomSlider, self).__init__(*args, **kwargs)
        self.slider = DoubleSlider(QtCore.Qt.Horizontal)
        self.numbox = QtWidgets.QDoubleSpinBox()
        self.numbox.setRange(self.slider.minimum(), self.slider.maximum())
        self.slider.valueChanged.connect(self.numbox.setValue)
        self.slider.rangeChanged.connect(self.numbox.setRange)
        self.numbox.valueChanged.connect(self.slider.setValue)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.numbox)
        layout.addWidget(self.slider)

    @QtCore.pyqtSlot(float)
    def setMinimum(self, minval):
        self.slider.setMinimum(minval)

    @QtCore.pyqtSlot(float)
    def setMaximum(self, maxval):
        self.slider.setMaximum(maxval)

    @QtCore.pyqtSlot(float, float)
    def setRange(self, minval, maxval):
        self.slider.setRange(minval, maxval)

    @QtCore.pyqtSlot(float)
    def setValue(self, value):
        self.slider.setValue(value)
    def value(self):
        self.slider.value()

    def setTickPosition(self, value):
        self.slider.setTickPosition(value)

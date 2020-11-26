from pathlib import Path

import numpy
from PyQt5.QtWidgets import QFileDialog


def resize_to_height(wh, target_h):
    w, h = wh
    k = target_h / h
    return int(w * k) // 2 * 2, target_h


def pick_save_file(self, title='Render As', pre_path='', suffix: str = None) -> Path:
    pick_filter = f"File {suffix} (*{suffix});;All Files (*)"
    target_file = QFileDialog.getSaveFileName(self, title, '', pick_filter)
    print(f"Save picked as: {target_file}")
    if not target_file[0]:
        return None

    path = Path(target_file[0])
    if path.suffix != suffix:
        path = path.parent / (path.name + suffix)

    return path


def trim_to_4width(img: numpy.ndarray) -> numpy.ndarray:
    """
    Workaround crash if image not divided by 4
    """
    height, width, channels = img.shape
    print(f"┃ Image wh: {width}x{height} w%4={width % 4}")
    if width % 4 != 0:
        img = img[:, :width % 4 * -1]
        height, width, channels = img.shape
        print(f"┗FIX to wh: {width}x{height} w%4={width % 4}")
    return img

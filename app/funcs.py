from pathlib import Path

import numpy
from PyQt5.QtWidgets import QFileDialog

from app.logs import logger


def resize_to_height(wh, target_h):
    w, h = wh
    k = target_h / h
    return int(w * k) // 2 * 2, target_h


def pick_save_file(self, title='Render As', pre_path='', suffix: str = None) -> Path:
    pick_filter = f"File {suffix} (*{suffix});;All Files (*)"
    target_file = QFileDialog.getSaveFileName(self, title, '', pick_filter)
    logger.debug(f"Save picked as: {target_file}")
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
    logger.debug(f"┃ Image wh: {width}x{height} w%4={width % 4}")
    if width % 4 != 0:
        img = img[:, :width % 4 * -1]
        height, width, channels = img.shape
        logger.debug(f"┗FIX to wh: {width}x{height} w%4={width % 4}")
    return img


def expand_to_4width(img: numpy.ndarray) -> numpy.ndarray:
    """
    Workaround crash if image not divided by 4
    """
    height, width, channels = img.shape
    logger.debug(f"┃ Image wh: {width}x{height} w%4={width % 4}")
    d = width % 4
    if d != 0:
        img = numpy.concatenate((img, img[:, -1:(d + 1) * -1:-1]), axis=1)
        height, width, channels = img.shape
        logger.debug(f"┗FIX to wh: {width}x{height} w%4={width % 4}")
    return img

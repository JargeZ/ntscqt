import os
import sys
from pathlib import Path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QLibraryInfo
from app.logs import logger
from app.NtscApp import NtscApp

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)


def crash_handler(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))
    exit(1)


# Install exception handler
sys.excepthook = crash_handler


def main():
    translator = QtCore.QTranslator()
    locale = QtCore.QLocale.system().name()

    # if run by pyinstaller executable, frozen attr will be true
    if getattr(sys, 'frozen', False):
        # _MEIPASS contain temp pyinstaller dir
        base_dir = Path(sys._MEIPASS)
        locale_file = str((base_dir / 'translate' / f'{locale}.qm').resolve())
    else:
        base_dir = Path(__file__).absolute().parent
        locale_file = str((base_dir / 'translate' / f'{locale}.qm').resolve())

    print(f"Try load {locale} locale: {locale_file}")
    if translator.load(locale_file):
        print(f'Localization loaded: {locale}')  # name, dir
    else:
        print("Using default translation")

    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    app.installTranslator(translator)

    window = NtscApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#!/usr/bin/env sh

case $1 in
"ui")
  echo updating ui py
  pyuic5 ui/mainWindow.ui -o ui/mainWindow.py
  pyuic5 ui/configExportDialog.ui -o ui/configExportDialog.py
  ;;
"translate")
  echo Updating translate file for lunguist
  pylupdate5 ui/mainWindow.py app/NtscApp.py ui/configExportDialog.py -ts translate/ru_RU.ts
  ;;
"build")
  if [ ! -f 'ffmpeg.exe' ]; then
    echo 'Downloading ffmpeg'
    echo 'windows x64'
    echo '  downloading from github.com'
    wget 'https://github.com/ShareX/FFmpeg/releases/download/v4.3.1/ffmpeg-4.3.1-win64.zip' -O "./win32-x64.zip"
    echo '  extracting'
    unzip -o -d . -j win32-x64.zip 'ffmpeg.exe'
    echo '  remove archive'
    rm win32-x64.zip
  fi
  docker run --entrypoint /bin/sh --rm -v "$(pwd):/src/" cdrx/pyinstaller-windows -c "python -m pip install --upgrade pip && /entrypoint.sh"
  ;;

esac


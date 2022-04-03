# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ntscQT.py'],
             pathex=['Z:\\src', 'c:\\Python37\\Lib\\site-packages\\cv2'],
             binaries=[
                ('c:\\Python37\\Lib\\site-packages\\cv2\\opencv_videoio_ffmpeg455_64.dll', '.'),
                ('ffmpeg.exe', '.')
             ],
             datas=[
                ('./app/ringPattern.npy', './app'),
                ('translate/*.qm', 'translate/'),
             ],
             hiddenimports=['scipy.special.cython_special', 'scipy.spatial.transform._rotation_groups', 'app'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ntscQT',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          icon='Z:\\src\\ntscqt_icon.ico',
          runtime_tmpdir=None,
          console=False )

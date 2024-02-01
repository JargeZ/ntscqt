# [<img src="https://github.com/JargeZ/ntscqt/blob/master/docs/img/ntscqt_banner.png?raw=true">](https://0hz.ru/ntscqt/)

<div align="center">
   
[![Downloads](https://img.shields.io/github/downloads/JargeZ/ntscqt/total?style=for-the-badge&color=blue)](https://github.com/JargeZ/ntscqt/releases/latest)
[![Website](https://img.shields.io/badge/-WEBSITE-blue?label=&style=for-the-badge)](https://0hz.ru/ntscqt/)

<!---
[![Release version](https://img.shields.io/github/v/release/JargeZ/ntscqt?color=blue&label=&style=for-the-badge)](https://github.com/JargeZ/ntscqt/releases/latest)
[![Commits](https://img.shields.io/github/commit-activity/m/JargeZ/ntscqt?label=commits&style=for-the-badge)](https://github.com/JargeZ/ntscqt/commits)
[![Last Commit](https://img.shields.io/github/last-commit/JargeZ/ntscqt/master?label=&style=for-the-badge)](https://github.com/JargeZ/ntscqt/commits)
-->

</div>

## Alternatives
Thank you, everyone, so many stars 🌟 and uses are very much appreciated.\
Nowadays this project has the latest working release, but will not be supported further
- [NTSC-RS](https://github.com/valadaptive/ntsc-rs) is one of the promising ones, the algorithm is implemented in Rust and should be faster\
  and [there are OpenFX or After Effects plugins available](https://github.com/valadaptive/ntsc-rs/releases)
- [NtscQT+](https://github.com/rgm89git/ntscQTplus) is a fork modification of the current version
- [valadaptive/ntscqt](https://github.com/valadaptive/ntscqt) is fork with fixes in current version
- The Signal plugin for AE also exists, though it's a paid and quite expensive one. It's based on the same algorithm.\
  Its complete replacement is [ntsc-rs-windows-afterfx.zip](https://github.com/valadaptive/ntsc-rs/releases)
  
You can also use [current version](https://github.com/JargeZ/ntscqt/releases/tag/v1.5.0) if it suits your purpose.



[![Demo](demo.gif)](https://youtu.be/uqT3Z0kfF24)
![example](https://i.imgur.com/nn92Jmp.jpg)

<div align="center">

## Complete guide by Jonah Longoria
[<img alt="Jonah Longoria s guide" src="https://i.imgur.com/ERBwB7N.png" height="257">](https://youtu.be/O9jpc5rySUI)

## Demo:
[<img alt="Tutorial by Skittleology" src="https://i.imgur.com/5vJ3Pdb.png" height="157">](https://youtu.be/hV9IoedRe7I)
[<img alt="GiyuGamer556 Comparing" src="https://i.imgur.com/gVBgqkO.png" height="157">](https://youtu.be/S6Qn-_wWuMc)


[<img alt="Jack demo" src="https://i.imgur.com/G2Lpqqt.png" height="157">](https://youtu.be/M7vZqABy85M)

[<img alt="Program interface" src="https://i.imgur.com/BXLqOMN.png" height="157">](https://youtu.be/uqT3Z0kfF24)
[<img src="https://i.imgur.com/BiPpjoD.png" height="157">](https://youtu.be/Jr7Jmn81WNQ)
[<img alt="Satyr video intro" src="https://sun9-13.userapi.com/impg/8OTpTqANlgy5K5nXWTXfMomyOVi9ljtmxUb7EQ/GmzqXzWO-GM.jpg?size=1098x776&quality=96&sign=c286b8766606af183a5291765e32c21d&type=album" height="157">](https://youtu.be/TMZathtFWM8?t=377)
[<img alt="YT Demo" src="https://i.imgur.com/cDRA96Q.png" height="140">](https://youtu.be/FPcTfAHiPyw)
[<img alt="YT Demo" src="https://i.imgur.com/PmhceT6.jpg" height="140">](https://youtu.be/k5l16rJfh-8)
[<img alt="YT Demo" src="https://i.imgur.com/Xy5Cex9.png" height="140">](https://youtu.be/vjvISSdGYv0)
[<img alt="YT Demo" src="https://i.imgur.com/i5FxlYU.jpg" height="140">](https://youtu.be/ctMSn--04Sk)

</div>

<div align="center">

### Download:
[<img src="https://img.shields.io/github/downloads/JargeZ/ntscqt/latest/total?label=DOWNLOAD%20THE%20LATEST%20VERSION&style=for-the-badge" height="40">](https://github.com/JargeZ/ntsc/releases/latest/download/ntscQT.exe)

You can [download latest version here](https://github.com/JargeZ/ntsc/releases/latest/download/ntscQT.exe) or from [releases page](https://github.com/JargeZ/ntsc/releases)

</div>

### Compiling:

#### Requisites:
Python *(on moment, until Python 3.9, Python 3.10+ support will be on development)*

#### For Windows:
1. Open your terminal of preference.
2. If not already installed, install Chocolatey: [chocolatey.org](https://chocolatey.org/)
3. Install ffmpeg *(necessary)*:
   ```powershell
   choco install ffmpeg
   ```
4. Install ntscQT:
    ```powershell
    git clone https://github.com/JargeZ/ntscqt -C ntscqt
    cd ntscqt
    python -m venv ./venv
    ./venv/Scripts/activate
    pip install -r requirements.txt
    ```
5. After that you can test run by command `python ntscQT.py`
6. After exit and subsequent times, you should run app by entering the following command:
   ```powershell
   cd ntscqt && ./venv/Scripts/activate && python ntscQT.py
   ```

#### For Mac OS X and Linux distributions:
Thanks for [Robot Riot Records](https://linktr.ee/robotriot) for donation which motivated to make MacOS fixes
1. Open your terminal of preference.
2. **For Mac OS users:** If not already installed, install Homebrew: [brew.sh](https://brew.sh/)
3. Install ffmpeg *(necessary)*:
   ```bash
   brew install ffmpeg # For Linux users: use package manager of distribution you're using to download and install FFmpeg
      # --- LINUX SPECIFIC PACKAGES ---
   sudo apt install libxcb-xinerama0 # use package manager of distribution you're using to download and install this list of packages
   ```
4. Install ntscQT:
    ```bash
    git clone https://github.com/JargeZ/vhs ~/ntscqt
    cd ~/ntscqt
    python3 -m venv ./venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
5. After that you can test run by command `python ntscQT.py`
6. After exit and subsequent times, you should run app by entering the following command:
   ```bash
   cd ~/ntscqt && venv/bin/python ntscQT.py
   ```

#### For Mac on M1 Apple Silicon try this:
```bash
brew install pyqt@5
git clone https://github.com/JargeZ/vhs ~/ntscqt
cd ~/ntscqt
python3 -m venv ./venv
cp -R /opt/homebrew/Cellar/pyqt@5/5.15.6/lib/python3.9/site-packages/* ./venv/lib/python3.9/site-packages/
source venv/bin/activate
pip install --pre -i https://pypi.anaconda.org/scipy-wheels-nightly/simple scipy
pip install --ignore-installed -r requirements.m1-temp.txt
venv/bin/python ntscQT.py
```

### About installation process on Termux 
At this moment ntscqt **is not supported on Termux even with proot-distro utility.** Maybe ntscqt is runnable on Termux but **there is no method to make it work.**

### What It Is
Эта простая программа сделана на основе алгоритма, который позволяет добиться эффекта реального старого магнитофона или VHS, а не простое размытие и шумы со статическими эффектами, как на многих видео simpsonwave и подобных. Я надеюсь, что этот инструмент поможет вам в творчестве, если вы решите стилизовать картинки или видео под старинные кадры.
<hr>
This simple program is made on the basis of an algorithm that allows you to achieve the effect of a real old tape recorder or VHS, rather than simple blur and noise with static effects, as in many simpsonwave videos and the like. I hope this tool will help you in your creative work if you decide to stylize pictures or videos to look like old video.

## Warning
Если вам нужно обработать только какую-то часть видео, сначала вырежьте её через видеоредактор, где вы работаете и пропустите через программу только этот кусок.\
В программе есть возможность выключить применение эффекта во время рендера и включить только в нужный момент, но это всё равно будет дольше, чем заранее подготовить нужный кусок.

`This code is *SLOW*. It's designed to be as accurate as I can make it, not fast. You may want to take any Simpsons episodes you will be editing and cut them up first in Adobe Premiere (or your favorite video editor) then run the exported "clip show" through this program instead of wasting CPU cycles on whole episodes.`

`Этот код *ОЧЕНЬ МЕДЛЕННЫЙ*. Он был разработан настолько точным, насколько насколько было возможно, но он медленный. Возможно, вам будет лучше взять, напримре, какую-то серию Симпсонов, которую Вы хотите отредактировать и вырезать из неё нужный фрагмент в Adobe Premiere (или в Вашем любимом редакторе), а затем пропустить экспортированный клип через эту программу вместо того, чтобы тратить мощности процессора на целый эпизод.`

# Использование (RU)
Откройте видео и играйтесь ползунками
- Поле с номером **Seed** генерирует случайные параметры обработки, которые всегда будут одинаковы для одной и той же цифры
- **Preview height** указывает размер кадра, который обрабатывается для предпросмотра. Меньше - быстрее.
- **Render height** изначально становится такой, как у видео, которое вы загрузили. Если установить значение меньше, то при рендере входное видео будет ресайзиться и обработается быстрее
- **Pause Render** позволяет поставить рендер на паузу и изменить параметры обработки, чтобы достичь изменяемого эффекта в видео. Также ползунки можно крутить прямо во время рендера без паузы.
- **LivePreview** можно включить во время рендера, тогда в окне предпросмотра будет показываться каждый обрабатываемся кадр, тогда как изанчально только каждый 10-й
- **Кнопка :arrows_counterclockwise:** рендерит заново текущий кадр с наложенным эффектом
# Usage (EN)
You can open the video and experiment with all parameters
- **Seed** field generates random processing parameters that will always be the same for the same value
- **Preview height** indicates the size of the frame that is processed for preview. Less is faster.
- The **Render height** initially becomes the same as the video you uploaded. If you set the value less, the video will be resized and processed faster
- **Pause Render** allows you to pause the render and change the processing parameters to achieve a variable effect in the video. Also, the sliders can be turned directly during rendering without pause.
- **LivePreview** can be turned on during rendering, then every frame being processed will be shown in the preview window, default only every 10th frame shown
- **:arrows_counterclockwise: button** re-render the current frame effect
- - -
> You can find more info there [/releases](https://github.com/JargeZ/ntsc/releases)\
> Подробности есть по ссылке [/releases](https://github.com/JargeZ/ntsc/releases)
# Presets
<p align="center"><a href="https://github.com/rgm89git/rgms-ntscqt-presets">RGM's ntscQT presets <i>(by RGM)</i></a></p>

#### <p align="center">AKA `Line maker 10.0`</p>
- - -
#
##### Original README (оригинальное описание)
#### NTSC video emulator
![alt text](https://github.com/zhuker/ntsc/raw/master/ntsc.gif)

This is a python3.6 rewrite of https://github.com/joncampbell123/composite-video-simulator
intended for use in analog artifact removal neural networks but can also be used for artistic purposes

The ultimate goal is to reproduce all of the artifacts described here
https://bavc.github.io/avaa/tags.html#video

At this point simulated artifacts include 

# Dot crawl
A composite video artifact, dot crawl occurs as a result of the multiplexing of luminance and chrominance information carried in the signal. Baseband NTSC signals carry these components as different frequencies, but when they are displayed together, the chroma information can be misinterpreted as luma. The result is the appearance of a moving line of beady dots. It is most apparent on horizontal borders between objects with high levels of saturation. Using a comb filter to process the video can reduce the distraction caused by dot crawl when migrating composite video sources, and the artifact may be eliminated through the use of s-video or component connections. However, if it is present in an original source transfer, it might be compounded in subsequent generations of composite video transfers.

![alt text](https://github.com/zhuker/ntsc/raw/master/DotCrawl_Flat.jpg)

# Ringing
In a general sense, ringing refers to an undesirable oscillation exhibited in a signal. This video artifact is common to recordings created using less sophisticated, early model cameras and VTR equipment (particularly early U-matic equipment). It can be accentuated by over-enhancement or sharpening of the image using processing hardware or CRT monitor controls. When recorded in the signal on tape, it becomes part of the image.
![a](https://github.com/zhuker/ntsc/raw/master/Ringing1_Flat.jpg)
![a](https://github.com/zhuker/ntsc/raw/master/Ringing2_Flat.jpg)


# Chroma/Luma Delay Error aka Color Bleeding

When video suffers from Y/C delay error, there will be a mismatch in the timing among the luminance and/or color channels, with resulting visible misalignment in how colors appear in the monitor. A misalignment of Y/C shows a blurry edge around areas with high contrast color difference, and will be most apparent around sharp edges of objects in the video image.
![](https://github.com/zhuker/ntsc/raw/master/YCDelayError_Flat.jpg)
 

# Rainbow effects
Rainbow effects and dot crawls are caused by imperfect separation of the luma and chroma components of a composite video signal. This effect is called color crosstalk. It is most noticeable on computer generated images like subtitles, weather maps, stationary logos and video images where you have hi-frequency data (like the shot of a skyscraper in the distance). Whenever you have strong alternating, fine patterns (= high frequencies) in luma, you have rainbow effects. Whenever you have a sudden, big change in chroma (typically computer generated graphics etc.), you have dot crawls. The technical terms are as follows: rainbow effects is cross color (hi-frequency luma data upsets the chroma demodulator) and dot crawl is cross luminance (chroma leftovers in the Y signal).

![](https://github.com/zhuker/ntsc/raw/master/rainbow5.jpg)


# Chrominance Noise
Chrominance noise can be identified as traces and specks of color in an otherwise clear picture. It is most visible in dark, saturated areas of the video image. It can be due to limitations of CCD sensitivity in video cameras (i.e., low-lighting conditions during camera recording), over-boosting of chrominance in the video signal, or the use of poor video processors. Multi-generation composite dubs may suffer from high levels of chrominance noise.
![alt text](https://github.com/zhuker/ntsc/raw/master/ChromaNoise_Flat.jpg)

# Head Switching Noise
Head switching noise is commonly seen at the bottom of video display during VHS playback. Although it occurs in other formats, it is often masked depending on the processing features and calibration of the playback VTR. During playback of videotape, video heads are turned on as they pass over the media and then turned off to prevent the display of noise that would be output when they are not in contact with the tape. Head switching noise is a result of that switching interval, and it occurs prior to the start of vertical sync. This artifact is not viewable in overscan on a broadcast monitor, but it is viewable in underscan and in full-raster digitized video and un-cropped digital derivatives. Some VTRs feature “SWP masking”, which effectively masks the lines created during head switching with video black.
![alt text](https://github.com/zhuker/ntsc/raw/master/HeadSwitch_Butterfly_SLV-779HF_Sharp1_XCard.jpg)

# Long/Extended Play
Long Play (LP) mode, available for a variety of video formats (see list below), makes it possible to extend the potential recording time of a tape by lowering the tape speed and changing the angle and proximity of the recorded tracks. For proper playback, a recording made in LP mode must be played back in LP mode.

If played back in Standard Play (SP) mode, the image is still recognisable, but—depending on the format—may be played back between 1.5x and 2x too fast, displaying irregular, horizontal, bands of noise similar to those that appear when fast-forwarding. Audio on the longitudinal track will sound too high-pitched, and will be played back so fast that the speech sounds incomprehensible. If FM or PCM audio is recorded on the helical tracks, it will drop out completely.
LP mode was effectively replaced with EP (“extended play”) or SLP (“super long play”). Often referred to together as “EP/SLP”, this mode involves tape speed 3x slower than standard play speeds.

In cases where the tape speed is slowed to economize on media usage, less information is recorded for a given image, resulting in noticeably reduced picture quality. Generally speaking, when tape speed is reduced, any other condition afflicting the tape, such as stiction or stretching, is further exacerbated.

# Luminance Noise
Luminance noise manifests itself in a video picture as light white noise. It may be the result of electronic failure, recording in low-light, worn or poorly coated tape stock, transmission of a video signal over cables that are too long, over-enhancement of the video signal, or dirty record or playback heads. Color video or black and white video can both contain luminance noise.

# OVERSATURATION
Oversaturation refers to high chrominance amplitude in a video signal, creating the appearance of very intense color in the image. Depending on severity of oversaturation, color in the image may appear to bleed into areas outside of an object’s apparent boundaries. Most NTSC broadcast standards require that the composite video signal not exceed 120 IRE (flat). SMPTE split field color bars use 75% saturation as the maximum value for calibration, although there are other patterns used for testing which contain 100% saturation values.

![a](https://github.com/zhuker/ntsc/raw/master/Oversaturated_Flat.jpg)


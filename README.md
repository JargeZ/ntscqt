# NTSC video emulator

![alt text](ntsc.gif)

This is a python3.6 rewrite of https://github.com/joncampbell123/composite-video-simulator
intended for use in analog artifact removal neural networks but can also be used for artistic purposes

The ultimate goal is to reproduce all of the artifacts described here
https://bavc.github.io/avaa/tags.html#video

At this point simulated artifacts include 

# Dot crawl
A composite video artifact, dot crawl occurs as a result of the multiplexing of luminance and chrominance information carried in the signal. Baseband NTSC signals carry these components as different frequencies, but when they are displayed together, the chroma information can be misinterpreted as luma. The result is the appearance of a moving line of beady dots. It is most apparent on horizontal borders between objects with high levels of saturation. Using a comb filter to process the video can reduce the distraction caused by dot crawl when migrating composite video sources, and the artifact may be eliminated through the use of s-video or component connections. However, if it is present in an original source transfer, it might be compounded in subsequent generations of composite video transfers.

![alt text](DotCrawl_Flat.jpg)

# Ringing
In a general sense, ringing refers to an undesirable oscillation exhibited in a signal. This video artifact is common to recordings created using less sophisticated, early model cameras and VTR equipment (particularly early U-matic equipment). It can be accentuated by over-enhancement or sharpening of the image using processing hardware or CRT monitor controls. When recorded in the signal on tape, it becomes part of the image.
![a](Ringing1_Flat.jpg)
![a](Ringing2_Flat.jpg)


# Chroma/Luma Delay Error aka Color Bleeding

When video suffers from Y/C delay error, there will be a mismatch in the timing among the luminance and/or color channels, with resulting visible misalignment in how colors appear in the monitor. A misalignment of Y/C shows a blurry edge around areas with high contrast color difference, and will be most apparent around sharp edges of objects in the video image.
![](YCDelayError_Flat.jpg)
 

# Rainbow effects
Rainbow effects and dot crawls are caused by imperfect separation of the luma and chroma components of a composite video signal. This effect is called color crosstalk. It is most noticeable on computer generated images like subtitles, weather maps, stationary logos and video images where you have hi-frequency data (like the shot of a skyscraper in the distance). Whenever you have strong alternating, fine patterns (= high frequencies) in luma, you have rainbow effects. Whenever you have a sudden, big change in chroma (typically computer generated graphics etc.), you have dot crawls. The technical terms are as follows: rainbow effects is cross color (hi-frequency luma data upsets the chroma demodulator) and dot crawl is cross luminance (chroma leftovers in the Y signal).

![](rainbow5.jpg)


# Chrominance Noise
Chrominance noise can be identified as traces and specks of color in an otherwise clear picture. It is most visible in dark, saturated areas of the video image. It can be due to limitations of CCD sensitivity in video cameras (i.e., low-lighting conditions during camera recording), over-boosting of chrominance in the video signal, or the use of poor video processors. Multi-generation composite dubs may suffer from high levels of chrominance noise.
![alt text](ChromaNoise_Flat.jpg)

# Head Switching Noise
Head switching noise is commonly seen at the bottom of video display during VHS playback. Although it occurs in other formats, it is often masked depending on the processing features and calibration of the playback VTR. During playback of videotape, video heads are turned on as they pass over the media and then turned off to prevent the display of noise that would be output when they are not in contact with the tape. Head switching noise is a result of that switching interval, and it occurs prior to the start of vertical sync. This artifact is not viewable in overscan on a broadcast monitor, but it is viewable in underscan and in full-raster digitized video and un-cropped digital derivatives. Some VTRs feature “SWP masking”, which effectively masks the lines created during head switching with video black.
![alt text](HeadSwitch_Butterfly_SLV-779HF_Sharp1_XCard.jpg)

# Long/Extended Play
Long Play (LP) mode, available for a variety of video formats (see list below), makes it possible to extend the potential recording time of a tape by lowering the tape speed and changing the angle and proximity of the recorded tracks. For proper playback, a recording made in LP mode must be played back in LP mode.

If played back in Standard Play (SP) mode, the image is still recognisable, but—depending on the format—may be played back between 1.5x and 2x too fast, displaying irregular, horizontal, bands of noise similar to those that appear when fast-forwarding. Audio on the longitudinal track will sound too high-pitched, and will be played back so fast that the speech sounds incomprehensible. If FM or PCM audio is recorded on the helical tracks, it will drop out completely.
LP mode was effectively replaced with EP (“extended play”) or SLP (“super long play”). Often referred to together as “EP/SLP”, this mode involves tape speed 3x slower than standard play speeds.

In cases where the tape speed is slowed to economize on media usage, less information is recorded for a given image, resulting in noticeably reduced picture quality. Generally speaking, when tape speed is reduced, any other condition afflicting the tape, such as stiction or stretching, is further exacerbated.

# Luminance Noise
Luminance noise manifests itself in a video picture as light white noise. It may be the result of electronic failure, recording in low-light, worn or poorly coated tape stock, transmission of a video signal over cables that are too long, over-enhancement of the video signal, or dirty record or playback heads. Color video or black and white video can both contain luminance noise.

# OVERSATURATION
Oversaturation refers to high chrominance amplitude in a video signal, creating the appearance of very intense color in the image. Depending on severity of oversaturation, color in the image may appear to bleed into areas outside of an object’s apparent boundaries. Most NTSC broadcast standards require that the composite video signal not exceed 120 IRE (flat). SMPTE split field color bars use 75% saturation as the maximum value for calibration, although there are other patterns used for testing which contain 100% saturation values.

![a](Oversaturated_Flat.jpg)


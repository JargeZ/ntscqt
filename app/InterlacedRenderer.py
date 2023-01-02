import cv2
from app.Renderer import DefaultRenderer
from app.ntsc import Ntsc


class InterlacedRenderer(DefaultRenderer):
    @staticmethod
    def apply_main_effect(nt: Ntsc, frame1, frame2=None):
        if frame2 is None:
            frame2 = frame1

        frame1 = nt.composite_layer(frame1, frame1, field=0, fieldno=0)
        frame1 = cv2.convertScaleAbs(frame1)
        frame2 = nt.composite_layer(frame2, frame2, field=2, fieldno=1)
        frame2 = cv2.convertScaleAbs(frame2)

        # import numpy as np
        # debug1 = np.concatenate((frame1.copy(), frame2), axis=1)
        # debug2 = np.concatenate((frame1[0:-2:2], frame2[2::2]), axis=1)
        # frame1[1:-1:2] = frame1[0:-2:2] / 2 + frame2[2::2] / 2
        # debug3 = np.concatenate(
        #     (
        #         frame1,
        #         frame1
        #     ), axis=1)
        #
        # debug = cv2.vconcat((debug1, debug2, debug3))
        # return debug
        # TODO: Ensure, that we combine
        #      N         N+1      RESULT
        #  [A, A, A]  [b, b, b]  [A, A, A]
        #  [A, A, A]  [b, b, b]  [b, b, b]
        #  [A, A, A]  [b, b, b]  [A, A, A]
        #  for now im not sure in field and fieldno behaviour

        frame1[1:-1:2] = frame1[0:-2:2] / 2 + frame2[2::2] / 2
        return frame1

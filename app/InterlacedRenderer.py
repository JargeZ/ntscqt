from app.Renderer import DefaultRenderer
from app.ntsc import Ntsc


class InterlacedRenderer(DefaultRenderer):
    @staticmethod
    def apply_main_effect(nt: Ntsc, frame1, frame2=None):
        raise NotImplementedError()
        # TODO: RGM
        return frame

#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Parameter evaluators"""

from ros3ddevcontroller.param.parameter import Evaluator
import math

class DofHelperCalc(Evaluator):

    REQUIRES = [
        'focus_distance_m',
        'focal_length_mm',
        'aperture',
        'coc_um',
        'frame_width_px',
        'sensor_width_px'
    ]

    @staticmethod
    def calc_h_hs(coc_um=None, focus_distance_m=None, aperture=None,
                  frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        coc_mm = coc_um / 1000.
        ratio = frame_width_px / sensor_width_px
        h = 0.001 * (focal_length_mm * focal_length_mm) / (coc_mm * ratio * aperture)
        hs = h * focus_distance_m

        return h, hs


class DofNearCalc(DofHelperCalc):

    def __call__(self, coc_um=None, focus_distance_m=None, aperture=None,
                 frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        if coc_um == 0:
            return focus_distance_m

        h, hs = DofHelperCalc.calc_h_hs(coc_um, focus_distance_m, aperture,
                                        frame_width_px, sensor_width_px, focal_length_mm)

        if focus_distance_m == float('inf'):
            return h

        near = hs / (h + focus_distance_m)
        return near


class DofFarCalc(DofHelperCalc):

    def __call__(self, coc_um=None, focus_distance_m=None, aperture=None,
                 frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        if coc_um == 0:
            return focus_distance_m

        if focus_distance_m == float('inf'):
            return float('inf')

        h, hs = DofHelperCalc.calc_h_hs(coc_um, focus_distance_m, aperture,
                                        frame_width_px, sensor_width_px, focal_length_mm)
        far = float('inf') if focus_distance_m >= h else (hs / (h - focus_distance_m))
        return far


class DofTotalCalc(Evaluator):

    REQUIRES = [
        'dof_near_m',
        'dof_far_m'
    ]

    def __call__(self, dof_near_m=None, dof_far_m=None):
        return dof_far_m - dof_near_m

class FovHorizontalDegCalc(Evaluator):
    pass


class FovVerticalDegCalc(Evaluator):
    pass


class FovDiagonalDegCalc(Evaluator):
    pass


class ConvergenceDegCalc(Evaluator):

    REQUIRES = [
        'baseline_mm',
        'distance_screen_m'
    ]

    def __call__(self, baseline_mm=None, distance_screen_m=None):
        return 2 * math.degrees(math.atan((baseline_mm / 2) / distance_screen_m))


class ConvergencePxCalc(Evaluator):

    REQUIRES = [
        'frame_width_px',
        'baseline_mm',
        'distance_screen_m',
        'frame_width_mm',
        'focal_length_mm'
    ]

    def __call__(self, frame_width_px=None, baseline_mm=None, distance_screen_m=None,
                 frame_width_mm=None, focal_length_mm=None):
        return frame_width_px * math.atan(baseline_mm / (2 * 1000 * distance_screen_m))  / math.atan(frame_width_mm / (2 * focal_length_mm))


class ParallaxPercentHelperCalc(Evaluator):

    REQUIRES = [
        'baseline_mm',
        'focal_length_mm',
        'frame_width_mm',
        'distance_screen_m'
    ]

    @staticmethod
    def calc_parallax_percent(baseline_mm, focal_length_mm, frame_width_mm,
                              distance_screen_m, distance):

        return 100 * (baseline_mm * focal_length_mm) / frame_width_mm * (1 / (1000 * distance_screen_m) - 1 / (1000 * distance))


class ParallaxNearPercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_near_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_near_m=None):

        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_near_m)


class ParallaxScreenPercentCalc(Evaluator):
    pass


class ParallaxFarPercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_far_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_far_m=None):
        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_far_m)


class ParallaxObject1PercentCalc(Evaluator):
    pass


class ParallaxObject2PercentCalc(Evaluator):
    pass


class ParallaxNearMMCalc(Evaluator):
    pass


class ParallaxFarMMCalc(Evaluator):
    pass


class ParallaxObject1MMCalc(Evaluator):
    pass


class ParallaxObject2MMCalc(Evaluator):
    pass


class RealWidthNearCalc(Evaluator):
    pass


class RealHeightNearCalc(Evaluator):
    pass


class RealWidthScreenCalc(Evaluator):
    pass


class RealHeightScreenCalc(Evaluator):
    pass


class RealWidthFarCalc(Evaluator):
    pass


class RealHeightFarCalc(Evaluator):
    pass


class RealHeightObject1Calc(Evaluator):
    pass


class RealWidthObject1Calc(Evaluator):
    pass


class RealWidthObject2Calc(Evaluator):
    pass


class RealHeightObject2Calc(Evaluator):
    pass


class FrameWidthMMCalc(Evaluator):
    pass


class FrameDiagonalMMCalc(Evaluator):
    pass


class FrameHorizontalCropCalc(Evaluator):
    pass


class FrameVerticalCropCalc(Evaluator):
    pass


class FrameDiagonalCropCalc(Evaluator):
    pass


class CocUmCalc(Evaluator):
    pass


class ScreenDistanceCalc(Evaluator):
    pass


class SpectatorFovHorizontalDegCalc(Evaluator):
    pass


class PerceivedPositionNearPercCalc(Evaluator):
    pass


class PerceivedPositionScreenPercCalc(Evaluator):
    pass


class PerceivedPositionFarPercCalc(Evaluator):
    pass


class PerceivedPositionObject1PercCalc(Evaluator):
    pass


class PerceivedPositionObject2PercCalc(Evaluator):
    pass


class PerceivedPositionNearMCalc(Evaluator):
    pass


class PerceivedPositionScreenMCalc(Evaluator):
    pass


class PerceivedPositionFarMCalc(Evaluator):
    pass


class PerceivedPositionObject1MCalc(Evaluator):
    pass


class PerceivedPositionObject2MCalc(Evaluator):
    pass


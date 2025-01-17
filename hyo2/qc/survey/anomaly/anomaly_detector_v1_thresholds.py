import numpy as np
import time
from scipy.ndimage import gaussian_filter
from matplotlib import pyplot as plt
import logging

from hyo2.qc.survey.anomaly.anomaly_detector_v1_proxies import calc_proxies

logger = logging.getLogger(__name__)


class ThresholdsV1:

    @classmethod
    def nan_gaussian_filter(cls, arr, sigma=5.0, mode="nearest", cval=0):
        v = arr.copy()
        v[np.isnan(arr)] = 0
        vv = gaussian_filter(v, sigma=sigma, mode=mode, cval=cval)

        w = 0 * arr.copy() + 1
        w[np.isnan(arr)] = 0
        ww = gaussian_filter(w, sigma=sigma, mode=mode, cval=cval)

        return vv / ww

    def __init__(self):

        self._array = None
        self.filter_radius = 3
        # self.mask = None
        self.median = None
        self.nmad = None
        self.std_gauss_curv = None
        self.th_height = None
        self.th_gauss_curv = None

    def calculate(self, array: np.ndarray):
        logger.info("calculation ...")

        if array.dtype == np.float32:
            logger.debug("converting to double")
            self._array = array.astype(np.float64)
        else:
            self._array = array

        # def nan_median(arr):
        #     with np.warnings.catch_warnings():
        #         np.warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        #
        #         return np.nanmedian(arr)
        #
        # def nan_mad(arr):
        #     # with np.warnings.catch_warnings():
        #     # np.warnings.filterwarnings('ignore', r'Mean of empty slice')
        #
        #     arr = np.ma.masked_invalid(arr).compressed()
        #     if arr.size == 0:
        #         return np.nan
        #     dtm_mean = np.mean(arr)
        #     dtm_std = np.std(arr)
        #     dtm_mad = abs(np.nanmedian(arr) - dtm_mean)  # median absolute deviation to measure the data variability
        #     # logger.debug("arr:\n%s %s %s" % (arr, dtm_mad, dtm_std))
        #     return dtm_mad / dtm_std
        #
        # def nan_std_gauss_curv(arr):
        #     # logger.debug("%s" % arr)
        #     arr = np.ma.masked_invalid(arr).reshape(self.filter_size, self.filter_size)  # .compressed()
        #     # logger.debug("%s" % arr)
        #     gy, gx = np.gradient(arr)
        #     # logger.debug("arr:\n%s" % arr)
        #     # logger.debug("gx:\n%s" % gx)
        #     # exit()
        #     gxy, gxx = np.gradient(gx)
        #     gyy, _ = np.gradient(gy)
        #     gauss_curv = (gxx * gyy - (gxy ** 2)) / (1 + (gx ** 2) + (gy ** 2)) ** 2
        #     if gauss_curv.mask.all():
        #         return np.nan
        #     return np.std(gauss_curv)

        # self.mask = self._array[self._array == np.nan]

        # start_time = time.time()
        # self.median = ndimage.generic_filter(array, nan_median,
        #                                      size=(self.filter_size, self.filter_size),
        #                                      mode="constant", cval=np.nan)
        # self.nmad = ndimage.generic_filter(array, nan_mad,
        #                                    size=(self.filter_size, self.filter_size),
        #                                    mode="constant", cval=np.nan)
        # self.std_gauss_curv = ndimage.generic_filter(array, nan_std_gauss_curv,
        #                                              size=(self.filter_size, self.filter_size),
        #                                              mode="constant", cval=np.nan)
        # logger.info("calculation: OK (time: %.3f s)" % (time.time() - start_time, ))

        start_time = time.time()
        self.median = np.empty_like(self._array)
        self.nmad = np.empty_like(self._array)
        self.std_gauss_curv = np.empty_like(self._array)
        self.th_height = np.empty_like(self._array)
        self.th_gauss_curv = np.empty_like(self._array)
        # logger.debug("input proxies dtypes: %s" % self._array.dtype)
        calc_proxies(self._array,
                     self.median, self.nmad, self.std_gauss_curv,
                     self.th_height, self.th_gauss_curv,
                     self.filter_radius)
        logger.info("calculation: OK (time: %.3f s)" % (time.time() - start_time,))

        self.th_height = self.nan_gaussian_filter(self.th_height)
        self.th_gauss_curv = self.nan_gaussian_filter(self.th_gauss_curv)

        # self._calc_thresholds()

    # def _calc_thresholds(self):
    #     logger.info("thresholds calculation ...")
    #     start_time = time.time()
    #
    #     self.th_height = np.ones_like(self.median) * np.nan
    #     self.th_gauss_curv = np.ones_like(self.median) * np.nan
    #
    #     for r in range(self.median.shape[0]):
    #
    #         for c in range(self.median.shape[1]):
    #
    #             pct_height = 3.0  # per cent
    #
    #             # correction for variability in range
    #             nmad = self.nmad[r, c]
    #             if (nmad < 0.1) or np.isnan(nmad):
    #                 pass
    #             elif nmad < 0.2:
    #                 pct_height += 0.5
    #             elif nmad < 0.3:
    #                 pct_height += 1.0
    #             elif nmad < 0.4:
    #                 pct_height += 1.5
    #             else:
    #                 pct_height += 2.0
    #
    #             # correction for global roughness
    #             std_gauss_curv = self.std_gauss_curv[r, c]
    #             if (std_gauss_curv < 0.01) or (np.isnan(std_gauss_curv)):
    #                 pass
    #             elif std_gauss_curv < 0.03:
    #                 pct_height += 0.5
    #             elif std_gauss_curv < 0.06:
    #                 pct_height += 1.0
    #             elif std_gauss_curv < 0.1:
    #                 pct_height += 1.5
    #             else:
    #                 pct_height += 2.0
    #
    #             median = self.median[r, c]
    #             if np.isnan(median):
    #                 self.th_height[r, c] = np.nan
    #             else:
    #                 self.th_height[r, c] = abs(median) * pct_height * 0.01
    #                 if self.th_height[r, c] < 0.5:
    #                     self.th_height[r, c] = 0.5
    #
    #             # noinspection PyStringFormat
    #             # logger.debug("proxies -> median: %f, nmad: %f, std curv: %f -> %.1f%% -> %.3f"
    #             #              % (median, nmad, std_gauss_curv, pct_height, self.th_height[r, c]))
    #
    #             # correction for curvature threshold
    #             if np.isnan(std_gauss_curv):
    #                 th_curv = np.nan
    #             else:
    #                 th_curv = 0.0001
    #                 if std_gauss_curv < -0.01:
    #                     th_curv *= 2.0
    #                 if std_gauss_curv < -0.03:
    #                     th_curv *= 2.0
    #                 if std_gauss_curv < -0.1:
    #                     th_curv *= 2.0
    #
    #             # logger.info("estimated gaussian threshold: %.1f" % th_curv)
    #             self.th_gauss_curv[r, c] = th_curv
    #
    #     logger.info("thresholds calculation: OK (time: %.3f s)" % (time.time() - start_time, ))

    def plot(self):
        if self._array is not None:
            plt.figure("input: array")
            m = plt.imshow(self._array, interpolation='none')
            plt.colorbar(m)

        if self.median is not None:
            plt.figure("proxy: median")
            m = plt.imshow(self.median, interpolation='none')
            plt.colorbar(m)

        if self.nmad is not None:
            plt.figure("proxy: nmad")
            m = plt.imshow(self.nmad, interpolation='none')
            plt.colorbar(m)

        if self.std_gauss_curv is not None:
            plt.figure("proxy: std gaussian curvature")
            m = plt.imshow(self.std_gauss_curv, interpolation='none')
            plt.colorbar(m)

        if self.th_height is not None:
            plt.figure("output: height thresholds")
            m = plt.imshow(self.th_height, interpolation='none')
            plt.colorbar(m)

        if self.th_gauss_curv is not None:
            plt.figure("output: gaussian curvature thresholds")
            m = plt.imshow(self.th_gauss_curv, interpolation='none')
            plt.colorbar(m)

        plt.show()

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <filter radius: %s>\n" % self.filter_radius
        msg += "  <median: %s>\n" % (self.median is not None)
        msg += "  <nmad: %s>\n" % (self.nmad is not None)
        msg += "  <std gauss curv: %s>\n" % (self.std_gauss_curv is not None)

        msg += "  <th height: %s>\n" % (self.th_height is not None)
        msg += "  <th curvature: %s>\n" % (self.th_gauss_curv is not None)

        return msg

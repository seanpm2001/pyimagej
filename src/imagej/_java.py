"""
Internal utility functions for working with Java objects.
These are not intended for external use in PyImageJ-based scripts!
"""
import logging
from functools import lru_cache

from jpype import JArray, JObject
from scyjava import JavaClasses, jstacktrace


def log_exception(logger: logging.Logger, exc: "jc.Throwable") -> None:
    if logger.isEnabledFor(logging.DEBUG):
        jtrace = jstacktrace(exc)
        if jtrace:
            logger.debug(jtrace)


# Import Java resources on demand.


@lru_cache(maxsize=None)
def JObjectArray():
    return JArray(JObject)


class MyJavaClasses(JavaClasses):
    """
    Utility class used to make importing frequently-used Java classes
    significantly easier and more readable.
    """

    @JavaClasses.java_import
    def Throwable(self):
        return "java.lang.Throwable"

    @JavaClasses.java_import
    def ImagePlus(self):
        return "ij.ImagePlus"

    @JavaClasses.java_import
    def ResultsTable(self):
        return "ij.measure.ResultsTable"

    @JavaClasses.java_import
    def ImageMetadata(self):
        return "io.scif.ImageMetadata"

    @JavaClasses.java_import
    def MetadataWrapper(self):
        return "io.scif.filters.MetadataWrapper"

    @JavaClasses.java_import
    def LabelingIOService(self):
        return "io.scif.labeling.LabelingIOService"

    @JavaClasses.java_import
    def Dataset(self):
        return "net.imagej.Dataset"

    @JavaClasses.java_import
    def ImageJ(self):
        return "net.imagej.ImageJ"

    @JavaClasses.java_import
    def ImgPlus(self):
        return "net.imagej.ImgPlus"

    @JavaClasses.java_import
    def Axes(self):
        return "net.imagej.axis.Axes"

    @JavaClasses.java_import
    def Axis(self):
        return "net.imagej.axis.Axis"

    @JavaClasses.java_import
    def AxisType(self):
        return "net.imagej.axis.AxisType"

    @JavaClasses.java_import
    def CalibratedAxis(self):
        return "net.imagej.axis.CalibratedAxis"

    @JavaClasses.java_import
    def ClassUtils(self):
        return "org.scijava.util.ClassUtils"

    @JavaClasses.java_import
    def Dimensions(self):
        return "net.imglib2.Dimensions"

    @JavaClasses.java_import
    def RandomAccessibleInterval(self):
        return "net.imglib2.RandomAccessibleInterval"

    @JavaClasses.java_import
    def ImgMath(self):
        return "net.imglib2.algorithm.math.ImgMath"

    @JavaClasses.java_import
    def Img(self):
        return "net.imglib2.img.Img"

    @JavaClasses.java_import
    def ImgView(self):
        return "net.imglib2.img.ImgView"

    @JavaClasses.java_import
    def ImgLabeling(self):
        return "net.imglib2.roi.labeling.ImgLabeling"

    @JavaClasses.java_import
    def Named(self):
        return "org.scijava.Named"

    @JavaClasses.java_import
    def Table(self):
        return "org.scijava.table.Table"

    @JavaClasses.java_import
    def Util(self):
        return "net.imglib2.util.Util"

    @JavaClasses.java_import
    def Views(self):
        return "net.imglib2.view.Views"


jc = MyJavaClasses()

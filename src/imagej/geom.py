import scyjava as sj
from functools import lru_cache

class GeomManager:
    def __init__(self, ConvertService, ROIService):
        self.ROIService = ROIService
        self.ConvertService = ConvertService
        return

    def add(self):
        return

    def add_roi(self, roi):
        return
    
    def select(self):
        return

    def _imagej_to_imglib2_roi(self, roi):
        return self.ConvertService.convert(roi, _RealMask())

    def _imglib2_to_imagej_roi(self, roi):
        return self.ConvertService.convert(roi, _PolygonRoi())

# import Java resouces on demand
@lru_cache(maxsize=None)
def _Dataset():
    return sj.jimport("net.imagej.Dataset")

@lru_cache(maxsize=None)
def _LabelRegions():
    return sj.jimport("net.imglib2.roi.labeling.LabelRegions")

@lru_cache(maxsize=None)
def _Regions():
    return sj.jimport("net.imglib2.roi.Regions")

@lru_cache(maxsize=None)
def _Polygon2D():
    return sj.jimport("net.imglib2.roi.geom.real.Polygon2D")

@lru_cache(maxsize=None)
def _Box():
    return sj.jimport("net.imglib2.roi.geom.real.Box")

@lru_cache(maxsize=None)
def _Ellipsoid():
    return sj.jimport("net.imglib2.roi.geom.real.Ellipsoid")

@lru_cache(maxsize=None)
def _Line():
    return sj.jimport("net.imglib2.roi.geom.real.Line")

@lru_cache(maxsize=None)
def _GeomMasks():
    return sj.jimport("net.imglib2.roi.geom.GeomMasks")

@lru_cache(maxsize=None)
def _RealMask():
    return sj.jimport("net.imglib2.roi.RealMask")

@lru_cache(maxsize=None)
def _MaskPredicate():
    return sj.jimport("net.imglib2.roi.MaskPredicate")

@lru_cache(maxsize=None)
def _PolygonRoi():
    return sj.jimport("ij.gui.PolygonRoi")
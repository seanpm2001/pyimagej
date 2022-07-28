import scyjava as sj
from functools import lru_cache

class GeomManager:
    def __init__(self, ConvertService, ROIService):
        self.ROIService = ROIService
        self.ConvertService = ConvertService
        self._roi_dict = {}

    def add_roi(self, roi):
        """Add rois to the Geom Manager.
        """
        # generate a unique key
        if self._is_listlike(roi):
            for i in range(len(roi)):
                self._roi_dict[self._generate_roi_label(roi[i])] = roi[i]
        else:
            self._roi_dict[self._generate_roi_label(roi)] = roi

    def display_imageplus_roi(self, image: "ij.ImagePlus"):
        """Display the stored Geom Manager rois on an ImagePlus image.
        """
        ov = _Overlay()()
        for k, v in self._roi_dict.items():
            if not isinstance(v, _Roi()):
                ij_roi = self._imglib2_to_imagej_roi(v)
                ov.add(ij_roi)
            else:
                ov.add(v)

        ic = image.getCanvas()
        ic.setShowAllList(ov)
        image.draw

    def collect_RoiManager_rois(self, RoiManager):
        """Collect rois from the ImageJ RoiManager.
        """
        rois = RoiManager.getRoisAsArray()
        self.add_roi(rois)

    def get_roi(self, key):
        """Get a specific roi with a key.
        """
        try:
            return self._roi_dict[key]
        except KeyError:
            print(f"{key} ROI was not found.")

    def get_roi_as_list(self):
        """Get Geom Manager's rois as a List.
        """
        rois = []
        for k, v in self._roi_dict.items():
            rois.append(v)

        return rois

    def select(self):
        return

    def show(self):
        i = 0
        print(f"index\tlabel\troi")
        for k, v in self._roi_dict.items():
            print(f"{i}\t{k}\t{type(v)}")
            i += 1

    def transfer_imageplus_roi(self, image, rois: "ij.gui.Roi"):
        """Transfer ROIs from an ImagePlus to another ImagePlus
        ImgLib2 image.

        :return: Output image with transfered ROIs.
        """
        # check input and output image types
        if not (isinstance(image, _ImagePlus()) or isinstance(image, _RandomAccessibleInterval())):
            raise TypeError(f"Input image type {type(image)} is not supported.")

        # transfer imagej rois to ImagePlus
        if isinstance(image, _ImagePlus()):
            if isinstance(rois, _PolygonRoi()):
                return image.setRoi(rois)
            elif self._is_listlike(rois):
                for i in range(len(rois)):
                    image.setRoi(rois[i])
                return image

        # transfer imagej rois to ImgLib2

        # check if rois a list or single roi
        # if list --> transfer --> return
        # if single --> transfer --> return

    def _generate_roi_label(self, roi, pln=None):
        """Generate a unique label from the ROI.
        """
        x_coord = str(int(roi.getXBase()))
        y_coord = str(int(roi.getYBase()))

        if pln == None:
            return x_coord + "-" + y_coord
        else:
            return str(pln) + "-" + x_coord + "-" + y_coord

    def _imagej_to_imglib2_roi(self, roi):
        return self.ConvertService.convert(roi, _RealMask())

    def _imglib2_to_imagej_roi(self, roi):
        return self.ConvertService.convert(roi, _PolygonRoi())

    def _is_listlike(self, lst):
        return (
            hasattr(lst, "length")
            or hasattr(lst, "pop")
        )

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
def _RandomAccessibleInterval():
    return sj.jimport("net.imglib2.RandomAccessibleInterval")

@lru_cache(maxsize=None)
def _Roi():
    return sj.jimport("ij.gui.Roi")

@lru_cache(maxsize=None)
def _PolygonRoi():
    return sj.jimport("ij.gui.PolygonRoi")

@lru_cache(maxsize=None)
def _ImagePlus():
    return sj.jimport("ij.ImagePlus")

@lru_cache(maxsize=None)
def _Overlay():
    return sj.jimport("ij.gui.Overlay")

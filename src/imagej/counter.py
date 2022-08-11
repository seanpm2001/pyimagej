import scyjava as sj

from pandas import DataFrame
from collections import defaultdict
from jpype import JLong
from functools import lru_cache

class ObjectCounter:
    def __init__(self, exclude=False, size_filter = True, ij_instance=None):
        self.bit_depth = None
        self.exclude = exclude
        self.size_filter = size_filter
        self.stats = None
        self._ij = ij_instance
        self._centers = []
        self._rawstats = defaultdict(list)

    def label_objects(self, image: "net.imagej.ImgPlus", structuring_element: str):
        """
        Find objects in an image using ImageJ Ops CCA.
        
        :param image: 8-bit binary image
        :param structuring_element: Specify how are considered connected.

            Options include:

            * "four" -
                Select four connected structuring element.
            * "eight" -
                Select eight connected structuring element.
        """
        # check if PyImageJ is running
        if self._ij == None:
            self._get_imagej_gateway()

        # run CCA
        if structuring_element.lower() == "four":
            labeling = self._ij.op().labeling().cca(image, _StructuringElement().FOUR_CONNECTED)
        elif structuring_element.lower() == "eight":
            labeling = self._ij.op().labeling().cca(image, _StructuringElement().EIGHT_CONNECTED)
        else:
            raise ValueError(f"\"{structuring_element}\" is not a valid StructuringElement. Use \"four\" or \"eight\".")

        return labeling

    def compute_stats(self, image, labeling: "net.imglib2.roi.labeling.ImgLabeling") -> DataFrame:
        regions = _LabelRegions()(labeling)
        for region in regions:
            self._compute_region_stats(region, image)
        
        self.stats = DataFrame(self._rawstats)
        return self.stats

    def compute_center_of_mass(self, labeling: "net.imglib2.roi.labeling.ImgLabeling"):
        regions = _LabelRegions()(labeling)
        for region in regions:
            self._centers.append(region.getCenterOfMass())

    def _compute_region_stats(self, image, region: "net.imglib2.roi.labeling.LabelRegions"):
        samples = _Regions().sample(region, image)
        self._rawstats["area"].append(self._ij.op().run("stats.size", samples).getRealDouble())
        self._rawstats["mean"].append(self._ij.op().run("stats.mean", samples).getRealDouble())
        min_max = self._ij.op().run("stats.minMax", samples)
        self._rawstats["min"].append(min_max.getA().getRealDouble())
        self._rawstats["max"].append(min_max.getB().getRealDouble())
        centroid = self._ij.op().run("geom.centroid", region)
        self._rawstats["centroid"].append(tuple(centroid.getDoublePosition(d) for d in range(centroid.numDimensions())))
        self._rawstats["median"].append(self._ij.op().run("stats.median", samples).getRealDouble())
        self._rawstats["skeness"].append(self._ij.op().run("stats.skewness", samples).getRealDouble())
        self._rawstats["kurtosis"].append(self._ij.op().run("stats.kurtosis", samples).getRealDouble())

    def overlay_center_of_mass(self, image: "net.imagej.ImgPlus"):
        """
        """
        if not self._centers:
            raise ValueError(f"No centers of mass have been calcualted.")
        
        center_image = self._ij.op().namespace(_CreateNamespace()).img(image)
        center_ra = center_image.randomAccess()
        max_value = int(center_image.firstElement().getMaxValue())
        for center in self._centers:
            dx = -1
            while dx <= 1:
                dx += 1
                dy = -1
                while dy <= 1:
                    x_pos = round(center.getDoublePosition(0)) + dx
                    y_pos = round(center.getDoublePosition(1)) + dy
                    #if x_pos >= center_image.dimension(JLong(0)) or y_pos >= center_image.dimensions(JLong(1)): # TODO: This line doesn't like int or JLong.
                    #    continue
                    center_ra.setPosition(x_pos, 0)
                    center_ra.setPosition(y_pos, 1)
                    center_ra.get().set(max_value)
                    dy += 1

        stack = _Views().stack(image, center_image)
        self._ij.ui().show("center of mass", stack)

    def _get_imagej_gateway(self):
        try:
            from imagej import ij

            self._ij = ij
        except ImportError:
            print(f"PyImageJ has not been initialized.")

@lru_cache(maxsize=None)
def _CreateNamespace():
    return sj.jimport("net.imagej.ops.create.CreateNamespace")

@lru_cache(maxsize=None)
def _LabelRegions():
    return sj.jimport("net.imglib2.roi.labeling.LabelRegions")

@lru_cache(maxsize=None)
def _RealLocalizable():
    return sj.jimport("net.imglib2.RealLocalizable")

@lru_cache(maxsize=None)
def _Regions():
    return sj.jimport("net.imglib2.roi.Regions")
        
@lru_cache(maxsize=None)
def _StructuringElement():
    return sj.jimport("net.imglib2.algorithm.labeling.ConnectedComponents.StructuringElement")

@lru_cache(maxsize=None)
def _Views():
    return sj.jimport("net.imglib2.view.Views")
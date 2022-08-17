import scyjava as sj

from pandas import DataFrame
from collections import defaultdict
from functools import lru_cache
from jpype import JInt

class ObjectCounter:
    def __init__(self, exclude=False, size_filter = True, ij_instance=None):
        self.bit_depth = None
        self.exclude = exclude
        self.size_filter = size_filter
        self.stats = None
        self._ij = ij_instance
        self._centers = []
        self._regions = []
        self._rawstats = defaultdict(list)

    def filter_labels(self, min_size: int, max_size: int, labelings: "net.imglib2.roi.labeling.ImgLabeling", structuring_element: str) -> "net.imglib2.roi.labeling.ImgLabeling":
        """Filter a labelings.

        Apply a size filter (defined by min and max pixel size) to a
        net.imglib2.roi.labeling.ImgLabeling.

        :param min_size: Miniumum pixel size to filter.
        :param max_size: Maximum pixel size to filter.
        :param labelings: ImgLabelings (i.e. the out put of a connected component analysis).
        :return: A filtered ImgLabeling.
        """
        self._check_imagej_gateway()
        regions = _LabelRegions()(labelings)

        # filter based on min and max size using flex_label_list to iterate on
        # the first LabelSet is always empty, so skip it.
        i = len(labelings.getMapping().getLabelSets()) - 1
        new_index_img = self._ij.op().namespace(_CreateNamespace()).img(labelings.getIndexImg())
        new_index_img_ra = new_index_img.randomAccess()
        _ImgUtil().copy(labelings.getIndexImg(), new_index_img)

        while i > 0:
            region = regions.getLabelRegion(labelings.getMapping().getLabels().toArray()[i - 1])
            # filter regions based on region size
            if (region.size() < min_size) or (region.size() > max_size):
                c = region.localizingCursor()
                # set regions that are outside min/max boundries to 0
                while c.hasNext():
                    c.next()
                    for d in range(c.ndim):
                        new_index_img_ra.setPosition(c.getIntPosition(d), d)
                    new_index_img_ra.get().set(0)
            else:
                c = region.localizingCursor()
                # set region kept regions to 255
                while c.hasNext():
                    c.next()
                    for d in range(c.ndim):
                        new_index_img_ra.setPosition(c.getIntPosition(d), d)
                    new_index_img_ra.get().set(255)
            i -= 1

        # convert index image to 8-bit and perform CCA again
        new_index_img = self._ij.op().convert().uint8(new_index_img)

        return self._run_cca(new_index_img, structuring_element)

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
        # run CCA
        return self._run_cca(image, structuring_element)

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

        return _Views().stack(image, center_image)

    def _run_cca(self, image, se):
        self._check_imagej_gateway()
        if se.lower() == "four":
            labeling = self._ij.op().labeling().cca(image, _StructuringElement().FOUR_CONNECTED)
        elif se.lower() == "eight":
            labeling = self._ij.op().labeling().cca(image, _StructuringElement().EIGHT_CONNECTED)
        else:
            raise ValueError(f"\"{se}\" is not a valid StructuringElement. Use \"four\" or \"eight\".")

        return labeling

    def _check_imagej_gateway(self):
        # check if PyImageJ is running
        if self._ij == None:
            self._get_imagej_gateway()

    def _compute_region_stats(self, region: "net.imglib2.roi.labeling.LabelRegions", image):
        samples = _Regions().sample(region, image)
        self._rawstats["area"].append(self._ij.op().stats().size(samples).getRealDouble())
        self._rawstats["mean"].append(self._ij.op().stats().mean(samples).getRealDouble())
        min_max = self._ij.op().stats().minMax(samples)
        self._rawstats["min"].append(min_max.getA().getRealDouble())
        self._rawstats["max"].append(min_max.getB().getRealDouble())
        centroid = self._ij.op().geom().centroid(region)
        self._rawstats["centroid"].append(tuple(centroid.getDoublePosition(d) for d in range(centroid.numDimensions())))
        self._rawstats["median"].append(self._ij.op().stats().median(samples).getRealDouble())
        self._rawstats["skewness"].append(self._ij.op().stats().skewness(samples).getRealDouble())
        self._rawstats["kurtosis"].append(self._ij.op().stats().kurtosis(samples).getRealDouble())

    def _get_imagej_gateway(self):
        try:
            from imagej import ij

            self._ij = ij
        except ImportError:
            print(f"PyImageJ has not been initialized.")

    def _labelings_to_list(self, labelings):
        regions = _LabelRegions()(labelings)
        for region in regions:
            self._regions.append(region)

@lru_cache(maxsize=None)
def _CreateNamespace():
    return sj.jimport("net.imagej.ops.create.CreateNamespace")

@lru_cache(maxsize=None)
def _ImgLabeling():
    return sj.jimport("net.imglib2.roi.labeling.ImgLabeling")

@lru_cache(maxsize=None)
def _LabelRegions():
    return sj.jimport("net.imglib2.roi.labeling.LabelRegions")

@lru_cache(maxsize=None)
def _RealLocalizable():
    return sj.jimport("net.imglib2.RealLocalizable")

@lru_cache(maxsize=None)
def _ImgUtil():
    return sj.jimport("net.imglib2.util.ImgUtil")

@lru_cache(maxsize=None)
def _Regions():
    return sj.jimport("net.imglib2.roi.Regions")
        
@lru_cache(maxsize=None)
def _StructuringElement():
    return sj.jimport("net.imglib2.algorithm.labeling.ConnectedComponents.StructuringElement")

@lru_cache(maxsize=None)
def _Views():
    return sj.jimport("net.imglib2.view.Views")
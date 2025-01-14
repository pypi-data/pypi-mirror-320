"""This is the vtk module"""

# this module has the same contents as vtkmodules.all
from vtkmodules.vtkCommonCore import *
from vtkmodules.vtkCommonMath import *
from vtkmodules.vtkCommonTransforms import *
from vtkmodules.vtkCommonDataModel import *
from vtkmodules.vtkCommonExecutionModel import *
from vtkmodules.vtkCommonMisc import *
from vtkmodules.vtkFiltersCore import *
from vtkmodules.vtkRenderingCore import *
from vtkmodules.vtkFiltersGeneral import *
from vtkmodules.vtkFiltersSources import *
from vtkmodules.vtkRenderingContext2D import *
from vtkmodules.vtkInteractionWidgets import *
from vtkmodules.vtkViewsCore import *
from vtkmodules.vtkViewsContext2D import *
from vtkmodules.vtkTestingRendering import *
from vtkmodules.vtkInteractionStyle import *
from vtkmodules.vtkViewsInfovis import *
try:
  from vtkmodules.vtkCommonColor import *
except ImportError:
  pass
from vtkmodules.vtkPythonContext2D import *
from vtkmodules.vtkImagingCore import *
from vtkmodules.vtkImagingMath import *
from vtkmodules.vtkIOImage import *
try:
  from vtkmodules.vtkRenderingHyperTreeGrid import *
except ImportError:
  pass
from vtkmodules.vtkRenderingUI import *
from vtkmodules.vtkRenderingOpenGL2 import *
from vtkmodules.vtkRenderingVolume import *
from vtkmodules.vtkRenderingVolumeOpenGL2 import *
from vtkmodules.vtkRenderingFreeType import *
from vtkmodules.vtkRenderingLabel import *
from vtkmodules.vtkRenderingLOD import *
from vtkmodules.vtkRenderingLICOpenGL2 import *
from vtkmodules.vtkRenderingImage import *
from vtkmodules.vtkRenderingContextOpenGL2 import *
from vtkmodules.vtkFiltersCellGrid import *
from vtkmodules.vtkRenderingCellGrid import *
from vtkmodules.vtkIOVeraOut import *
from vtkmodules.vtkIOTecplotTable import *
from vtkmodules.vtkIOSegY import *
from vtkmodules.vtkIOXMLParser import *
from vtkmodules.vtkIOXML import *
from vtkmodules.vtkIOParallelXML import *
from vtkmodules.vtkIOCore import *
from vtkmodules.vtkIOPLY import *
from vtkmodules.vtkIOMovie import *
from vtkmodules.vtkIOOggTheora import *
from vtkmodules.vtkIONetCDF import *
from vtkmodules.vtkIOMotionFX import *
from vtkmodules.vtkIOLegacy import *
from vtkmodules.vtkIOGeometry import *
from vtkmodules.vtkIOParallel import *
from vtkmodules.vtkIOMINC import *
from vtkmodules.vtkIOLSDyna import *
from vtkmodules.vtkIOInfovis import *
from vtkmodules.vtkIOImport import *
from vtkmodules.vtkParallelCore import *
from vtkmodules.vtkIOIOSS import *
from vtkmodules.vtkIOFLUENTCFF import *
from vtkmodules.vtkIOVideo import *
try:
  from vtkmodules.vtkRenderingSceneGraph import *
except ImportError:
  pass
try:
  from vtkmodules.vtkRenderingVtkJS import *
except ImportError:
  pass
from vtkmodules.vtkIOExport import *
from vtkmodules.vtkIOExportPDF import *
try:
  from vtkmodules.vtkRenderingGL2PSOpenGL2 import *
except ImportError:
  pass
from vtkmodules.vtkIOExportGL2PS import *
from vtkmodules.vtkIOExodus import *
from vtkmodules.vtkIOEnSight import *
from vtkmodules.vtkIOCityGML import *
from vtkmodules.vtkIOChemistry import *
from vtkmodules.vtkIOCesium3DTiles import *
from vtkmodules.vtkIOCellGrid import *
from vtkmodules.vtkIOCONVERGECFD import *
from vtkmodules.vtkIOHDF import *
from vtkmodules.vtkIOCGNSReader import *
from vtkmodules.vtkIOAsynchronous import *
from vtkmodules.vtkIOAMR import *
from vtkmodules.vtkInteractionImage import *
from vtkmodules.vtkImagingStencil import *
from vtkmodules.vtkImagingStatistics import *
from vtkmodules.vtkImagingGeneral import *
from vtkmodules.vtkImagingMorphological import *
from vtkmodules.vtkImagingFourier import *
from vtkmodules.vtkIOSQL import *
from vtkmodules.vtkImagingSources import *
from vtkmodules.vtkInfovisCore import *
from vtkmodules.vtkGeovisCore import *
from vtkmodules.vtkInfovisLayout import *
from vtkmodules.vtkRenderingAnnotation import *
from vtkmodules.vtkImagingHybrid import *
from vtkmodules.vtkImagingColor import *
from vtkmodules.vtkFiltersTopology import *
from vtkmodules.vtkFiltersTensor import *
from vtkmodules.vtkFiltersSelection import *
from vtkmodules.vtkFiltersSMP import *
from vtkmodules.vtkFiltersReduction import *
from vtkmodules.vtkFiltersPython import *
from vtkmodules.vtkFiltersProgrammable import *
from vtkmodules.vtkFiltersModeling import *
from vtkmodules.vtkFiltersPoints import *
from vtkmodules.vtkFiltersStatistics import *
from vtkmodules.vtkFiltersImaging import *
from vtkmodules.vtkFiltersExtraction import *
from vtkmodules.vtkFiltersGeometry import *
from vtkmodules.vtkFiltersHybrid import *
from vtkmodules.vtkFiltersHyperTree import *
from vtkmodules.vtkFiltersTexture import *
from vtkmodules.vtkFiltersParallel import *
from vtkmodules.vtkFiltersParallelImaging import *
from vtkmodules.vtkFiltersGeometryPreview import *
from vtkmodules.vtkFiltersGeneric import *
from vtkmodules.vtkCommonComputationalGeometry import *
from vtkmodules.vtkFiltersFlowPaths import *
from vtkmodules.vtkFiltersAMR import *
from vtkmodules.vtkDomainsChemistry import *
from vtkmodules.vtkDomainsChemistryOpenGL2 import *
from vtkmodules.vtkCommonPython import *
from vtkmodules.vtkChartsCore import *
from vtkmodules.vtkCommonSystem import *
from vtkmodules.vtkFiltersVerdict import *


# useful macro for getting type names
from vtkmodules.util.vtkConstants import vtkImageScalarTypeNameMacro

# import convenience decorators
from vtkmodules.util.misc import calldata_type

# import the vtkVariant helpers
from vtkmodules.util.vtkVariant import *

# clone parts of vtkmodules to make this look like a package
import vtkmodules as _vtk_package
__path__ = _vtk_package.__path__
__version__ = _vtk_package.__version__
del _vtk_package

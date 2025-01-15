#!/Users/cbm038/Documents/science/code/Windmapper/implimentation/._view/scjkmzim3fnkz7yvcwyiiti766jw6mgg/bin/python3

import sys

from osgeo.gdal import deprecation_warn

# import osgeo_utils.ogrmerge as a convenience to use as a script
from osgeo_utils.ogrmerge import *  # noqa
from osgeo_utils.ogrmerge import main

deprecation_warn("ogrmerge")
sys.exit(main(sys.argv))

#!/Users/cbm038/Documents/science/code/Windmapper/implimentation/._view/scjkmzim3fnkz7yvcwyiiti766jw6mgg/bin/python3

import sys

from osgeo.gdal import deprecation_warn

# import osgeo_utils.pct2rgb as a convenience to use as a script
from osgeo_utils.pct2rgb import *  # noqa
from osgeo_utils.pct2rgb import main

deprecation_warn("pct2rgb")
sys.exit(main(sys.argv))

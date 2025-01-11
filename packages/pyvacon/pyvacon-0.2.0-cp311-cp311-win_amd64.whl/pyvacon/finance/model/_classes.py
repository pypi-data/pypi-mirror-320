import pyvacon.pyvacon_swig as _swig
from pyvacon._converter import _add_converter

BaseModel = _add_converter(_swig.BaseModel)
CalibrationStorage = _add_converter(_swig.CalibrationStorage)
ModelLab = _add_converter(_swig.ModelLab)
BuehlerLocalVolModel = _add_converter(_swig.BuehlerLocalVolModel)
MultiModel = _add_converter(_swig.MultiModel)



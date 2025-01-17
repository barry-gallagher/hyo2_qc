import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

from PySide import QtGui

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.qctools.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

app = QtGui.QApplication([])
wid = QtGui.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a CSAR file
csar_files = testing.input_test_files(".csar")
print("- CSAR files: %d" % len(csar_files))

# # add a BAG file
# bag_files = testing.input_test_files(".bag")
# print("- BAG files: %d" % len(bag_files))

prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(csar_files[1])
# prj.add_to_grid_list(bag_files[0])
print("%s" % (prj.grid_list,))

four_gb = 4294967296
one_mb = 1048576

for grid_path in prj.grid_list:
    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)
    tvu_qc_layers = prj.cur_grid_tvu_qc_layers()
    if len(tvu_qc_layers) > 0:
        prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])
    ret = prj.grid_qa_v4(force_tvu_qc=True,
                         calc_object_detection=True,
                         calc_full_coverage=True
                         )
    prj.open_gridqa_output_folder()
    print("passed? %s" % ret)

# print project info
logger.debug(prj)

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
# csar_files = testing.input_test_files(".csar")
# print("- CSAR files: %d" % len(csar_files))

# # add a BAG file
bag_files = testing.input_test_files(".bag")
# print("- BAG files: %d" % len(bag_files))
# csar_file = "C:/Users/giumas/Google Drive/Testing_Datasets/ObjectDetection_H12676/H12676_10_2_2_Ranges_ObjectDetection_Holidays_finalized.csar"
# csar_file = "C:/Users/giumas/Google Drive/Testing_Datasets/ObjectDetection_H12676/H12676_10_2_2_Ranges_ObjectDetection_Holidays.csar"
# csar_file = "C:\\Users\\giumas\\Google Drive\\QC Tools\\test data\\H12924\\H12924_MB_1m_MLLW_Final.csar"
csar_file = "C:\\Users\\gmasetti\\Google Drive\\QC Tools\\test data\\W00341\\W00341_MB_VR_MLLW_Final.csar"

# prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(csar_files[1])
# prj.add_to_grid_list(bag_files[0])
prj.add_to_grid_list(csar_file)
print("%s" % (prj.grid_list,))

four_gb = 4294967296
one_mb = 1048576

force_tvu_qc = True

calc_object_detection = False
calc_full_coverage = True

hist_depth = True
hist_density = True
hist_tvu_qc = True
hist_pct_res = True

depth_vs_density = False
depth_vs_tvu_qc = False


for grid_path in prj.grid_list:

    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)

    tvu_qc_layers = prj.cur_grid_tvu_qc_layers()
    if len(tvu_qc_layers) > 0:
        prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])

    ret = prj.grid_qa_v5(
        force_tvu_qc=force_tvu_qc,
        calc_object_detection=calc_object_detection, calc_full_coverage=calc_full_coverage,
        hist_depth=hist_depth, hist_density=hist_density, hist_tvu_qc=hist_tvu_qc, hist_pct_res=hist_pct_res,
        depth_vs_density=depth_vs_density, depth_vs_tvu_qc=depth_vs_tvu_qc
    )
    prj.open_gridqa_output_folder()
    print("passed? %s" % ret)

# print project info
logger.debug(prj)

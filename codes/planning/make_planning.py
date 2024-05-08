import matplotlib.pyplot as plt

from codes.drld_parser import data_reduction_library_design as drld_parser
from codes.aiv_parser.aiv_mapping import AivMap
from codes.pip_releases.pip_releases import DeliveryScheduler

drld = drld_parser.DataReductionLibraryDesign()

# # Generate the matrix PDFs
aiv_map = AivMap()
aiv_map.plot_aiv_matrix(True, "recipes", "recipes.pdf")
aiv_map.plot_aiv_matrix(True, "data_items", "data_items.pdf")

# Generate schedule
ds = DeliveryScheduler(True)
ds.dump_yaml("pip_releases_details.yaml")
ds.dump_latex("pip_releases_details.tex")


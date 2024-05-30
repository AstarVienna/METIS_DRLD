import matplotlib.pyplot as plt

from codes.drld_parser import data_reduction_library_design as drld_parser
from codes.aiv_parser.aiv_mapping import AivMap
from codes.pip_releases.pip_releases import DeliveryScheduler

drld = drld_parser.DataReductionLibraryDesign()

# # Generate the matrix PDFs
compress = False
aiv_map = AivMap()
aiv_map.plot_aiv_matrix(compress, "recipes", "recipes.pdf")
aiv_map.plot_aiv_matrix(compress, "data_items", "data_items.pdf")

ds = DeliveryScheduler(True)
ds.plot_delv_matrix(filename="deliveries_recipes.pdf")

# Generate schedule
# ds = DeliveryScheduler(True)
# ds.dump_yaml("pip_releases_details.yaml")
# ds.dump_latex("pip_releases_details.tex")


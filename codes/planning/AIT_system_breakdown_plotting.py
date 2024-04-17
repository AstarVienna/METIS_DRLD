from collections import OrderedDict

import yaml
from datetime import datetime, date
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from codes.drld_parser import data_reduction_library_design as drld_parser
DRLD = drld_parser.DataReductionLibraryDesign()

RECIPES = {key.lower(): value for key, value in DRLD.get_recipes().items()}
RECIPES = OrderedDict(sorted(RECIPES.items()))

DATA_ITEMS = {key.lower(): value for key, value in DRLD.get_dataitems().items()}
DATA_ITEMS = OrderedDict(sorted(DATA_ITEMS.items()))

VALS = {"skel": 1, "func": 2, "perf": 3, "sci": 4}
CLRS = {"skel": "blue", "func": "yellow", "perf": "orange", "sci": "red"}


class AivMap:
    def __init__(self, data):
        self.aiv_phases = [AivPhase(**aiv_phase) for aiv_phase in data]

    @property
    def year_index_dict(self):
        aiv_phases = self.aiv_matrix[1]
        aiv_years = {10 : 2025, 330 : 2026, 640 : 2027, 850 : 2028}
        return {year: np.where(aiv_phases == aiv)[0][0]
                for aiv, year in aiv_years.items()}

    def aiv_matrix(self, compress=False, which="recipes"):
        if which == "recipes":
            if compress:
                mat = [aiv_phase.tests_vector for aiv_phase in self.aiv_phases]
                mat = np.vstack(mat).T
            else:
                mat = [aiv_phase.tests_matrix for aiv_phase in self.aiv_phases]
                mat = np.hstack(mat)
        elif which == "data_items":
            if compress:
                mat = [aiv_phase.tests_di_vector for aiv_phase in self.aiv_phases]
                mat = np.vstack(mat).T
            else:
                mat = [aiv_phase.tests_di_matrix for aiv_phase in self.aiv_phases]
                mat = np.hstack(mat)

        # Sort by AIV phase
        idx = np.argsort(mat[0])
        mat = mat[:, idx]

        return mat

    def plot_aiv_matrix(self, compress=False, which="recipes", filename=None,
                        figsize=(15, 10)):
        im = aiv_map.aiv_matrix(compress, which)
        # Sort by leading zeros
        leading_zeros = [np.where(row > 0)[0][0]
                         if row.max() > 0 else im.shape[1] for row in im]
        idx = np.argsort(leading_zeros[3:])
        im[3:, :] = im[3:, :][idx, :]

        if which == "recipes":
            recipes = list(RECIPES.keys())
            y_tick_labels = [recipes[i] for i in idx]
            gridspec_kw = {'height_ratios': [1, 5]}
        elif which == "data_items":
            data_items = list(DATA_ITEMS.keys())
            y_tick_labels = [data_items[i] for i in idx]
            gridspec_kw = {'height_ratios': [1, 20]}

        fig, axs = plt.subplots(2, 1, figsize=figsize,
                                gridspec_kw=gridspec_kw)

        plt.sca(axs[1])
        plt.imshow(im[3:], cmap="jet", norm=LogNorm())

        for phase in self.aiv_phases:
            phase_line = im[1]
            i = np.where(phase_line == phase.int_phase_id)[0][0]
            plt.axvline(i - 0.5)
            plt.text(i, -1.5, phase.date, rotation=90, ha="center", va="bottom")

        x_values = im[2]
        x_axis = np.arange(len(x_values))
        plt.xticks(x_axis, x_values, rotation=90)

        y_axis = np.arange(len(y_tick_labels))
        plt.yticks(y_axis, y_tick_labels)
        plt.gca().set_aspect('auto')

        plt.sca(axs[0])
        plt.imshow(im[:1], cmap="Greys")

        x_values = np.unique(im[1])
        x_axis = [np.where(x == im[1])[0][0] for x in x_values]
        plt.xticks(x_axis, [f"AIV-{x}" for x in x_values], rotation=90)

        y_tick_labels = ["Days remaining"]
        y_axis = np.arange(len(y_tick_labels))
        plt.yticks(y_axis, y_tick_labels)
        plt.gca().xaxis.tick_top()

        plt.tight_layout()

        if filename:
            plt.savefig(filename, format="pdf")


class AivPhase:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.aiv_tests = [AivTest(**test) for test in kwargs["tests"]]

    @property
    def int_phase_id(self):
        return int(self.phase_id.split("-")[-1])

    @property
    def days_left(self) -> int:
        if not isinstance(self.date, date):
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        return (self.date - datetime.now().date()).days

    @property
    def tests_matrix(self):
        mat = [aiv_test.recipes_matrix for aiv_test in self.aiv_tests]
        mat = np.vstack(mat).T
        mat[1] = self.int_phase_id
        mat[0] = self.days_left
        return mat

    @property
    def tests_vector(self):
        return self.tests_matrix.max(axis=1)

    @property
    def tests_di_matrix(self):
        mat = [aiv_test.data_items_matrix for aiv_test in self.aiv_tests]
        mat = np.vstack(mat).T
        mat[1] = self.int_phase_id
        mat[0] = self.days_left
        return mat

    @property
    def tests_di_vector(self):
        return self.tests_di_matrix.max(axis=1)


class AivTest:
    def __init__(self, **kwargs):
        self.__dict__.update({"pip_recipes": []})
        self.__dict__.update(kwargs)

    @property
    def int_test_id(self):
        return int(self.polarion_id.split("-")[-1])

    @property
    def recipes_matrix(self):
        mat = np.zeros(len(RECIPES) + 3, dtype=int)
        mat[2] = self.int_test_id
        for i, rec in enumerate(RECIPES):
            if self.pip_recipes and rec in self.pip_recipes:
                mat[i+3] = VALS[self.pip_recipes[rec]]
        return mat

    @property
    def data_items(self):
        data_itmes_dict = {}
        if self.pip_recipes:
            for my_rec, level in self.pip_recipes.items():
                for drld_rec, rec_item in RECIPES.items():
                    if my_rec == drld_rec.lower():
                        for in_d in rec_item.input_data:
                            data_itmes_dict[in_d.name] = level
                        for in_d in rec_item.output_data:
                            data_itmes_dict[in_d.name] = level

        return data_itmes_dict

    @property
    def data_items_matrix(self):
        mat = np.zeros(len(DATA_ITEMS) + 3, dtype=int)
        mat[2] = self.int_test_id
        data_items = self.data_items
        for i, di in enumerate(DATA_ITEMS):
            if data_items and di.upper() in data_items:
                mat[i + 3] = VALS[data_items[di.upper()]]
        return mat


if __name__ == "__main__":
    with open("AIT-system-tests-breakdown-for-pip-schedule.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    aiv_map = AivMap(data)
    aiv_map.plot_aiv_matrix(True, which="recipes",
                            filename="recipes.pdf", figsize=(10, 15))
    aiv_map.plot_aiv_matrix(True, which="data_items",
                            filename="data_items.pdf", figsize=(10, 40))

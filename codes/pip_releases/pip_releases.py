import numpy as np
import yaml
from pathlib import Path
from copy import copy


from codes.aiv_parser.aiv_mapping import AivMap, RECIPES, DATA_ITEMS, INV_VALS, DRLD
AIV_MAP = AivMap()


class Delivery:
    def __init__(self, dic: dict):
        self.orig_dic = dic
        self.__dict__.update(dic)

        sub_aiv_map = AivMap(data=[])
        sub_aiv_map.aiv_phases = [ph for ph in AIV_MAP.aiv_phases
                                  if ph.date <= self.date]
        if sub_aiv_map.aiv_phases:
            self.recipes_mat = sub_aiv_map.aiv_matrix(compress=True, which="recipes")
            self.data_items_mat = sub_aiv_map.aiv_matrix(compress=True, which="data_items")
        else:
            self.recipes_mat = None
            self.data_items_mat = None

    @property
    def recipes(self):
        recs = {}
        if self.recipes_mat is not None:
            lvls = self.recipes_mat.max(axis=1)
            recs = {rec: lvl for rec, lvl in zip(RECIPES, lvls[3:])}

        return recs

    @property
    def data_items(self):
        dis = {}
        if self.recipes_mat is not None:
            lvls = self.data_items_mat.max(axis=1)
            dis = {di: lvl for di, lvl in zip(DATA_ITEMS, lvls[3:])}

        return dis

    def get_items_by_level(self, which="recipes", level=1):
        dis = []
        if which == "recipes":
            dis = [di for di in self.recipes if di == level]
        elif which == "data_items":
            dis = [di for di in self.data_items if di == level]


class DeliveryScheduler:
    def __init__(self, auto_redistibute=False):
        path = Path(__file__).parent
        with open(path / "pip_releases_summary.yaml", "r") as f:
            self.data = yaml.load(f, Loader=yaml.FullLoader)
        self.deliveries = {i: Delivery(d) for i, d in enumerate(self.data)}
        self.auto_redistibute = auto_redistibute

    def new_items(self, i, which="recipes"):
        this_del = getattr(self.deliveries[i], which)
        prev_del = getattr(self.deliveries[i-1], which) if i else {}

        new_items = {}
        for item, lvl in this_del.items():
            if this_del[item] == 0:
                continue
            elif not len(prev_del):
                new_items[item] = INV_VALS[lvl]
            elif item in prev_del and this_del[item] > prev_del[item]:
                new_items[item] = INV_VALS[lvl]

        return new_items

    @property
    def delivery_dict(self):
        delv_dict = {}
        for i, dv in self.deliveries.items():
            dv.orig_dic["pip_recipes"] = self.new_items(i, which="recipes")
            # dv.orig_dic["data_items"] = self.new_items(i, which="data_items")
            delv_dict[i] = dv.orig_dic

        if self.auto_redistibute:
            self.redistribute_items(delv_dict, "recipes")
            # self.redistribute_items(delv_dict, "data_items")

        for delv in delv_dict.values():
            data_itmes_dict = {}
            for my_rec, level in delv["pip_recipes"].items():
                if my_rec in RECIPES:
                    rec_item = RECIPES[my_rec]
                    for in_d in rec_item.input_data:
                        if in_d.name is not None and isinstance(in_d.name, str):
                            data_itmes_dict[in_d.name.upper()] = level
                    for out_d in rec_item.output_data:
                        if out_d.name is not None and isinstance(out_d.name, str):
                            data_itmes_dict[out_d.name.upper()] = level

            delv["data_items"] = data_itmes_dict

        for i in range(1, len(delv_dict)):
            to_pop = []
            dis_this = delv_dict[i]["data_items"]
            for j in range(i):
                dis_prev = delv_dict[j]["data_items"]
                to_pop = [di for di, lvl in dis_this.items()
                          if di in dis_prev and dis_prev[di] == lvl]
            for di in to_pop:
                dis_this.pop(di)

        return delv_dict

    def redistribute_items(self, delv_dict, which="recipes"):
        item_name = which
        if which == "recipes":
            item_name = "pip_" + item_name

        for i in delv_dict:
            empty_i = []
            j = copy(i)
            while j < len(delv_dict) - 1 and len(delv_dict[j][item_name]) == 0:
                empty_i += [j]
                j += 1

            recs_to_distribute = delv_dict[j][item_name]
            n_delvs = len(empty_i) + 1
            n_recs_per_delv = len(recs_to_distribute) // n_delvs
            for k in empty_i:
                for lvl in ["sci", "perf", "func", "skel"]:
                    if len(delv_dict[k][item_name]) == n_recs_per_delv:
                        break
                    for rec, rec_lvl in recs_to_distribute.items():
                        if len(delv_dict[k][item_name]) == n_recs_per_delv:
                            break
                        if rec_lvl == lvl:
                            delv_dict[k][item_name][rec] = rec_lvl

                for rec in delv_dict[k][item_name]:
                    recs_to_distribute.pop(rec)



    def make_latex_for_delivery(self, delv):

        rel_type_str = ", ".join(delv["release_types"])

        indent = "    \\\\ \n                    & "
        recipe_str = indent.join(["\REC{" + item + "} : " + lvl
                                  for item, lvl in delv["pip_recipes"].items()])

        data_items_str = indent.join(["\PROD{" + item + "} : " + lvl
                                      for item, lvl in delv["data_items"].items()])

        delv_str = r"\begin{recipedef}" + f"""
    Version      :  & {delv["version_no"]}      \\\\
    Release Name :  & {delv["version_name"]}    \\\\
    Release Date :  & {delv["date"]}            \\\\
    Description :   & {delv["comment"]}         \\\\
    Needed by AIV phase : & AIV-{delv["needed_by_aiv_phase"]}     \\\\
    Contents :      & {rel_type_str}            \\\\
    Recipes :       & {recipe_str}              \\\\
    Data Items :    & {data_items_str}          \\\\
""" + r"\end{recipedef}"

        return delv_str

    @property
    def latex_for_delivery_schedule(self):
        latex_str = ""
        for delv in self.delivery_dict.values():
            preamble_str = r"\subsubsection{" + f"Version {delv['version_no']} : {delv['version_name']}" + r"}" + "\n" \
                           r"\label{sssec:pip_del_" + f"{delv['version_no']}" + r"}" + "\n\n\n"
            latex_str += preamble_str
            latex_str += self.make_latex_for_delivery(delv) + "\n\n\n"

        return latex_str

    def dump_yaml(self, filename="pip_releases_details.yaml"):
        with open(filename, "w") as f:
            yaml.dump(self.delivery_dict, f)

    def dump_latex(self, filename="pip_releases_details.tex"):
        with open(filename, "w") as f:
            f.write(self.latex_for_delivery_schedule)


if __name__ == "__main__":
    ds = DeliveryScheduler(True)
    dd = ds.delivery_dict
    s = ds.latex_for_delivery_schedule
    ds.dump_latex()
    print(s)

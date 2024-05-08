from os.path import exists
import pickle
import yaml
from bs4 import BeautifulSoup

import numpy as np
from astropy.io import ascii

import polarion.polarion as polarion
from polarion.workitem import Workitem


aiv_dates_tbl = ascii.read("aiv_dates.dat")
AIV_DATES = {row["MET-AIV-x"] : [row["Date"], row["Description"]]
             for row in aiv_dates_tbl}


def get_polarion_test_cases():
    username = "leschinskik"
    password = "m3T!54KL"
    url = 'https://polarion.astron.nl/polarion'
    client = polarion.Polarion(url, username, password)
    project = client.getProject('METIS')

    search_str = 'type:(system_test_case) AND NOT status:discarded'
    systest_search_result = project.searchWorkitem(search_str)
    polarion_ids = [result['id'] for result in systest_search_result]
    work_items = [project.getWorkitem(p_id) for p_id in polarion_ids]

    return work_items


class PolarionWorkItemDict():
    def __init__(self, work_item: Workitem):
        # self.work_item = work_item
        self.p_id: int = int(work_item.id.replace("METIS-", ""))
        self.title: str = work_item.title
        self.time_estimate: str = work_item.initialEstimate
        self.description: str = work_item.description.content

        self.category: str = work_item.getCustomField("tccategory").EnumOptionId[0].id
        self.owner: str = work_item.getCustomField("owner").id
        self.sub_systems: list[str] = [opt.id for opt in work_item.getCustomField("subsys").EnumOptionId] if work_item.getCustomField("subsys") else []
        self.pip_recipes: list[str] = [opt.id for opt in work_item.getCustomField("pip_recipes").EnumOptionId] if work_item.getCustomField("pip_recipes") else []

        self.test_steps = work_item.getTestSteps()

        self.ait_id: int = int(work_item.getCustomField("ait-id").EnumOptionId[0].id) if work_item.getCustomField("ait-id") else 10
        self.aiv_date, self.aiv_description = AIV_DATES[self.ait_id]

    def __repr__(self):
        return (f"PolarionWorkItemDict : AIV-{self.aiv_date} "
                f": METIS-{self.p_id} "
                f": {len(self.pip_recipes)} PIP recipes")

    @property
    def _pip_recipes_clean(self):
        return [rec for rec in self.pip_recipes if rec != "na"]

    @property
    def yaml_dict(self):
        test_steps = self.test_steps
        for step in test_steps:
            for key, value in step.items():
                if value:
                    step[key] = BeautifulSoup(step[key], "lxml").text

        return {"polarion_id": self.p_id,
                "title": self.title,
                "ait_id": self.ait_id,
                "aiv_date": str(self.aiv_date),
                "aiv_description": str(self.aiv_description),
                "test_steps": test_steps,
                "pip_recipes": {rec: 5 for rec in self.pip_recipes if rec != "na"},
                "comments": "",
                }


class MetisTestCases:
    def __init__(self, force_polarion: bool = False,
                 filename: str = "polarion_tests.pyc") -> None:

        self.filename = filename
        if exists(self.filename) and not force_polarion:
            with open(self.filename, "rb") as f:
                self.test_case_dicts = pickle.load(f)
        else:
            work_items = get_polarion_test_cases()
            self.test_case_dicts = [PolarionWorkItemDict(work_item)
                                    for work_item in work_items]
            self.dump()

    def dump(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.test_case_dicts, f)

    @property
    def pip_test_cases(self):
        return [tc for tc in self.test_case_dicts if tc._pip_recipes_clean]

    @property
    def pip_tests_time_sorted(self):
        dates = np.unique([tc.aiv_date for tc in self.pip_test_cases])
        dates_dic = {date : [] for date in dates}
        for tc in self.pip_test_cases:
            dates_dic[tc.aiv_date].append(tc)
        return dates_dic

    @property
    def pip_recipes_time_unique(self):
        date_dict = {date: test.pip_recipes
                     for date, tests in self.pip_tests_time_sorted.items()
                     for test in tests}
        date_dict = {date : np.unique(recipes)
                     for date, recipes in date_dict.items()}
        return date_dict

    @property
    def pip_recipe_need_dates(self):
        recipes_need_dates = {}
        for date, recipes in self.pip_recipes_time_unique.items():
            for recipe in recipes:
                if recipe not in recipes_need_dates:
                    recipes_need_dates[recipe] = date

        return recipes_need_dates

    def dump_as_yaml(self, filename="test_summary.yaml"):
        tests_lists = [tc.yaml_dict for tc in self.test_case_dicts if tc.pip_recipes]
        if filename:
            with open(filename, "w") as f:
                yaml.dump(tests_lists, f)
        else:
            return yaml.dump(tests_lists)

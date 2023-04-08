import glob

import numpy
import pytest

from ..drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    find_latex_inputs,
    DataItemReference,
)
from ..drld_parser.template_manual import METIS_TemplateManual


class TestDataReductionLibraryDesign:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0

    def test_number_of_dataitems_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.dataitems) > 0

    def test_dataitem_extraction(self):
        """Another way to find the datatimes."""
        sglob = str(METIS_DataReductionLibraryDesign.path_drld / "*.tex")
        paths_tex = glob.glob(sglob)
        lines1 = [
            line
            for path in paths_tex
            for line in open(path).readlines()
            if "paragraph" in line and "dataitem" in line and not line.startswith("%")
        ]
        lines_with_and = [line for line in lines1 if " and " in line]

        is_used = numpy.zeros(len(lines1), dtype=bool)
        not_found = []
        found_more_than_once = []

        # Are all dataitems in the DRLD also in the lines above?
        for di in METIS_DataReductionLibraryDesign.dataitems:
            found = numpy.array([di in line for line in lines1])
            if not found.any():
                not_found.append(di)
            if found.sum() > 1:
                found_more_than_once.append(di)
            is_used |= found

        # Are all lines used for some dataitem?
        not_parsed = [line for line, used in zip(lines1, is_used) if not used]

        assert not not_found
        assert not found_more_than_once
        assert not not_parsed
        assert all(is_used)
        assert len(lines1) + len(lines_with_and) == len(
            METIS_DataReductionLibraryDesign.dataitems
        )

    def test_template_and_recipe_names_do_not_overlap(self):
        names_recipes = {
            name.lower() for name in METIS_DataReductionLibraryDesign.recipes.keys()
        }
        names_templates = {
            name.lower() for name in METIS_TemplateManual.templates.keys()
        }
        assert not (names_recipes & names_templates)

    @pytest.mark.xfail(
        reason="There are several recipes mentioned that do not exist..."
    )
    def test_all_recipe_names_used_also_exist(self):
        names_existing = METIS_DataReductionLibraryDesign.recipes.keys()
        names_used = METIS_DataReductionLibraryDesign.recipe_names_used
        names_existing_lower = [name.lower() for name in names_existing]
        names_not_existing = [
            name
            for name in names_used
            if name not in names_existing and name.lower() not in names_existing_lower
        ]

        assert (
            not names_not_existing
        ), f"Non existing recipe names: {names_not_existing}"

    @pytest.mark.xfail(
        reason="There are references to recipes with incorrect capitalization, e.g. in LSS_data_items.tex."
    )
    def test_all_recipe_names_are_correctly_capitalized(self):
        names_existing = METIS_DataReductionLibraryDesign.recipes.keys()
        names_used = METIS_DataReductionLibraryDesign.recipe_names_used
        names_existing_lower = [name.lower() for name in names_existing]

        names_bad_capitalization = [
            name
            for name in names_used
            if name not in names_existing and name.lower() in names_existing_lower
        ]
        assert (
            not names_bad_capitalization
        ), f"Recipe names with incorrect capitalization: {names_bad_capitalization}"

    @pytest.mark.xfail(
        reason="There are many references to templates that do not exits."
    )
    def test_all_templates_used_also_exist(self):
        # TODO: hack_rename_template_names_drld and
        #  TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI are currently not
        #  used anymore.
        names_existing = METIS_TemplateManual.templates.keys()
        names_used = METIS_DataReductionLibraryDesign.template_names_used
        names_existing_lower = [name.lower() for name in names_existing]
        names_not_existing = [
            name
            for name in names_used
            if name not in names_existing and name.lower() not in names_existing_lower
            # TODO: Do something sensible with *'s in these names.
            and "*" not in name
        ]

        assert (
            not names_not_existing
        ), f"Non existing template names: {names_not_existing}"


class TestFindLatexInputs:
    def test_find_latex_inputs(self):
        fns_expected = [
            "CalDB_data_items.tex",
            "LMS_data_items.tex",
            "IMG_data_items.tex",
            "LSS_data_items.tex",
        ]
        path = (
            METIS_DataReductionLibraryDesign.path_drld / "09_0-DRL-Data-Structures.tex"
        )
        paths_input = find_latex_inputs(path)
        filenames_input = [pp.name for pp in paths_input]
        assert filenames_input == fns_expected


class TestParseDataItemReference:
    def test_parse_dataitem_reference(self):
        diref = DataItemReference.from_recipe_line(
            r"\hyperref[dataitem:nlsssciobjmap]{\PROD{N_LSS_SCI_OBJ_MAP}}: Pixel map of object pixels"
        )
        assert diref.name == "N_LSS_SCI_OBJ_MAP"
        assert diref.dtype == "PROD"
        assert diref.hyperref == "dataitem:nlsssciobjmap"
        assert diref.description == "Pixel map of object pixels"

        diref = DataItemReference.from_recipe_line(
            r"\hyperref[dataitem:nlsswaveguess]{\STATCALIB{N_LSS_WAVE_GUESS}}"
        )
        assert diref.name == "N_LSS_WAVE_GUESS"
        assert diref.dtype == "STATCALIB"
        assert diref.hyperref == "dataitem:nlsswaveguess"
        assert diref.description is None

        diref = DataItemReference.from_recipe_line(r"\PROD{MF\_BEST\_FIT\_TAB}")
        assert diref.name == "MF_BEST_FIT_TAB"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description is None

        diref = DataItemReference.from_recipe_line(
            r"\PROD{N_DIST_REDUCED} (reduced grid mask images)"
        )
        assert diref.name == "N_DIST_REDUCED"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "reduced grid mask images"

        diref = DataItemReference.from_recipe_line(
            "Chopped/nodded science or standard images"
        )
        assert diref.name is None
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "Chopped/nodded science or standard images"

        diref = DataItemReference.from_recipe_line(
            "$N\\times$ \\hyperref[dataitem:nlssrsrfpinhraw]{\\RAW{N_LSS_RSRF_PINH_RAW}}"
        )
        assert diref.name == "N_LSS_RSRF_PINH_RAW"
        assert diref.dtype == "RAW"
        assert diref.hyperref == "dataitem:nlssrsrfpinhraw"
        assert diref.description == "$N\\times$"

        diref = DataItemReference.from_recipe_line(
            "Calibrated science images (\\PROD{LM_SCI_CALIBRATED})"
        )
        assert diref.name == "LM_SCI_CALIBRATED"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "Calibrated science images"

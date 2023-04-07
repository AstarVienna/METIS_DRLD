from ..drld_parser.data_reduction_library_design import METIS_DataReductionLibraryDesign


class TestDataReductionLibraryDesign:

    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0

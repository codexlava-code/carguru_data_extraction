from unittest import TestCase

# custom method added (math formula, type of graph)
from apps.back_end.utils import graph_mode
from apps.back_end.cloud_data import cloud_data_filter

# called the object then called the method to get data
cloud_obj = cloud_data_filter.CloudFilter()
df_days, df_filtered = cloud_obj.get_filter_data("2022-04-10", "2022-04-10", "1Min")


class UtilsFunction(TestCase):
    """_utility method testing_

    Args:
        unittest (_type_): _unit test testcase_
    """

    def setUp(self):
        """_setup all property_"""
        self.date_filtered = df_filtered
        self.formula_selection = "Add"
        self.categories = ["VACUUM"]
        self.sub_categories = ["bp1_water_flow", "bp1_water_temp"]
        self.mode_id = "mode"

    def test_formula_not_none(self):
        """_test formula method existance_"""
        formula = graph_mode.formula_function(
            self.date_filtered, self.formula_selection, self.sub_categories
        )
        self.assertIsNotNone(formula, "this is worked")

    def test_graph_mode_notNone(self):
        """_test graph method existance_"""
        mode = graph_mode.type_selection(
            self.mode_id, self.sub_categories, self.categories
        )
        self.assertIsNotNone(mode, "this is fine")

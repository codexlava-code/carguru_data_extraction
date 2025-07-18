import unittest

# getting cloud data through CloudFilter class
from apps.back_end.cloud_data.cloud_data_filter import CloudFilter


class TestCloudFilter(unittest.TestCase):
    """_ testing all cloud filter methods_"""

    @classmethod
    def setup_class(cls):
        """_it's called once before any of the unit test _"""
        print("Start setup TestCloudFilter\n!")

    @classmethod
    def teardown_class(cls):
        """_it's called once after all method execution _"""
        print("Teardown TestClass!")

    # @unittest.skip
    def setup_method(self, method):
        """_setup function will automatically call before each module method_
        Args:
            method (_type_): _description_
        """
        print("dsfsdfs")
        if method == self.test_column_data:
            print("\nSetting up test1")
        else:
            print("\nSetup method start")

    def teardown_method(self, method):
        """_after execution of each unit it's called teardown method_
        Args:
            method (_type_): _description_
        """
        print("dfsdfdsf")
        if method == self.test_column_data:
            print("\nTearing down test1!")
        else:
            print("\n Teardown method end")

    def cloud_object(self):
        """_call the class make object_"""
        cloud_obj = CloudFilter()  # make a object from the class
        return cloud_obj

    def test_column_data(self):
        """_test column data list_"""
        cloud_obj = self.cloud_object()
        cloud_column_data = cloud_obj.column_data()  # called column_data() method
        self.assertTrue(cloud_column_data, "this is not exist")

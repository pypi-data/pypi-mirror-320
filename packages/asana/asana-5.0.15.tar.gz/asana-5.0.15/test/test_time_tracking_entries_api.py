# coding: utf-8

"""
    Asana

    This is the interface for interacting with the [Asana Platform](https://developers.asana.com). Our API reference is generated from our [OpenAPI spec] (https://raw.githubusercontent.com/Asana/openapi/master/defs/asana_oas.yaml).  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import asana
from asana.api.time_tracking_entries_api import TimeTrackingEntriesApi  # noqa: E501
from asana.rest import ApiException


class TestTimeTrackingEntriesApi(unittest.TestCase):
    """TimeTrackingEntriesApi unit test stubs"""

    def setUp(self):
        self.api = TimeTrackingEntriesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_time_tracking_entry(self):
        """Test case for create_time_tracking_entry

        Create a time tracking entry  # noqa: E501
        """
        pass

    def test_delete_time_tracking_entry(self):
        """Test case for delete_time_tracking_entry

        Delete a time tracking entry  # noqa: E501
        """
        pass

    def test_get_time_tracking_entries_for_task(self):
        """Test case for get_time_tracking_entries_for_task

        Get time tracking entries for a task  # noqa: E501
        """
        pass

    def test_get_time_tracking_entry(self):
        """Test case for get_time_tracking_entry

        Get a time tracking entry  # noqa: E501
        """
        pass

    def test_update_time_tracking_entry(self):
        """Test case for update_time_tracking_entry

        Update a time tracking entry  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()

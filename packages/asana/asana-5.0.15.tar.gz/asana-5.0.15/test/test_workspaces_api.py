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
from asana.api.workspaces_api import WorkspacesApi  # noqa: E501
from asana.rest import ApiException


class TestWorkspacesApi(unittest.TestCase):
    """WorkspacesApi unit test stubs"""

    def setUp(self):
        self.api = WorkspacesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_add_user_for_workspace(self):
        """Test case for add_user_for_workspace

        Add a user to a workspace or organization  # noqa: E501
        """
        pass

    def test_get_workspace(self):
        """Test case for get_workspace

        Get a workspace  # noqa: E501
        """
        pass

    def test_get_workspaces(self):
        """Test case for get_workspaces

        Get multiple workspaces  # noqa: E501
        """
        pass

    def test_remove_user_for_workspace(self):
        """Test case for remove_user_for_workspace

        Remove a user from a workspace or organization  # noqa: E501
        """
        pass

    def test_update_workspace(self):
        """Test case for update_workspace

        Update a workspace  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()

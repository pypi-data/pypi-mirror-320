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
from asana.api.custom_field_settings_api import CustomFieldSettingsApi  # noqa: E501
from asana.rest import ApiException


class TestCustomFieldSettingsApi(unittest.TestCase):
    """CustomFieldSettingsApi unit test stubs"""

    def setUp(self):
        self.api = CustomFieldSettingsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_custom_field_settings_for_portfolio(self):
        """Test case for get_custom_field_settings_for_portfolio

        Get a portfolio's custom fields  # noqa: E501
        """
        pass

    def test_get_custom_field_settings_for_project(self):
        """Test case for get_custom_field_settings_for_project

        Get a project's custom fields  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()

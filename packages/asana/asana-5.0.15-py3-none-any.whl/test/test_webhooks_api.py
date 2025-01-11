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
from asana.api.webhooks_api import WebhooksApi  # noqa: E501
from asana.rest import ApiException


class TestWebhooksApi(unittest.TestCase):
    """WebhooksApi unit test stubs"""

    def setUp(self):
        self.api = WebhooksApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_webhook(self):
        """Test case for create_webhook

        Establish a webhook  # noqa: E501
        """
        pass

    def test_delete_webhook(self):
        """Test case for delete_webhook

        Delete a webhook  # noqa: E501
        """
        pass

    def test_get_webhook(self):
        """Test case for get_webhook

        Get a webhook  # noqa: E501
        """
        pass

    def test_get_webhooks(self):
        """Test case for get_webhooks

        Get multiple webhooks  # noqa: E501
        """
        pass

    def test_update_webhook(self):
        """Test case for update_webhook

        Update a webhook  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()

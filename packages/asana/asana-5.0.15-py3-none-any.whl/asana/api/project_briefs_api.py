# coding: utf-8

"""
    Asana

    This is the interface for interacting with the [Asana Platform](https://developers.asana.com). Our API reference is generated from our [OpenAPI spec] (https://raw.githubusercontent.com/Asana/openapi/master/defs/asana_oas.yaml).  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six
from asana.api_client import ApiClient
from asana.pagination.event_iterator import EventIterator
from asana.pagination.page_iterator import PageIterator

class ProjectBriefsApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def create_project_brief(self, body, project_gid, opts, **kwargs):  # noqa: E501
        """Create a project brief  # noqa: E501

        Creates a new project brief.  Returns the full record of the newly created project brief.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_project_brief(body, project_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param dict body: The project brief to create. (required)
        :param str project_gid: Globally unique identifier for the project. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = kwargs.get("_return_http_data_only", True)
        if kwargs.get('async_req'):
            return self.create_project_brief_with_http_info(body, project_gid, opts, **kwargs)  # noqa: E501
        else:
            (data) = self.create_project_brief_with_http_info(body, project_gid, opts, **kwargs)  # noqa: E501
            return data

    def create_project_brief_with_http_info(self, body, project_gid, opts, **kwargs):  # noqa: E501
        """Create a project brief  # noqa: E501

        Creates a new project brief.  Returns the full record of the newly created project brief.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.create_project_brief_with_http_info(body, project_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param dict body: The project brief to create. (required)
        :param str project_gid: Globally unique identifier for the project. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        all_params = []
        all_params.append('async_req')
        all_params.append('header_params')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('full_payload')
        all_params.append('item_limit')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_project_brief" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if (body is None):
            raise ValueError("Missing the required parameter `body` when calling `create_project_brief`")  # noqa: E501
        # verify the required parameter 'project_gid' is set
        if (project_gid is None):
            raise ValueError("Missing the required parameter `project_gid` when calling `create_project_brief`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['project_gid'] = project_gid  # noqa: E501

        query_params = {}
        query_params = opts


        header_params = kwargs.get("header_params", {})

        form_params = []
        local_var_files = {}

        body_params = body

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json; charset=UTF-8'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json; charset=UTF-8'])  # noqa: E501

        # Authentication setting
        auth_settings = ['personalAccessToken']  # noqa: E501

        # hard checking for True boolean value because user can provide full_payload or async_req with any data type
        if kwargs.get("full_payload", False) is True or kwargs.get('async_req', False) is True:
            return self.api_client.call_api(
                '/projects/{project_gid}/project_briefs', 'POST',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        elif self.api_client.configuration.return_page_iterator:
            (data) = self.api_client.call_api(
                '/projects/{project_gid}/project_briefs', 'POST',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
            if params.get('_return_http_data_only') == False:
                return data
            return data["data"] if data else data
        else:
            return self.api_client.call_api(
            '/projects/{project_gid}/project_briefs', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=object,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_project_brief(self, project_brief_gid, **kwargs):  # noqa: E501
        """Delete a project brief  # noqa: E501

        Deletes a specific, existing project brief.  Returns an empty data record.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_project_brief(project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :return: EmptyResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = kwargs.get("_return_http_data_only", True)
        if kwargs.get('async_req'):
            return self.delete_project_brief_with_http_info(project_brief_gid, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_project_brief_with_http_info(project_brief_gid, **kwargs)  # noqa: E501
            return data

    def delete_project_brief_with_http_info(self, project_brief_gid, **kwargs):  # noqa: E501
        """Delete a project brief  # noqa: E501

        Deletes a specific, existing project brief.  Returns an empty data record.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_project_brief_with_http_info(project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :return: EmptyResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        all_params = []
        all_params.append('async_req')
        all_params.append('header_params')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('full_payload')
        all_params.append('item_limit')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_project_brief" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'project_brief_gid' is set
        if (project_brief_gid is None):
            raise ValueError("Missing the required parameter `project_brief_gid` when calling `delete_project_brief`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['project_brief_gid'] = project_brief_gid  # noqa: E501

        query_params = {}


        header_params = kwargs.get("header_params", {})

        form_params = []
        local_var_files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json; charset=UTF-8'])  # noqa: E501

        # Authentication setting
        auth_settings = ['personalAccessToken']  # noqa: E501

        # hard checking for True boolean value because user can provide full_payload or async_req with any data type
        if kwargs.get("full_payload", False) is True or kwargs.get('async_req', False) is True:
            return self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'DELETE',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        elif self.api_client.configuration.return_page_iterator:
            (data) = self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'DELETE',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
            if params.get('_return_http_data_only') == False:
                return data
            return data["data"] if data else data
        else:
            return self.api_client.call_api(
            '/project_briefs/{project_brief_gid}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=object,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_project_brief(self, project_brief_gid, opts, **kwargs):  # noqa: E501
        """Get a project brief  # noqa: E501

        Get the full record for a project brief.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_project_brief(project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = kwargs.get("_return_http_data_only", True)
        if kwargs.get('async_req'):
            return self.get_project_brief_with_http_info(project_brief_gid, opts, **kwargs)  # noqa: E501
        else:
            (data) = self.get_project_brief_with_http_info(project_brief_gid, opts, **kwargs)  # noqa: E501
            return data

    def get_project_brief_with_http_info(self, project_brief_gid, opts, **kwargs):  # noqa: E501
        """Get a project brief  # noqa: E501

        Get the full record for a project brief.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_project_brief_with_http_info(project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        all_params = []
        all_params.append('async_req')
        all_params.append('header_params')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('full_payload')
        all_params.append('item_limit')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_project_brief" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'project_brief_gid' is set
        if (project_brief_gid is None):
            raise ValueError("Missing the required parameter `project_brief_gid` when calling `get_project_brief`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['project_brief_gid'] = project_brief_gid  # noqa: E501

        query_params = {}
        query_params = opts


        header_params = kwargs.get("header_params", {})

        form_params = []
        local_var_files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json; charset=UTF-8'])  # noqa: E501

        # Authentication setting
        auth_settings = ['personalAccessToken']  # noqa: E501

        # hard checking for True boolean value because user can provide full_payload or async_req with any data type
        if kwargs.get("full_payload", False) is True or kwargs.get('async_req', False) is True:
            return self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'GET',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        elif self.api_client.configuration.return_page_iterator:
            (data) = self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'GET',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
            if params.get('_return_http_data_only') == False:
                return data
            return data["data"] if data else data
        else:
            return self.api_client.call_api(
            '/project_briefs/{project_brief_gid}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=object,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_project_brief(self, body, project_brief_gid, opts, **kwargs):  # noqa: E501
        """Update a project brief  # noqa: E501

        An existing project brief can be updated by making a PUT request on the URL for that project brief. Only the fields provided in the `data` block will be updated; any unspecified fields will remain unchanged.  Returns the complete updated project brief record.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_project_brief(body, project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param dict body: The updated fields for the project brief. (required)
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = kwargs.get("_return_http_data_only", True)
        if kwargs.get('async_req'):
            return self.update_project_brief_with_http_info(body, project_brief_gid, opts, **kwargs)  # noqa: E501
        else:
            (data) = self.update_project_brief_with_http_info(body, project_brief_gid, opts, **kwargs)  # noqa: E501
            return data

    def update_project_brief_with_http_info(self, body, project_brief_gid, opts, **kwargs):  # noqa: E501
        """Update a project brief  # noqa: E501

        An existing project brief can be updated by making a PUT request on the URL for that project brief. Only the fields provided in the `data` block will be updated; any unspecified fields will remain unchanged.  Returns the complete updated project brief record.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_project_brief_with_http_info(body, project_brief_gid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param dict body: The updated fields for the project brief. (required)
        :param str project_brief_gid: Globally unique identifier for the project brief. (required)
        :param list[str] opt_fields: This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
        :return: ProjectBriefResponseData
                 If the method is called asynchronously,
                 returns the request thread.
        """
        all_params = []
        all_params.append('async_req')
        all_params.append('header_params')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('full_payload')
        all_params.append('item_limit')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method update_project_brief" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if (body is None):
            raise ValueError("Missing the required parameter `body` when calling `update_project_brief`")  # noqa: E501
        # verify the required parameter 'project_brief_gid' is set
        if (project_brief_gid is None):
            raise ValueError("Missing the required parameter `project_brief_gid` when calling `update_project_brief`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['project_brief_gid'] = project_brief_gid  # noqa: E501

        query_params = {}
        query_params = opts


        header_params = kwargs.get("header_params", {})

        form_params = []
        local_var_files = {}

        body_params = body

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json; charset=UTF-8'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json; charset=UTF-8'])  # noqa: E501

        # Authentication setting
        auth_settings = ['personalAccessToken']  # noqa: E501

        # hard checking for True boolean value because user can provide full_payload or async_req with any data type
        if kwargs.get("full_payload", False) is True or kwargs.get('async_req', False) is True:
            return self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'PUT',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
        elif self.api_client.configuration.return_page_iterator:
            (data) = self.api_client.call_api(
                '/project_briefs/{project_brief_gid}', 'PUT',
                path_params,
                query_params,
                header_params,
                body=body_params,
                post_params=form_params,
                files=local_var_files,
                response_type=object,  # noqa: E501
                auth_settings=auth_settings,
                async_req=params.get('async_req'),
                _return_http_data_only=params.get('_return_http_data_only'),
                _preload_content=params.get('_preload_content', True),
                _request_timeout=params.get('_request_timeout'),
                collection_formats=collection_formats
            )
            if params.get('_return_http_data_only') == False:
                return data
            return data["data"] if data else data
        else:
            return self.api_client.call_api(
            '/project_briefs/{project_brief_gid}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=object,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

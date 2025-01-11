# coding: utf-8

"""
    Data Repository API

    <details><summary>This document defines the REST API for the Terra Data Repository.</summary> <p> **Status: design in progress** There are a few top-level endpoints (besides some used by swagger):  * / - generated by swagger: swagger API page that provides this documentation and a live UI for submitting REST requests  * /status - provides the operational status of the service  * /configuration - provides the basic configuration and information about the service  * /api - is the authenticated and authorized Data Repository API  * /ga4gh/drs/v1 - is a transcription of the Data Repository Service API  The API endpoints are organized by interface. Each interface is separately versioned. <p> **Notes on Naming** <p> All of the reference items are suffixed with \\\"Model\\\". Those names are used as the class names in the generated Java code. It is helpful to distinguish these model classes from other related classes, like the DAO classes and the operation classes. </details>   # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from data_repo_client.configuration import Configuration


class DuosFirecloudGroupsSyncResponse(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'synced': 'list[DuosFirecloudGroupModel]',
        'errors': 'list[ErrorModel]'
    }

    attribute_map = {
        'synced': 'synced',
        'errors': 'errors'
    }

    def __init__(self, synced=None, errors=None, local_vars_configuration=None):  # noqa: E501
        """DuosFirecloudGroupsSyncResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._synced = None
        self._errors = None
        self.discriminator = None

        if synced is not None:
            self.synced = synced
        if errors is not None:
            self.errors = errors

    @property
    def synced(self):
        """Gets the synced of this DuosFirecloudGroupsSyncResponse.  # noqa: E501

        The Firecloud groups whose contents were successfully updated.   # noqa: E501

        :return: The synced of this DuosFirecloudGroupsSyncResponse.  # noqa: E501
        :rtype: list[DuosFirecloudGroupModel]
        """
        return self._synced

    @synced.setter
    def synced(self, synced):
        """Sets the synced of this DuosFirecloudGroupsSyncResponse.

        The Firecloud groups whose contents were successfully updated.   # noqa: E501

        :param synced: The synced of this DuosFirecloudGroupsSyncResponse.  # noqa: E501
        :type: list[DuosFirecloudGroupModel]
        """

        self._synced = synced

    @property
    def errors(self):
        """Gets the errors of this DuosFirecloudGroupsSyncResponse.  # noqa: E501

        Errors which may have interfered in the syncing for select DUOS Firecloud groups.   # noqa: E501

        :return: The errors of this DuosFirecloudGroupsSyncResponse.  # noqa: E501
        :rtype: list[ErrorModel]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this DuosFirecloudGroupsSyncResponse.

        Errors which may have interfered in the syncing for select DUOS Firecloud groups.   # noqa: E501

        :param errors: The errors of this DuosFirecloudGroupsSyncResponse.  # noqa: E501
        :type: list[ErrorModel]
        """

        self._errors = errors

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DuosFirecloudGroupsSyncResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DuosFirecloudGroupsSyncResponse):
            return True

        return self.to_dict() != other.to_dict()

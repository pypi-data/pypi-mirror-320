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


class EnumerateDatasetModel(object):
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
        'total': 'int',
        'filtered_total': 'int',
        'items': 'list[DatasetSummaryModel]',
        'role_map': 'dict(str, list[str])'
    }

    attribute_map = {
        'total': 'total',
        'filtered_total': 'filteredTotal',
        'items': 'items',
        'role_map': 'roleMap'
    }

    def __init__(self, total=None, filtered_total=None, items=None, role_map=None, local_vars_configuration=None):  # noqa: E501
        """EnumerateDatasetModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._total = None
        self._filtered_total = None
        self._items = None
        self._role_map = None
        self.discriminator = None

        if total is not None:
            self.total = total
        if filtered_total is not None:
            self.filtered_total = filtered_total
        if items is not None:
            self.items = items
        if role_map is not None:
            self.role_map = role_map

    @property
    def total(self):
        """Gets the total of this EnumerateDatasetModel.  # noqa: E501

        Total number of datasets  # noqa: E501

        :return: The total of this EnumerateDatasetModel.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this EnumerateDatasetModel.

        Total number of datasets  # noqa: E501

        :param total: The total of this EnumerateDatasetModel.  # noqa: E501
        :type: int
        """

        self._total = total

    @property
    def filtered_total(self):
        """Gets the filtered_total of this EnumerateDatasetModel.  # noqa: E501

        The number of datasets included in this enumeration  # noqa: E501

        :return: The filtered_total of this EnumerateDatasetModel.  # noqa: E501
        :rtype: int
        """
        return self._filtered_total

    @filtered_total.setter
    def filtered_total(self, filtered_total):
        """Sets the filtered_total of this EnumerateDatasetModel.

        The number of datasets included in this enumeration  # noqa: E501

        :param filtered_total: The filtered_total of this EnumerateDatasetModel.  # noqa: E501
        :type: int
        """

        self._filtered_total = filtered_total

    @property
    def items(self):
        """Gets the items of this EnumerateDatasetModel.  # noqa: E501


        :return: The items of this EnumerateDatasetModel.  # noqa: E501
        :rtype: list[DatasetSummaryModel]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this EnumerateDatasetModel.


        :param items: The items of this EnumerateDatasetModel.  # noqa: E501
        :type: list[DatasetSummaryModel]
        """

        self._items = items

    @property
    def role_map(self):
        """Gets the role_map of this EnumerateDatasetModel.  # noqa: E501

        Map of datasets to the calling user's roles. The key is the dataset ID and the value is a list of role names.   # noqa: E501

        :return: The role_map of this EnumerateDatasetModel.  # noqa: E501
        :rtype: dict(str, list[str])
        """
        return self._role_map

    @role_map.setter
    def role_map(self, role_map):
        """Sets the role_map of this EnumerateDatasetModel.

        Map of datasets to the calling user's roles. The key is the dataset ID and the value is a list of role names.   # noqa: E501

        :param role_map: The role_map of this EnumerateDatasetModel.  # noqa: E501
        :type: dict(str, list[str])
        """

        self._role_map = role_map

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
        if not isinstance(other, EnumerateDatasetModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EnumerateDatasetModel):
            return True

        return self.to_dict() != other.to_dict()

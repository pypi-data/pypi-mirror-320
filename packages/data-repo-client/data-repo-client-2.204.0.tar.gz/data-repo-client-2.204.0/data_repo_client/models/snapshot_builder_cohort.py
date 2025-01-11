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


class SnapshotBuilderCohort(object):
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
        'name': 'str',
        'criteria_groups': 'list[SnapshotBuilderCriteriaGroup]'
    }

    attribute_map = {
        'name': 'name',
        'criteria_groups': 'criteriaGroups'
    }

    def __init__(self, name=None, criteria_groups=None, local_vars_configuration=None):  # noqa: E501
        """SnapshotBuilderCohort - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._criteria_groups = None
        self.discriminator = None

        if name is not None:
            self.name = name
        self.criteria_groups = criteria_groups

    @property
    def name(self):
        """Gets the name of this SnapshotBuilderCohort.  # noqa: E501


        :return: The name of this SnapshotBuilderCohort.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SnapshotBuilderCohort.


        :param name: The name of this SnapshotBuilderCohort.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def criteria_groups(self):
        """Gets the criteria_groups of this SnapshotBuilderCohort.  # noqa: E501


        :return: The criteria_groups of this SnapshotBuilderCohort.  # noqa: E501
        :rtype: list[SnapshotBuilderCriteriaGroup]
        """
        return self._criteria_groups

    @criteria_groups.setter
    def criteria_groups(self, criteria_groups):
        """Sets the criteria_groups of this SnapshotBuilderCohort.


        :param criteria_groups: The criteria_groups of this SnapshotBuilderCohort.  # noqa: E501
        :type: list[SnapshotBuilderCriteriaGroup]
        """
        if self.local_vars_configuration.client_side_validation and criteria_groups is None:  # noqa: E501
            raise ValueError("Invalid value for `criteria_groups`, must not be `None`")  # noqa: E501

        self._criteria_groups = criteria_groups

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
        if not isinstance(other, SnapshotBuilderCohort):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SnapshotBuilderCohort):
            return True

        return self.to_dict() != other.to_dict()

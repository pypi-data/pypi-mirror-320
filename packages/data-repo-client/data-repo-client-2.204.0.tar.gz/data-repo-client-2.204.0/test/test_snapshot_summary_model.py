# coding: utf-8

"""
    Data Repository API

    <details><summary>This document defines the REST API for the Terra Data Repository.</summary> <p> **Status: design in progress** There are a few top-level endpoints (besides some used by swagger):  * / - generated by swagger: swagger API page that provides this documentation and a live UI for submitting REST requests  * /status - provides the operational status of the service  * /configuration - provides the basic configuration and information about the service  * /api - is the authenticated and authorized Data Repository API  * /ga4gh/drs/v1 - is a transcription of the Data Repository Service API  The API endpoints are organized by interface. Each interface is separately versioned. <p> **Notes on Naming** <p> All of the reference items are suffixed with \\\"Model\\\". Those names are used as the class names in the generated Java code. It is helpful to distinguish these model classes from other related classes, like the DAO classes and the operation classes. </details>   # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import data_repo_client
from data_repo_client.models.snapshot_summary_model import SnapshotSummaryModel  # noqa: E501
from data_repo_client.rest import ApiException

class TestSnapshotSummaryModel(unittest.TestCase):
    """SnapshotSummaryModel unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test SnapshotSummaryModel
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = data_repo_client.models.snapshot_summary_model.SnapshotSummaryModel()  # noqa: E501
        if include_optional :
            return SnapshotSummaryModel(
                id = '0', 
                name = 'a', 
                description = '0', 
                created_date = '0', 
                profile_id = '0', 
                storage = [
                    data_repo_client.models.storage_resource_model.StorageResourceModel(
                        region = '0', 
                        cloud_resource = '0', 
                        cloud_platform = 'gcp', )
                    ], 
                secure_monitoring_enabled = True, 
                consent_code = '0', 
                phs_id = 'phs123456', 
                cloud_platform = 'gcp', 
                data_project = '0', 
                storage_account = '0', 
                self_hosted = True, 
                global_file_ids = True, 
                tags = [
                    'a-resource-tag'
                    ], 
                resource_locks = data_repo_client.models.resource_locks.ResourceLocks(
                    exclusive = 'a', 
                    shared = [
                        'a'
                        ], ), 
                duos_id = 'DUOS-123456'
            )
        else :
            return SnapshotSummaryModel(
        )

    def testSnapshotSummaryModel(self):
        """Test SnapshotSummaryModel"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()

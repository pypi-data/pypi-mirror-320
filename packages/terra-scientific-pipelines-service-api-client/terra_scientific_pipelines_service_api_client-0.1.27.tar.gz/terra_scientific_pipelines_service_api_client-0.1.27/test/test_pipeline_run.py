# coding: utf-8

"""
    Terra Scientific Pipelines Service

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from teaspoons_client.models.pipeline_run import PipelineRun

class TestPipelineRun(unittest.TestCase):
    """PipelineRun unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PipelineRun:
        """Test PipelineRun
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PipelineRun`
        """
        model = PipelineRun()
        if include_optional:
            return PipelineRun(
                job_id = '',
                pipeline_name = '',
                status = '',
                description = '',
                time_submitted = '',
                time_completed = ''
            )
        else:
            return PipelineRun(
                job_id = '',
                pipeline_name = '',
                status = '',
                time_submitted = '',
        )
        """

    def testPipelineRun(self):
        """Test PipelineRun"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()

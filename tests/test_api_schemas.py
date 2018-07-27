# -*- coding: UTF-8 -*-
"""
A suite of tests for the HTTP API schemas
"""
import unittest

from jsonschema import Draft4Validator, validate, ValidationError
from vlab_jumpbox_api.lib.views import jumpbox


class TestJumpboxViewSchema(unittest.TestCase):
    """A set of test cases for the schemas of /api/1/inf/jumpbox"""

    def test_post_schema(self):
        """The schema defined for POST on is valid"""
        try:
            Draft4Validator.check_schema(jumpbox.JumpboxView.POST_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete_schema(self):
        """The schema defined for DELETE on is valid"""
        try:
            Draft4Validator.check_schema(jumpbox.JumpboxView.DELETE_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_get_schema(self):
        """The schema defined for GET on is valid"""
        try:
            Draft4Validator.check_schema(jumpbox.JumpboxView.GET_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_post_network_required(self):
        """POST requires users to provide a network"""
        body = {}
        try:
            validate(body, jumpbox.JumpboxView.POST_SCHEMA)
            network_required = False
        except ValidationError:
            network_required = True

        self.assertTrue(network_required)

    def test_post_network(self):
        """POST accepts the parameter 'network'"""
        body = {'network': 'someNetwork'}
        try:
            validate(body, jumpbox.JumpboxView.POST_SCHEMA)
            network_required = True
        except ValidationError:
            network_required = False

        self.assertTrue(network_required)


if __name__ == '__main__':
    unittest.main()

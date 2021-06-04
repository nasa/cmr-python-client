# NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)
#
#     https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
#
# Copyright (c) 2020 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Test cases for the cmr.auth package
Date: 2020-10-15
Since: 0.0
"""

from unittest.mock import patch
import unittest

import test.cmr as util
import cmr.auth.token as token
import cmr.util.common as common

# ******************************************************************************

class TestToken(unittest.TestCase):
    """ Test suit for cmr.auth.token """

    # **********************************************************************
    # Tests

    def test_token_literal(self):
        """
        Test the literal token manager function which returns a token lambda
        """
        expected = "some-token-value"

        # returns a valid token
        manager = token.token_literal(expected)
        actual = manager({})
        self.assertEqual(expected, actual)
        actual = manager(None)
        self.assertEqual(expected, actual)

        # returns no token
        manager = token.token_literal(None)
        actual = manager({})
        self.assertEqual(None, actual)

    def test_token_config(self):
        """ Test the manager which pulls token from the configuration object """
        expected = "some-token-value"

        actual = token.token_config(None)
        self.assertEqual(None, actual)

        actual = token.token_config({})
        self.assertEqual(None, actual)

        actual = token.token_config({'cmr.token.value':expected})
        self.assertEqual(expected, actual)

    def test_token_file(self):
        """
        Test a valid login using the password file lambda with caching on. This
        will require that the test be able to write to a temp directory
        """
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        common.write_file(token_file, expected_token)

        #tests
        options = {'cmr.token.file': token_file}
        self.assertEqual (expected_token, token.token_file(options))

        actual = str(token.token(token.token_file, options))
        self.assertEqual (expected_token, actual)

        actual_token = common.read_file(token_file)
        self.assertEqual(expected_token, actual_token)

        #cleanup
        util.delete_file(token_file)

    def test_bearer(self):
        """Test a that a token can be returned as a Bearer token"""
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        expected_bearer = "Bearer " + expected_token
        common.write_file(token_file, expected_token)

        #tests
        options = {'cmr.token.file': token_file}
        actual = str(token.bearer(token.token_file, options))
        self.assertEqual (expected_bearer, actual, "Token formated as Bearer")

        #cleanup
        util.delete_file(token_file)

    # pylint: disable=W0212 ; test a private function
    def test__env_to_extention(self):
        """Check that the environment->extensions work as expected"""
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, given, msg : self.assertEqual(expected, token._env_to_extention(given), msg)

        test("", None, "No dictionary given")
        test("", {}, "Empty dictionary")
        test("", {"env":None}, "Emtpy value")
        test("", {"env":""}, "Blank value")
        test("", {"env":"ops"}, "Ops specified")
        test("", {"env":"prod"}, "Production specified")
        test("", {"env":"production"}, "Production specified")
        test(".uat", {"env":"uat"}, "UAT specified")
        test(".sit", {"env":"sit"}, "SIT specified")
        test(".future", {"env":"future"}, "Future envirnment")

    # pylint: disable=W0212 ; test a private function
    def test_token_file_env(self):
        """Test the function that returns the token file path"""
        # pylint: disable=C0301 # lambdas must be on one line
        test = lambda expected, config, msg: self.assertEqual(expected, token._token_file_path(config), msg)

        test("~/.cmr_token", None, "Not specified")
        test("~/.cmr_token", {"env" : None}, "None value")
        test("~/.cmr_token", {"env" : ""}, "Empty value")
        test("~/.cmr_token", {"env" : "OPS"}, "OPS specified")
        test("~/.cmr_token.uat", {"env" : "uat"}, "UAT specified")
        test("~/.cmr_token.uat", {"env" : "Uat"}, "UAT, mixed case, specified")
        test("~/.cmr_token.sit", {"env" : "sit"}, "SIT specified")

        test("/tmp/token", {"env": "sit", "cmr.token.file": "/tmp/token"}, "File specified")

    def test_token_file_ignoring_comments(self):
        """
        Test a valid login using the password file lambda. The file itself will
        contain comments to be ignored. This test will require that the test be
        able to write to a temp directory
        """
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        token_file_content = "#ignore this line\n" + expected_token
        common.write_file(token_file, token_file_content)

        #tests
        actual_token = common.read_file(token_file)
        self.assertEqual(token_file_content, actual_token)

        options = {'cmr.token.file': token_file}
        self.assertEqual (expected_token, token.token_file(options))

        actual = str(token.token(token.token_file, options))
        self.assertEqual (expected_token, actual)

        #cleanup
        util.delete_file(token_file)

    @patch('cmr.util.common.execute_command')
    def test_password_manager(self, cmd_mock):
        """ Test a valid login using the password manager """
        expected_token = "Secure-Token"
        options = {}
        cmd_mock.return_value = expected_token
        self.assertEqual(expected_token, token.token_manager(options))

        actual = str(token.token(token.token_manager, options))
        self.assertEqual (expected_token, actual)

    @patch('cmr.util.common.execute_command')
    def test_request_token_two_ways(self, cmd_mock):
        """
        Try to get the token using two different handlers. The file handler
        should fail fall back to the manager which will pass
        """
        options = {'cmr.token.file': "/tmp/__fake-file-never-existed.txt"}
        expected = "Secure-Token"
        cmd_mock.return_value = expected

        # try file first, then manager
        actual = token.token([token.token_manager,token.token_file], options)
        self.assertEqual(expected, actual)

        # try the other way around
        actual = token.token([token.token_file,token.token_manager], options)
        self.assertEqual(expected, actual)

    def test_help_full(self):
        """Test the built in help"""
        result_full = token.help_text()
        self.assertTrue (-1<result_full.find("token_file"))
        self.assertTrue (-1<result_full.find("token("))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = token.help_text("token_")
        self.assertTrue (-1<result_less.find("token_file"))
        self.assertFalse (-1<result_less.find("token()"))

if __name__ == '__main__':
    unittest.main()

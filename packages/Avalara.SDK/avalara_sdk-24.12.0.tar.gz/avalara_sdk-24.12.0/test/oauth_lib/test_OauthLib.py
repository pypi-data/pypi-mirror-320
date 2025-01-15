from time import sleep
from unittest import TestCase
from unittest import mock
import unittest

import urllib3
import urllib
import ssl
import uuid

from pathlib import Path
import sys
import os
from os.path import dirname

d = os.path.dirname(os.getcwd())
sys.path.insert(0, f"{dirname(os.path.dirname(os.getcwd()))}")

import Avalara.SDK.oauth_helper
from Avalara.SDK.oauth_helper import AvalaraCache
from Avalara.SDK.oauth_helper import AvalaraOauth2Client
from Avalara.SDK.oauth_helper import AvalaraApiEnvironment

from Avalara.SDK.exceptions import (
    ApiException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ServiceException,
    ApiValueError,
)


ssl._create_default_https_context = ssl._create_unverified_context


class TestOauthLib(TestCase):
    def setUp(self):
        cache = AvalaraCache()

        self.oauth_client = AvalaraOauth2Client(
            client_id=str(uuid.uuid1()),
            client_secret="",
            required_scopes="",
            avalara_api_environment=AvalaraApiEnvironment.QA,
        )
        self.__test_data__get_access_token_data = self.__generate_test_data(
            "__get_access_token_data"
        )
        self.__get_device_authorization_user_code_data = (
            self.__generate_test_data("__get_device_authorization_user_code")
        )

    @mock.patch.object(
        AvalaraOauth2Client, "_AvalaraOauth2Client__get_access_token_data"
    )
    def test_client_creds_flow(self, mock___get_access_token_data_output):
        mock___get_access_token_data_output.return_value = (
            self.__test_data__get_access_token_data
        )
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        expected__access_token_info = self.__test_data__get_access_token_data
        self.assertEqual(actual_access_token_info, expected__access_token_info)

    @mock.patch.object(
        AvalaraOauth2Client, "_AvalaraOauth2Client__get_access_token_data"
    )
    def test_cache_flow(self, mock___get_access_token_data_output):
        mock___get_access_token_data_output.return_value = (
            self.__test_data__get_access_token_data
        )
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        self.assertEqual(
            self.oauth_client._AvalaraOauth2Client__is_token_returned_from_cache,
            False,
            "Token is not expected to be present in cache",
        )
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        self.assertEqual(
            self.oauth_client._AvalaraOauth2Client__is_token_returned_from_cache,
            True,
            "Token is expected to be present in cache",
        )

    @mock.patch.object(
        AvalaraOauth2Client, "_AvalaraOauth2Client__get_access_token_data"
    )
    def test_cache_expiration(self, mock___get_access_token_data_output):
        self.__test_data__get_access_token_data["expires_in"] = 10
        self.oauth_client._AvalaraOauth2Client__token_renewal_seconds_before_ttl_end = (
            5
        )
        mock___get_access_token_data_output.return_value = (
            self.__test_data__get_access_token_data
        )
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        self.assertEqual(
            self.oauth_client._AvalaraOauth2Client__is_token_returned_from_cache,
            False,
            "Token is not expected to be present in cache",
        )
        token_data = self.oauth_client.cache.get(self.oauth_client.client_id)
        self.assertIsNotNone(
            token_data[0]["access_token"],
            msg="Access token is expected but none found",
        )
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        self.assertEqual(
            self.oauth_client._AvalaraOauth2Client__is_token_returned_from_cache,
            True,
            "Token is expected to be present in cache",
        )
        token_data = self.oauth_client.cache.get(self.oauth_client.client_id)
        self.assertIsNotNone(
            token_data[0]["access_token"],
            msg="Access token is expected but none found",
        )
        sleep(15)
        self.__test_data__get_access_token_data["expires_in"] = 60
        actual_access_token_info = (
            self.oauth_client.get_avalara_access_token_info()
        )
        self.assertEqual(
            self.oauth_client._AvalaraOauth2Client__is_token_returned_from_cache,
            False,
            "Token is not expected to be present in cache",
        )
        token_data = self.oauth_client.cache.get(self.oauth_client.client_id)
        self.assertIsNotNone(
            token_data[0]["access_token"],
            msg="Access token is expected but none found",
        )

    def test_oauth_retry_on_http_401_error(self):
        vars = {'execution_count': 0, 'max_retry_attempts_to_test': 3}
        max_retry_attempts_to_test = 3

        @Avalara.SDK.oauth_helper.avalara_retry_oauth(
            max_retry_attempts=max_retry_attempts_to_test
        )
        def method_for_test():
            try:
                vars["execution_count"] += 1
                execution_count = vars["execution_count"]
                if execution_count < max_retry_attempts_to_test:
                    raise UnauthorizedException()
            except UnauthorizedException as e:
                raise e

        try:
            method_for_test()
        except Exception as e:
            print(f"Expecting exception HTTPError: \n {str(e)}")
            pass
        finally:
            self.assertEqual(
                max_retry_attempts_to_test,
                vars["execution_count"],
                "Avalara oauth retry attempts are not executed as expected",
            )

    def test_oauth_retry_on_http_403_error(self):
        vars = {'execution_count': 0, 'max_retry_attempts_to_test': 3}
        max_retry_attempts_to_test = 3

        @Avalara.SDK.oauth_helper.avalara_retry_oauth(
            max_retry_attempts=max_retry_attempts_to_test
        )
        def method_for_test():
            try:
                vars["execution_count"] += 1
                execution_count = vars["execution_count"]
                if execution_count < max_retry_attempts_to_test:
                    raise ForbiddenException()
            except ForbiddenException as e:
                raise e

        try:
            method_for_test()
        except Exception as e:
            pass
        finally:
            self.assertEqual(
                max_retry_attempts_to_test,
                vars["execution_count"],
                "Avalara oauth retry attempts are not executed as expected",
            )

    def test_oauth_retry_on_non_http_403_or_401_error(self):
        vars = {'execution_count': 0}
        max_retry_attempts_to_test = 3

        @Avalara.SDK.oauth_helper.avalara_retry_oauth(
            max_retry_attempts=max_retry_attempts_to_test
        )
        def method_for_test():
            vars["execution_count"] += 1
            execution_count = vars["execution_count"]
            if execution_count < max_retry_attempts_to_test:
                err = urllib3.ConnectionError()
                raise err

        try:
            method_for_test()
        except Exception as e:
            pass
        finally:
            self.assertRaises(ConnectionError)

    # @mock.patch.object(
    #     AvalaraOauth2Client,
    #     "_AvalaraOauth2Client__get_device_authorization_user_code",
    # )
    def test_device_authorization_flow(self):
        self.oauth_client.client_id = ""
        device_authorization_code_info = (
            self.oauth_client.initiate_device_authorization_flow()
        )
        print(device_authorization_code_info)

    def tearDown(self):
        # print("Performing cleanup ........")
        # print("Cleanup complete !")
        pass

    def __generate_test_data(self, operation):

        if operation == "__get_access_token_data":
            test_data = {
                "access_token": "test_access_token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "scope": "avatax_api",
            }
        elif operation == "__get_device_authorization_user_code":
            user_code = "T+test00"
            base_url = self.oauth_client.oauth2_config.avalara_oidc_data.issuer
            test_data = {
                'device_code': 'test_device_code',
                'user_code': user_code,
                'verification_uri': f'{base_url}/device',
                'verification_uri_complete': f'{base_url}/device?userCode={user_code}',
                'expires_in': 300,
                'interval': 5,
            }
        return test_data


def get_tests():
    test_funcs = [
        "test_client_creds_flow",
        "test_cache_flow",
        "test_cache_expiration",
        "test_oauth_retry_on_http_401_error",
        "test_oauth_retry_on_http_403_error",
        "test_oauth_retry_on_non_http_403_or_401_error",
    ]
    return [TestOauthLib(func) for func in test_funcs]


if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    tests = get_tests()
    test_suite.addTests(tests)
    unittest.runner.TextTestRunner().run(test_suite)

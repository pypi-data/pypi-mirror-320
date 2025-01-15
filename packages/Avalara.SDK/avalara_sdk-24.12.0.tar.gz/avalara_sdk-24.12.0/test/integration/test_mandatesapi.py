from math import fabs
import unittest
import pytest
import ssl
import time
import Avalara.SDK
from Avalara.SDK import api_client
from Avalara.SDK.api.EInvoicing.V1.mandates_api import MandatesApi  # noqa: E501
from Avalara.SDK.oauth_helper import AvalaraOauth2Client

import os
from dotenv import load_dotenv

# @pytest.mark.usefixtures("params")
class TestMandatesApi(unittest.TestCase):
    """MandatesApi unit test stubs"""

    def setUp(self):
        load_dotenv()
        # ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL
        configuration = Avalara.SDK.Configuration(
            environment="sandbox",
            access_token=os.getenv('BEARER_TOKEN')
        )
        with Avalara.SDK.ApiClient(configuration) as api_client:
            self.api = MandatesApi(api_client)

    def tearDown(self):
        pass

    def test_get_documents(self):
        try:
            result = self.api.get_mandates("1.2")
            print(result)
            assert result is not None, "Result should not be None"
        except Avalara.SDK.ApiException as e:
            print("Exception when calling MandatesApi->get_mandates: %s\n" % e)
            assert False

        print("Completed")
        pass


if __name__ == '__main__':
    unittest.main()
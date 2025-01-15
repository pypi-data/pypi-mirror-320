from math import fabs
import unittest
import pytest
import ssl
import time
import Avalara.SDK
from Avalara.SDK import api_client
from Avalara.SDK.api.EInvoicing.V1.documents_api import DocumentsApi  # noqa: E501
from Avalara.SDK.oauth_helper import AvalaraOauth2Client

import os
from dotenv import load_dotenv

# @pytest.mark.usefixtures("params")
class TestDocumentsApi(unittest.TestCase):
    """DocumentsApi unit test stubs"""

    def setUp(self):
        load_dotenv()
        configuration = Avalara.SDK.Configuration(
            environment="sandbox",
            access_token=os.getenv('BEARER_TOKEN')
        )
        with Avalara.SDK.ApiClient(configuration) as api_client:
            self.api = DocumentsApi(api_client)

    def tearDown(self):
        pass

    def test_get_documents(self):
        try:
            result = self.api.get_document_list("1.2")
            print(result)
            assert result is not None, "Result should not be None"
        except Avalara.SDK.ApiException as e:
            print("Exception when calling DocumentsApi->get_document_list: %s\n" % e)
            assert False

        print("Completed")
        pass


if __name__ == '__main__':
    unittest.main()
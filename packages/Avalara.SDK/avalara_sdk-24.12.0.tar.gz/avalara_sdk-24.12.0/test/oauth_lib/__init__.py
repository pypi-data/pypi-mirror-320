# import sys
# from pathlib import Path

# print("File      Path:", Path(__file__).absolute())
# print(
#     "Directory Path:", Path().absolute()
# )  # Directory of current working directory, not __file__

# # # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(0,  f"{ Path().absolute()}/Avalara_oauth_helper")

# from Avalara_oauth_helper.AvalaraSdkOauthUtils import (
#     avalara_retry_oauth,
#     AVALARA_SDK_CONSTANTS,
#     AvalaraApiEnvironment,
# )
# from Avalara_oauth_helper.AvalaraOauth2Configuration import (
#     AvalaraOauth2Configuration,
# )
# from Avalara_oauth_helper.AvalaraOidcModel import (
#     AvalaraOidcModel,
# )
# from Avalara_oauth_helper.AvalaraOauth2Client import (
#     AvalaraOauth2Client,
# )
# from ..Avalara_oauth_helper.AvalaraCache import (
#     AvalaraCache,
# )

# avalara_cache = AvalaraCache()
# avalara_cache.set_item_with_ttl("test1", "test1", 20)
# avalara_cache.set_item_with_ttl("test2", "test2", 30)
# avalara_cache.delete_item_from_cache("test1")
# avalara_cache.delete_item_from_cache("test1123")

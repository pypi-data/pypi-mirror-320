"""
API客户端
"""
import os

from paddlehelix.api.api_common import CommonClient
from paddlehelix.api.api_helixfold3 import HelixFold3Client


_missing_sk_sk_message = """
        未配置用户身份验证信息AK、SK，请设置环境变量 PADDLEHELIX_API_AK、PADDLEHELIX_API_SK，设置方式如下：
        export PADDLEHELIX_API_AK="your_access_key"
        export PADDLEHELIX_API_SK="your_secret_key"
    """
_ak, _sk = os.getenv("PADDLEHELIX_API_AK", ""), os.getenv("PADDLEHELIX_API_SK", "")
assert len(_ak) > 0 and len(_sk) > 0, _missing_sk_sk_message


class APIClient:
    Common = CommonClient(_ak, _sk)
    HelixFold3 = HelixFold3Client(_ak, _sk)



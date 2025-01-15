"""
HelixFold3模型API调用
"""
from typing import Any

import requests

from paddlehelix.api.auth import APIAuthUtil
from paddlehelix.api.code import ErrorCode
from paddlehelix.api.config import HOST, SCHEME
from paddlehelix.api.registry import ServerAPIRegistry
from paddlehelix.api.structures import SubmitTaskResponse, BatchSubmitTaskResponse
from paddlehelix.utils import file_util
from paddlehelix.version.structures import list_type, dict_type


class HelixFold3Client:
    def __init__(self, ak: str = "", sk: str = ""):
        self._ak = ak
        self._sk = sk
        self.__authClient = APIAuthUtil(ak, sk)

    def submit(self, data: dict = None, **kwargs) -> SubmitTaskResponse:
        """
        HelixFold3任务提交API
        :param data:
            examples:
                {
                    "entities": [
                        {
                            "type": "ion",
                            "count": 2,
                            "ccd": "CA"
                        }
                    ],
                    "recycle": 20,
                    "ensemble": 10,
                    "job_name": "test-demo"
                }
        :return:
            examples:
                {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "task_id": 65593
                    }
                }
        """
        # 尝试从JSON文件中加载数据
        file_path = kwargs.get("file_path", "")
        if len(file_path) > 0:
            data = file_util.parse_json_from_file(file_path)
        if data is None or len(data) == 0:
            return SubmitTaskResponse(code=ErrorCode.FAILURE.value, msg="", data=None)
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.HelixFold3.submit.uri]),
                                 headers=self.__authClient.generate_header(ServerAPIRegistry.HelixFold3.submit.uri),
                                 json=data)
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("code") == ErrorCode.SUCCESS.value:
                return SubmitTaskResponse(
                    code=ErrorCode.SUCCESS.value,
                    msg=resp_json.get("msg", ""),
                    data=resp_json.get("data", None)
                )
            else:
                return SubmitTaskResponse(
                    code=ErrorCode.FAILURE.value,
                    msg=resp_json.get("msg", "")
                )
        return SubmitTaskResponse(code=ErrorCode.FAILURE.value, msg="")

    def batch_submit(self, data: list_type[dict_type[str, Any]] = None, **kwargs) -> BatchSubmitTaskResponse:
        """
        HelixFold3任务批量提交API
        :param data:
            examples:
                [
                    {
                        "entities": [
                            {
                                "type": "ion",
                                "count": 2,
                                "ccd": "CA"
                            }
                        ],
                        "recycle": 20,
                        "ensemble": 10,
                        "job_name": "test-demo"
                    },
                    {xxx}
                ]
        :return:
            examples:
                [
                    {
                        "code": 0,
                        "msg": "",
                        "data": {
                            "task_id": 65593
                        }
                    }
                ]
        """
        if data is None or len(data) <= 0:
            BatchSubmitTaskResponse(code=ErrorCode.FAILURE.value, msg="", data=None)
        json_data = {
            "tasks": data
        }
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.HelixFold3.batch_submit.uri]),
                                 headers=self.__authClient.generate_header(ServerAPIRegistry.HelixFold3.batch_submit.uri),
                                 json=json_data)
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("code") == ErrorCode.SUCCESS.value:
                return BatchSubmitTaskResponse(
                    code=ErrorCode.SUCCESS.value,
                    msg=resp_json.get("msg", ""),
                    data=resp_json.get("data", None)
                )
            else:
                return BatchSubmitTaskResponse(
                    code=ErrorCode.FAILURE.value,
                    msg=resp_json.get("msg", "")
                )
        return BatchSubmitTaskResponse(code=ErrorCode.FAILURE.value, msg="")

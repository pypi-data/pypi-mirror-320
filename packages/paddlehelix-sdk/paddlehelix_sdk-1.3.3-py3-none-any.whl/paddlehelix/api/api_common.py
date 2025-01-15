"""
通用API调用，例如查询任务执行结果
"""

from typing import Any

import requests
import time

from paddlehelix.api.auth import APIAuthUtil
from paddlehelix.api.code import ErrorCode
from paddlehelix.api.config import HOST, SCHEME
from paddlehelix.api.config import QUERY_BATCH_NUM, QUERY_BATCH_INTERVAL
from paddlehelix.api.config import QUERY_PRICE_BATCH_DATA_NUM, QUERY_PRICE_RETRY_COUNT, QUERY_PRICE_RETRY_INTERVAL
from paddlehelix.api.registry import ServerAPIRegistry
from paddlehelix.api.structures import QueryTaskInfoResponse, QueryTaskPriceResponse, CancelTaskResponse
from paddlehelix.api.task import TaskUtil
from paddlehelix.utils import file_util
from paddlehelix.version.structures import list_type, dict_type


class CommonClient:
    def __init__(self, ak: str = "", sk: str = ""):
        self._ak = ak
        self._sk = sk
        self.__authClient = APIAuthUtil(ak, sk)

    def cancel_task(self, task_id: int = 0, **kwargs) -> CancelTaskResponse:
        """
        取消任务
        :param task_id: 任务ID
        """
        if task_id <= 0:
            raise f"The parameter task_id {task_id} is not valid."
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.Common.cancel_task.uri]),
                                 headers=self.__authClient.generate_header(ServerAPIRegistry.Common.cancel_task.uri),
                                 json={"task_id": task_id})
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("code") == ErrorCode.SUCCESS.value:
                return CancelTaskResponse(code=ErrorCode.SUCCESS.value, msg=resp_json.get("msg", ""))
            else:
                return CancelTaskResponse(code=ErrorCode.FAILURE.value, msg=resp_json.get("msg", ""))
        return CancelTaskResponse(code=ErrorCode.FAILURE.value, msg="")

    # def batch_cancel_task(self, task_ids: list = None, **kwargs):
    #     """
    #     批量取消任务
    #     :param task_ids: 任务ID列表
    #     """
    #     if task_ids is None or len(task_ids) <= 0:
    #         return
    #     for task_id in task_ids:
    #         requests.post("".join([SCHEME, HOST, ServerAPIRegistry.Common.cancel_task.uri]),
    #                       headers=self.__authClient.generate_header(ServerAPIRegistry.Common.cancel_task.uri),
    #                       json={"task_id": task_id})

    def query_task_info(self, task_id: int = 0, **kwargs) -> QueryTaskInfoResponse:
        """
        HelixFold3查询任务处理结果API
        :param task_id: 任务ID
        :return:
            examples:
                {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "status": 10, # 2 -> 运行中，1 -> 完成，-1 -> 失败
                        "run_time", 10,
                        "result": "{"download_url":"https://"}"
                    }
                }
        """
        if task_id <= 0:
            return QueryTaskInfoResponse(code=ErrorCode.FAILURE.value, msg="", data=None)
        response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.Common.query_task_info.uri]),
                                 headers=self.__authClient.generate_header(
                                     ServerAPIRegistry.Common.query_task_info.uri),
                                 json={"task_id": task_id})
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("code") == ErrorCode.SUCCESS.value:
                return QueryTaskInfoResponse(code=ErrorCode.SUCCESS.value,
                                             msg=resp_json.get("msg", ""),
                                             data=resp_json.get("data", None)
                                             )
        return QueryTaskInfoResponse(code=ErrorCode.FAILURE.value, msg="", data=None)

    def query_task_infos(self, task_ids: list_type[int] = None, **kwargs) -> list_type[QueryTaskInfoResponse]:
        """
        HelixFold3批量查询任务处理结果API
        :param task_ids: 任务ID列表
        :return:
            examples:
                [
                    {
                        "code": 0,
                        "msg": "",
                        "data": {
                            "status": 10, # 10:运行中，20:取消，30:完成，40:失败
                            "run_time", 10,
                            "result": "{"download_url":"https://"}"
                        }
                    }
                ]
        """
        res = []
        if task_ids is None or len(task_ids) <= 0:
            return res
        task_counter = 0
        for task_id in task_ids:
            response = requests.post("".join([SCHEME, HOST, ServerAPIRegistry.Common.query_task_info.uri]),
                                     headers=self.__authClient.generate_header(
                                         ServerAPIRegistry.Common.query_task_info.uri),
                                     json={"task_id": task_id})
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") == ErrorCode.SUCCESS.value:
                    res.append(QueryTaskInfoResponse(
                        code=ErrorCode.SUCCESS.value,
                        msg=resp_json.get("msg", ""),
                        data=resp_json.get("data", None)))
                else:
                    res.append(QueryTaskInfoResponse(code=ErrorCode.FAILURE.value, msg="", data=None))
            task_counter += 1
            if task_counter % QUERY_BATCH_NUM == 0:
                time.sleep(QUERY_BATCH_INTERVAL)
        return res

    def download_task_result(self, save_dir: str, task_id: int) -> str:
        """
        下载任务结果
        :param save_dir: 保存目录
        :param task_id: 任务ID
        :return: 文件保存目录 download_dir + '/' + task_id
        """
        try:
            file_util.create_directories(save_dir)
        except RuntimeError:
            return ""
        task_info = self.query_task_info(task_id)
        if task_info.code != ErrorCode.SUCCESS.value:
            return ""
        file_util.clear_dir(save_dir)
        download_url = task_info.data.get_download_url()
        if len(download_url) > 0:
            file_util.download_file(save_dir, file_util.parse_filename_from_url(download_url), download_url)
        return save_dir

    def download_task_results(self, save_dir: str, task_ids: list_type[int]) -> list_type[str]:
        """
        批量下载任务结果
        :param save_dir: 保存目录
        :param task_ids: 任务ID列表
        :return: 文件保存目录列表，对于每个task的结果文件，保存目录为 download_dir + '/' + task_id
        """
        res = []
        for task_id in task_ids:
            res.append(self.download_task_result(save_dir, task_id))
        return res

    def query_task_prices(self,
                          data: dict_type[str, Any] = None,
                          data_list: list_type[dict_type[str, Any]] = None,
                          **kwargs) -> list_type[QueryTaskPriceResponse]:
        task_name = kwargs.get("task_name")
        # check common param
        assert isinstance(task_name, str), "The parameter task_name is not of str type."
        if task_name != ServerAPIRegistry.HelixFold3.name:
            raise ValueError("The parameter task_name {task_name} is not supported.")
        # check task param
        task_list = TaskUtil.parse_task_data_list_from_all_kinds_input(data, data_list, **kwargs)
        if len(task_list) <= 0:
            raise ValueError("The task data is empty.")
        # query task price
        res = []
        uri = ServerAPIRegistry.HelixFold3.batch_submit.uri + "/price"
        for i in range(0, len(task_list), QUERY_PRICE_BATCH_DATA_NUM):
            data_list = []
            for task in task_list[i:i + QUERY_PRICE_BATCH_DATA_NUM]:
                data_list.append(task.data)
            json_data = {
                "tasks": data_list
            }
            # 如果请求失败，重试最多三次
            retry_count = QUERY_PRICE_RETRY_COUNT
            succ = False
            msg = ""
            while retry_count > 0:
                try:
                    response = requests.post("".join([SCHEME, HOST, uri]),
                                            headers=self.__authClient.generate_header(uri),
                                            json=json_data)
                    if response.status_code == 200:
                        resp_json = response.json()
                        if resp_json.get("code") == ErrorCode.SUCCESS.value:
                            res.append(QueryTaskPriceResponse(
                                code=ErrorCode.SUCCESS.value,
                                msg=resp_json.get("msg", ""),
                                data=resp_json.get("data", None)))
                            succ = True
                            break
                        else:
                            msg = resp_json.get("msg", "")
                    else:
                        msg = response.text
                    time.sleep(QUERY_PRICE_RETRY_INTERVAL)
                    retry_count -= 1
                except Exception as e:
                    msg = e.__str__()
                    time.sleep(QUERY_PRICE_RETRY_INTERVAL)
                    retry_count -= 1
            if not succ:
                res = []
                res.append(QueryTaskPriceResponse(code=ErrorCode.FAILURE.value, msg=msg, data=dict()))
       
        responses = []
        total_price = 0.0
        prices = []
        msg = ""
        code = ErrorCode.SUCCESS.value
        for response in res:
            if response.code == ErrorCode.SUCCESS.value:
                for price in response.data.prices:
                    prices.append(dict(
                        name=price.name,
                        price=price.price
                    ))
                total_price += response.data.total_prices
            else:
                code = ErrorCode.FAILURE.value
                msg = response.msg
                total_price = 0.0
                prices = []
                break
        temp_response = QueryTaskPriceResponse(
            code=code,
            msg=msg,
            data=dict(
                    prices=prices,
                    total_amount=total_price
                )
            )
        responses.append(temp_response)
        return responses

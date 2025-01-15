"""
存放各种API对应的请求、响应体数据结构
"""

import json

from paddlehelix.version.structures import list_type, dict_type


class SubmitTaskResponse:
    def __init__(self, code: int = 0, msg: str = "", data: dict_type = None):
        self.code = code
        self.msg = msg
        self.data = self.Data(data)

    class Data:
        def __init__(self, sub_data: dict_type = None):
            self.task_id = sub_data["task_id"] if sub_data is not None else 0

        def to_json(self):
            return {
                "task_id": self.task_id
            }

    def to_json(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data.to_json()
        }


class BatchSubmitTaskResponse:
    def __init__(self, code: int = 0, msg: str = "", data: dict_type = None):
        self.code = code
        self.msg = msg
        self.data = self.Data(data)

    class Data:
        def __init__(self, sub_data: dict_type = None):
            self.task_ids = sub_data["task_ids"] if sub_data is not None else None

    #     def to_json(self):
    #         return {
    #             "task_ids": self.task_ids
    #         }
    #
    # def to_json(self):
    #     return {
    #         "code": self.code,
    #         "msg": self.msg,
    #         "data": self.data.to_json()
    #     }


class QueryTaskInfoResponse:
    def __init__(self, code: int = 0, msg: str = "", data: dict_type = None):
        self.code = code
        self.msg = msg
        self.data = self.Data(data)

    class Data:
        def __init__(self, sub_data: dict_type = None):
            self.status = sub_data.get("status", 0) if sub_data else 0
            self.run_time = sub_data.get("run_time", 0) if sub_data else 0
            self.result = sub_data.get("result", "") if sub_data else ""

            self.__result_dict = None
            if len(self.result) > 0:
                self.__result_dict = json.loads(self.result)

        def get_download_url(self) -> str:
            if self.__result_dict is not None:
                return self.__result_dict['download_url']
            return ""

        def to_json(self):
            return {
                "status": self.status,
                "run_time": self.run_time,
                "result": self.result
            }

    def to_json(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data.to_json()
        }


class TaskPrice:
    def __init__(self, data: dict_type = None):
        self.prices = self.Data.parse_prices(data)
        self.total_prices = data.get("total_amount", 0)

    def to_json(self):
        price_infos = []
        for price in self.prices:
            price_infos.append(price.to_json())
        return \
            f"""
            total_prices: {self.total_prices}
            prices: [{", ".join(price_infos)}]
            """

    class Data:
        def __init__(self, sub_data: dict_type = None):
            self.name = sub_data.get("name", "") if sub_data is not None else ""
            self.price = sub_data.get("price", "") if sub_data is not None else 0

        def to_json(self):
            return f"""name: {self.name} price: {self.price}"""

        @staticmethod
        def parse_prices(sub_data: dict_type = None) -> list_type:
            if sub_data is None:
                return []
            res = []
            if "prices" in sub_data:
                prices = sub_data.get("prices")
                for price in prices:
                    res.append(TaskPrice.Data(price))
            return res


class QueryTaskPriceResponse:
    def __init__(self, code: int = 0, msg: str = "", data: dict_type = None):
        self.code = code
        self.msg = msg
        self.data = TaskPrice(data)


class CancelTaskResponse:
    def __init__(self, code: int = 0, msg: str = "", data: dict_type = None):
        self.code = code
        self.msg = msg
        self.data = data

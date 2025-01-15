"""
公共请求变量
"""

# 请求变量
SCHEME = "http://"
HOST = "chpc.bj.baidubce.com"


# 任务状态
ApiTaskStatusDoing = 2  # 运行中
ApiTaskStatusCancel = 3  # 取消
ApiTaskStatusSucc = 1  # 成功
ApiTaskStatusFailed = -1  # 执行失败
ApiTaskStatusSubmitFailed = -2  # 提交失败
ApiTaskStatusUnknown = 0  # 未知状态

STATUS_TO_STR = {
    ApiTaskStatusSubmitFailed: "Task Submission Failed",
    ApiTaskStatusFailed: "Task Execution Failed",
    ApiTaskStatusSucc: "Task Executed Successfully",
    ApiTaskStatusDoing: "Task is Being Executed",
    ApiTaskStatusCancel: "Task Cancelled",
    ApiTaskStatusUnknown: "Unknown Task Status"
}


# 提交任务参数
DEFAULT_TASK_COUNT_ONE_BATCH = 10
MAX_TASK_COUNT_ONE_BATCH = 20
DEFAULT_SUBMIT_INTERVAL = 5


# 轮询任务参数
DEFAULT_POLLING_INTERVAL_SECONDS = 30
MIN_POLLING_INTERVAL_SECONDS = 2

# query params
QUERY_BATCH_NUM = 50
QUERY_BATCH_INTERVAL = 15

# 询价单批次数量
QUERY_PRICE_BATCH_DATA_NUM = 100
QUERY_PRICE_RETRY_COUNT = 3
QUERY_PRICE_RETRY_INTERVAL = 3
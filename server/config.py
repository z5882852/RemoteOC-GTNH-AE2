import os
from dotenv import load_dotenv
from callback import *
from action import *

__version__ = "1.1.0"

# 加载 .env 文件中的环境变量
if os.path.exists('.env.dev'):
    load_dotenv('.env.dev')
load_dotenv()


# 定时任务设置
timer_task_config = {
    # "timer_task_1": {  # 键名为任务名，用于查询，可自定义
    #     'interval': 15,  # 定时器间隔(秒)
    #     'client_id': 'client_01',  # 指定执行命令的OC客户端id
    #     'commands': [  # 远程执行的命令列表
    #         "return 114514",
    #     ],
    #     # 命令执行后的回调函数，callback(results: list)
    #     'callback': test,
    # },
    # "monitor": {
    #     'interval': 300,
    #     "client_id": "client_01",
    #     "commands": [
    #         "return getCapacitorInfo()",  # 获取兰波顿电容库数据
    #     ],
    #     "cache": True,
    #     "handle": parse_data,
    #     "callback": None,
    #     "save_history": True,  # 是否保存历史记录
    #     "history_days": 7,  # 历史记录最大保存天数
    # },
}


# 任务组设置，该任务执行结束后会调用callback，该任务记录不会被清除
task_config = {
    "getCpuDetailList": {  # 获取CPU详细信息列表
        "client_id": "client_01",  # 指定执行命令的OC客户端id
        "commands": [  # 远程执行的命令列表
            "return ae.getCpuList(true)",
        ],
        "cache": True,
        "handle": None,
        "callback": None,
    },
    "getCpuList": {  # 获取CPU简易信息列表
        "client_id": "client_01",
        "commands": [
            "return ae.getCpuList()",
        ],
        "cache": True,
        "handle": None,
        "callback": None,
    },
    "getAllItems": {  # 获取AE网络里所有物品信息
        "client_id": "client_01",
        "commands": [
            "return ae.getAllItems()",
        ],
        "cache": True,
        "handle": None,
        "callback": None,
        "chunked": True,  # 由于数据量过大，启用分块上传。
    },
    "getAllSilempleItems": {  # 获取AE网络里所有物品信息
        "client_id": "client_01",
        "commands": [
            "return ae.getAllSilempleItems()",
        ],
        "cache": True,
        "handle": None,
        "callback": None,
        "chunked": True,
    },
    "getAllCraftables": {  # 获取AE网络里所有可合成的物品信息
        "client_id": "client_01",
        "commands": [
            "return ae.getAllCraftables()",
        ],
        "cache": True,
        "handle": None,
        "callback": None,
    },
    "getAllCraftablesAndCpus": {  # 获取AE网络里所有可合成的物品信息和CPU信息
        "client_id": "client_01",
        "commands": ["return ae.getAllCraftables()", "return ae.getCpuList()"],
        "cache": True,
        "handle": None,
        "callback": None,
    },
}


# 触发器设置
trigger_config = {
    "CPU空闲时": {
        "interval": 180,  # 任务执行间隔
        "description": "当CPU空闲时执行任务",
        "task": {
            # 用占位符{xxx}表示参数，用于动态替换
            "task_id": None,  # 任务 ID, None 则自动生成
            "client_id": "{client_id}",
            "commands": [
                "return ae.getCpuInfoByName('{cpu_name}')",
            ],
            "handle": check_cpu_free,  # 返回值为 True 时执行任务
        },
        "args": [
            # tpye: str, int, float, bool
            {
                "key": "client_id",
                "field": "client_id",
                "type": "str",
                "default": "",
                "description": "客户端 ID",
            },
            {
                "key": "cpu_name",
                "field": "cpu_name",
                "type": "str",
                "description": "CPU 名称",
            },
        ],
        # 可选操作列表
        "actions": {
            "craft": {
                "name": "合成物品",
                "description": "向OC客户端发送合成物品请求",
                "function": craft_item,
                "args": [
                    {
                        "field": "client_id",
                        "type": "str",
                        "default": "",
                        "description": "客户端 ID",
                    },
                    {
                        "field": "item_name",
                        "type": "str",
                        "description": "name",
                    },
                    {
                        "field": "item_damage",
                        "type": "int",
                        "description": "damage",
                    },
                    {
                        "field": "item_amount",
                        "type": "int",
                        "default": 1,
                        "description": "数量",
                    },
                    {
                        "field": "cpu_name",
                        "type": "str",
                        "default": None,
                        "description": "指定合成的CPU",
                    },
                    {
                        "field": "label",
                        "type": "str",
                        "default": None,
                        "description": "label",
                    },
                ],
            },
            "http_request": {
                "name": "发送 HTTP 请求",
                "description": "向指定地址发送 HTTP 请求",
                "function": send_http_request,
                "args": [
                    {
                        "field": "method",
                        "type": "str",
                        "default": "GET",
                        "description": "请求方法",
                    },
                    {
                        "field": "url",
                        "type": "str",
                        "description": "请求地址",
                    },
                    {
                        "field": "headers",
                        "type": "str",
                        "default": None,
                        "description": "请求头",
                    },
                    {
                        "field": "params",
                        "type": "dict",
                        "default": None,
                        "description": "请求参数",
                    },
                    {
                        "field": "data",
                        "type": "dict",
                        "default": None,
                        "description": "请求体",
                    },
                ],
            },
        },
    },
}


# 自动化流程定时任务设置
timer_config = {
    "延迟任务": {
        "description": "在一段时间后执行任务",
        "args": [
            {
                "key": "delay",
                "field": "delay",
                "type": "int",
                "description": "延迟时间(秒)",
            },
        ],
        "actions": {
            "craft": {
                "name": "合成物品",
                "description": "向OC客户端发送合成物品请求",
                "function": craft_item,
                "args": [
                    {
                        "field": "client_id",
                        "type": "str",
                        "default": "",
                        "description": "客户端 ID",
                    },
                    {
                        "field": "item_name",
                        "type": "str",
                        "description": "name",
                    },
                    {
                        "field": "item_damage",
                        "type": "int",
                        "description": "damage",
                    },
                    {
                        "field": "item_amount",
                        "type": "int",
                        "default": 1,
                        "description": "数量",
                    },
                    {
                        "field": "cpu_name",
                        "type": "str",
                        "default": None,
                        "description": "指定合成的CPU",
                    },
                    {
                        "field": "label",
                        "type": "str",
                        "default": None,
                        "description": "label",
                    },
                ],
            },
        },
    },
    "定时任务": {
        "description": "在指定时间执行任务",
        "args": [
            {
                "key": "time",
                "field": "time",
                "type": "str",
                "description": "执行时间",
            },
        ],
        "actions": {
            "craft": {
                "name": "合成物品",
                "description": "向OC客户端发送合成物品请求",
                "function": craft_item,
                "args": [
                    {
                        "field": "client_id",
                        "type": "str",
                        "default": "",
                        "description": "客户端 ID",
                    },
                    {
                        "field": "item_name",
                        "type": "str",
                        "description": "name",
                    },
                    {
                        "field": "item_damage",
                        "type": "int",
                        "description": "damage",
                    },
                    {
                        "field": "item_amount",
                        "type": "int",
                        "default": 1,
                        "description": "数量",
                    },
                    {
                        "field": "cpu_name",
                        "type": "str",
                        "default": None,
                        "description": "指定合成的CPU",
                    },
                    {
                        "field": "label",
                        "type": "str",
                        "default": None,
                        "description": "label",
                    },
                ],
            },
        },
    },
}

# action模板
action_template = {
    "CPU空闲时": {
        "http_request": [
            {
                "name": "发送群消息",
                "description": "使用OneBot v11协议，发送群消息，需要在环境变量中配置参数",
                "action_kwargs": {
                    "method": "POST",
                    "url": "http://<ONEBOT_SERVER_ADDRESS>/send_group_msg",
                    "headers": {"Authorization": "<ONEBOT_SERVER_TOKEN>"},
                    "data": """{"group_id": "<TARGET_GROUP_ID>","message": "CPU '<CPU_NAME>' 已空闲"}""",
                },
                "args": {
                    # action_kwargs中属于key-value类型的参数
                    "key_values": ["headers"],
                },
            },
        ]
    }
}


SERVER_TOKEN = os.getenv("SERVER_TOKEN")

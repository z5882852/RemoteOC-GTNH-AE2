import uuid
import json
import requests
from utils.utils import READY
from utils.task import task_manager


def craft_item(client_id, item_name, item_damage=None, item_amount=1, cpu_name=None, label=None, stack_type="item"):
    """
    请求合成物品
    :param item_name: 物品名称
    :param item_damage: 物品伤害值
    :param item_amount: 物品数量
    :param cpu_name: CPU 名称
    :param label: 标签
    :param stack_type: AE2 存储类型（item 或 fluid）
    """

    def lua_string(value):
        return json.dumps(str(value), ensure_ascii=False)

    item_amount = int(item_amount)
    if stack_type == "fluid":
        cpu_argument = f", {lua_string(cpu_name)}" if cpu_name else ""
        command = f"return ae.requestFluid({lua_string(item_name)}, {item_amount}{cpu_argument})"
    else:
        item_damage = int(item_damage or 0)
        cpu_argument = lua_string(cpu_name) if cpu_name else "nil"
        label_argument = f", {lua_string(label)}" if label else ""
        command = (
            f"return ae.requestItem({lua_string(item_name)}, {item_damage}, "
            f"{item_amount}, {cpu_argument}{label_argument})"
        )

    task_id = str(uuid.uuid4())

    task_manager.add_task(
        task_id=task_id,
        client_id=client_id,
        commands=[
            command
        ],
        status=READY,
        is_chunked=False
    )
    return task_id


def send_http_request(method: str, url: str, headers=None, params=None, data=None):
    """
    发送http请求

    向指定的URL发送HTTP请求，并返回响应内容。
    :param method: 请求方法
    :param url: 请求地址
    :param headers: 请求头
    :param params: 请求参数
    :param data: 请求数据
    """
    if not params:
        params = {}
    if not data:
        data = {}
    if not headers:
        headers = {}
    try:
        res = requests.request(method, url, headers=headers, params=params, json=data, timeout=5)
        return res.text
    except Exception as e:
        return str(e)

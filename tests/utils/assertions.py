"""
通用断言工具模块

将测试用例中反复出现的断言逻辑封装为函数，实现：
1. 减少重复代码
2. 统一错误信息格式
3. 降低断言遗漏风险

参考：从 test_note_api.py 中可以提取出这些重复模式：
- 状态码断言（出现 15+ 次）
- message 字段断言（出现 5+ 次）
- 字段非空断言（出现 6+ 次）
- 字段值等于断言（出现 2 次）
- 列表非空断言（出现 1 次）
- 降序排列断言（出现 1 次）
"""
import requests
from typing import Any

def assert_status_code(response: requests.Response, status_code: int):
    """
    断言 HTTP 状态码
    :param response: requests.Response 对象
    :param status_code: 期望的 HTTP 状态码（int）
    """
    actual_code = response.status_code
    assert actual_code == status_code, (
          f"[状态码断言失败] 预期: {status_code}, 实际: {actual_code}\n"
          f"请求URL: {response.url}\n"
          f"响应内容: {response.text}"
    )

def assert_message(response: requests.Response, message: str):
    """
    断言 message 字段
    :param response: requests.Response 对象
    :param message: 期望的 message 字段内容（str）
    """
    resp_json = response.json()
    actual_message = resp_json.get("message")
    assert actual_message == message, (
          f"[message字段断言失败] 预期: {message}, 实际: {actual_message}\n"
          f"请求URL: {response.url}\n"
          f"响应内容: {response.text}"
    )

def assert_field_not_empty(data: dict, field: str, msg: str = ""):
    """
    断言字典中某字段非空
    :param data: 已解析的字典数据
    :param field: 期望的字段名（str）
    :param msg: 自定义错误提示（可选）
    """
    value = data.get(field)
    assert value is not None and value != "", (
          f"[字段非空断言失败] {msg}\n"
          f"字段: {field}, 值: {value}"
    )

def assert_field_value(data: dict, field: str, expected_value: Any):
    """
    断言字典中某字段的值等于预期值
    :param data: 已解析的字典数据
    :param field: 期望的字段名（str）
    :param expected_value: 期望的字段值（Any）
    """
    actual_value = data.get(field)
    assert actual_value == expected_value, (
          f"[字段值等于断言失败] 字段: {field}, 期望值: {expected_value}, 实际值: {actual_value}"
    )

def assert_list_not_empty(data_list: list, msg: str = ""):
    """
    断言列表非空
    :param data_list: 已解析的列表数据
    :param msg: 自定义错误提示（可选）
    """
    assert isinstance(data_list, list) and len(data_list) > 0, (
          f"[列表非空断言失败] {msg}"
    )

def assert_descending_order(data_list: list, field_name: str, msg: str = ""):
    """
    断言列表是否按指定字段降序排列（适用于 createdAt 等时间字段）
    :param data_list: 已解析的列表数据
    :param field_name: 排序字段名（str）
    :param msg: 自定义错误提示（可选）
    """
    if len(data_list) < 2:
        return
    for i in range(len(data_list) - 1):
        current_val = data_list[i].get(field_name)
        next_val = data_list[i + 1].get(field_name)
        assert current_val >= next_val, (
          f"[降序排列断言失败] {msg}\n"
          f"索引 {i} 的 {field_name} ({current_val}) "
          f"小于索引 {i+1} 的 {field_name} ({next_val})"
    )
            




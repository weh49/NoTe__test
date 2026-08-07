"""
通用断言工具函数
消除测试用例中重复的断言逻辑，提供统一的错误信息。
"""


def assert_status_code(response, expected_code):
    """
    断言 HTTP 状态码
    :param response: requests.Response 对象
    :param expected_code: 期望的 HTTP 状态码（int）
    """
    actual = response.status_code
    assert actual == expected_code, (
        f"状态码断言失败：期望 {expected_code}，实际 {actual}\n"
        f"响应体: {response.text[:500]}"
    )


def assert_json_message(response, expected_message):
    """
    断言响应体中的 message 字段
    :param response: requests.Response 对象
    :param expected_message: 期望的 message 内容
    """
    data = response.json()
    actual = data.get("message")
    assert actual == expected_message, (
        f"message 断言失败：期望 '{expected_message}'，实际 '{actual}'"
    )


def assert_json_field_exists(response, field_name):
    """
    断言响应体中存在指定字段
    :param response: requests.Response 对象
    :param field_name: 字段名
    """
    data = response.json()
    assert field_name in data, (
        f"字段 '{field_name}' 不存在于响应体中，实际字段: {list(data.keys())}"
    )


def assert_json_field_value(response, field_name, expected_value):
    """
    断言响应体中指定字段的值
    :param response: requests.Response 对象
    :param field_name: 字段名
    :param expected_value: 期望的值
    """
    data = response.json()
    assert field_name in data, (
        f"字段 '{field_name}' 不存在于响应体中"
    )
    actual = data[field_name]
    assert actual == expected_value, (
        f"字段 '{field_name}' 断言失败：期望 '{expected_value}'，实际 '{actual}'"
    )


def assert_is_list(response):
    """
    断言响应体是 JSON 数组
    :param response: requests.Response 对象
    """
    data = response.json()
    assert isinstance(data, list), (
        f"响应体类型断言失败：期望 list，实际 {type(data).__name__}"
    )


def assert_response_time(response, max_seconds=2.0):
    """
    断言响应时间在可接受范围内
    :param response: requests.Response 对象
    :param max_seconds: 最大允许响应时间（秒）
    """
    actual_time = response.elapsed.total_seconds()
    assert actual_time <= max_seconds, (
        f"响应时间断言失败：期望 <= {max_seconds}s，实际 {actual_time:.3f}s"
    )

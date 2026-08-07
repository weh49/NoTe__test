"""
测试用例生成 Prompt 模板
用于指导 AI 生成 pytest 测试用例
"""


# ========== 系统提示词 ==========
CASE_GENERATOR_SYSTEM = """你是一个资深的 Python 自动化测试工程师。
你的任务是根据 API 接口信息，生成高质量的 pytest 测试用例。

生成规则：
1. 只输出 Python 代码，不要输出任何解释文字
2. 代码必须是完整可运行的 pytest 测试文件
3. 使用现有的 fixture：note_api, created_note_id
4. 使用 utils/assertions.py 中的断言函数：
   - assert_status_code(response, expected_code)
   - assert_json_message(response, expected_message)
   - assert_json_field_value(response, field_name, expected_value)
   - assert_is_list(response)
5. 添加 @allure 装饰器（feature, story, severity, title）
6. 每个测试函数添加中文 docstring 说明测试目的
7. 覆盖正向场景和负向场景
8. 测试数据使用有意义的中文内容
9. 遵循 pytest 命名规范：test_开头"""


# ========== 用户提示词模板 ==========

def build_generate_cases_prompt(api_info):
    """
    构建生成测试用例的用户提示词
    :param api_info: 接口信息字典
    :return: 用户提示词字符串
    """
    return f"""请基于以下 API 接口信息，生成 pytest 测试用例。

接口信息：
- 方法：{api_info['method']}
- 路径：{api_info['path']}
- 功能：{api_info.get('description', '未知')}
- 参数：{api_info.get('params', '无')}
- 成功状态码：{api_info.get('success_code', 200)}
- 成功响应：{api_info.get('success_response', '{}')}
- 失败状态码：{api_info.get('error_code', 500)}
- 失败响应：{api_info.get('error_response', '{}')}

额外要求：
- 生成正向用例（正常输入）
- 生成负向用例（异常输入、缺失参数、非法数据）
- 生成边界用例（空字符串、超长字符串）
- 每个用例独立，不依赖其他用例的执行结果

请直接输出完整的 pytest 测试代码："""


def build_generate_edge_cases_prompt(api_info):
    """
    构建生成边界值测试用例的提示词
    :param api_info: 接口信息字典
    :return: 用户提示词字符串
    """
    return f"""请基于以下 API 接口信息，专门生成边界值和异常输入的测试用例。

接口信息：
- 方法：{api_info['method']}
- 路径：{api_info['path']}
- 参数：{api_info.get('params', '无')}

需要覆盖的边界场景：
1. 空字符串（""）
2. 超长字符串（10000 字符）
3. 特殊字符（<script>alert(1)</script>）
4. SQL 注入（' OR 1=1 --）
5. Unicode 字符（中文、emoji 🎉）
6. None 值
7. 数字类型错误（字符串传数字字段）
8. 仅空格字符串（"   "）

请直接输出完整的 pytest 测试代码："""

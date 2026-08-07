"""
LLM 客户端封装
统一调用接口，支持智谱 GLM / MIMO 等兼容 OpenAI 格式的模型
"""
import re
import ast
import time
import logging
from openai import OpenAI

from ai.config import (
    get_api_key,
    get_base_url,
    get_model_name,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
)

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM 调用异常"""
    pass


class LLMClient:
    """
    LLM 客户端
    统一封装 AI 模型调用，支持切换不同提供商
    """

    def __init__(self, provider=None, model=None):
        """
        初始化 LLM 客户端
        :param provider: 提供商名称（glm/mimo），默认使用配置文件中的 CURRENT_PROVIDER
        :param model: 模型名称，默认使用提供商的默认模型
        """
        self.provider = provider
        self.model_name = get_model_name(model, provider)
        self.base_url = get_base_url(provider)
        self.api_key = get_api_key(provider)

        # 创建 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )

        logger.info(f"LLM 客户端初始化完成: provider={provider}, model={self.model_name}")

    def chat(self, system_prompt, user_prompt, temperature=None, max_tokens=None):
        """
        发送对话请求
        :param system_prompt: 系统提示词
        :param user_prompt: 用户提示词
        :param temperature: 温度参数（0-1），越低越稳定
        :param max_tokens: 最大输出 token 数
        :return: AI 回复的文本内容
        """
        temperature = temperature or DEFAULT_TEMPERATURE
        max_tokens = max_tokens or DEFAULT_MAX_TOKENS

        logger.info(f"发送请求到 {self.model_name}...")
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            elapsed = time.time() - start_time
            content = response.choices[0].message.content
            logger.info(f"AI 响应完成，耗时 {elapsed:.2f}s，输出 {len(content)} 字符")
            return content

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"AI 请求失败，耗时 {elapsed:.2f}s: {e}")
            raise LLMError(f"LLM 调用失败: {e}") from e

    def generate_code(self, task_description, temperature=None):
        """
        专门用于生成代码的接口
        自动提取代码块、进行语法检查
        :param task_description: 任务描述
        :param temperature: 温度参数
        :return: 生成的 Python 代码字符串
        """
        system_prompt = """你是一个资深的 Python 测试工程师。
你的任务是生成高质量的 pytest 测试代码。

要求：
1. 只输出 Python 代码，不要输出其他内容
2. 代码必须是完整可运行的
3. 使用 ast 语法检查确保代码正确
4. 遵循 pytest 最佳实践
5. 添加中文注释说明每个测试的目的"""

        raw_response = self.chat(system_prompt, task_description, temperature)

        # 提取代码块
        code = self._extract_code(raw_response)

        # 语法检查
        self._validate_syntax(code)

        return code

    def _extract_code(self, text):
        """
        从 AI 响应中提取 Python 代码块
        :param text: AI 原始响应
        :return: 提取的代码字符串
        """
        # 尝试提取 ```python ... ``` 代码块
        pattern = r'```python\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            # 如果有多个代码块，拼接在一起
            return '\n\n'.join(match.strip() for match in matches)

        # 尝试提取 ``` ... ``` 代码块（不限定语言）
        pattern = r'```\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return '\n\n'.join(match.strip() for match in matches)

        # 如果没有代码块，返回原始文本（可能是纯代码）
        return text.strip()

    def _validate_syntax(self, code):
        """
        验证 Python 代码语法
        :param code: Python 代码字符串
        :raises SyntaxError: 语法错误时抛出
        """
        try:
            ast.parse(code)
            logger.info("代码语法检查通过")
        except SyntaxError as e:
            logger.warning(f"代码语法错误: {e}")
            raise SyntaxError(f"AI 生成的代码存在语法错误: {e}\n代码:\n{code}") from e


# ========== 便捷函数 ==========

def create_client(provider=None, model=None):
    """
    创建 LLM 客户端的便捷函数
    :param provider: 提供商名称
    :param model: 模型名称
    :return: LLMClient 实例
    """
    return LLMClient(provider=provider, model=model)

"""
AI 测试配置模块
支持 DeepSeek / 千问 Qwen / 智谱 GLM 等兼容 OpenAI 格式的模型
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


# ========== 模型提供商配置 ==========

PROVIDERS = {
    # ========== DeepSeek（推荐：免费额度大，代码能力强）==========
    "deepseek": {
        "name": "DeepSeek",
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/"),
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "models": {
            "chat": "deepseek-chat",          # 通用对话
            "v3": "deepseek-v3",              # DeepSeek V3
            "v4-flash": "deepseek-v4-flash",  # V4 Flash（免费）
        },
        "default_model": "deepseek-chat",
    },

    # ========== 千问 Qwen（阿里通义，免费额度）==========
    "qwen": {
        "name": "千问 Qwen",
        "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/"),
        "api_key": os.getenv("QWEN_API_KEY", ""),
        "models": {
            "turbo": "qwen-turbo",       # 快速版（免费额度大）
            "plus": "qwen-plus",         # 增强版
            "max": "qwen-max",           # 最强版
            "long": "qwen-long",         # 长文本版
        },
        "default_model": "qwen-turbo",
    },

    # ========== 智谱 GLM ==========
    "glm": {
        "name": "智谱 GLM",
        "base_url": os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
        "api_key": os.getenv("GLM_API_KEY", ""),
        "models": {
            "flash": "glm-4-flash",      # 免费
            "standard": "glm-4",          # 付费
            "plus": "glm-4-plus",         # 付费（更强）
        },
        "default_model": "glm-4-flash",
    },

    # ========== 小米 MIMO ==========
    "mimo": {
        "name": "小米 MIMO",
        "base_url": os.getenv("MIMO_BASE_URL", "https://api.xiaomi.com/v1/"),
        "api_key": os.getenv("MIMO_API_KEY", ""),
        "models": {
            "7b": "mimo-7b",
            "13b": "mimo-13b",
        },
        "default_model": "mimo-7b",
    },
}


# ========== 当前使用的提供商 ==========

# 从环境变量读取当前使用的提供商，默认为 deepseek（免费额度大）
CURRENT_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")


def get_provider_config(provider=None):
    """
    获取指定提供商的配置
    :param provider: 提供商名称（glm/mimo），默认使用 CURRENT_PROVIDER
    :return: 配置字典
    """
    provider = provider or CURRENT_PROVIDER
    if provider not in PROVIDERS:
        raise ValueError(
            f"不支持的提供商: {provider}\n"
            f"支持的提供商: {list(PROVIDERS.keys())}"
        )
    return PROVIDERS[provider]


def get_api_key(provider=None):
    """
    获取 API Key
    :param provider: 提供商名称
    :return: API Key 字符串
    """
    config = get_provider_config(provider)
    api_key = config["api_key"]
    if not api_key:
        raise ValueError(
            f"未配置 {config['name']} 的 API Key\n"
            f"请在 tests/.env 文件中设置:\n"
            f"  {provider.upper()}_API_KEY=your_api_key_here"
        )
    return api_key


def get_base_url(provider=None):
    """
    获取 API 基础 URL
    :param provider: 提供商名称
    :return: URL 字符串
    """
    return get_provider_config(provider)["base_url"]


def get_model_name(model_alias=None, provider=None):
    """
    获取模型全名
    :param model_alias: 模型别名（flash/standard/plus 等）
    :param provider: 提供商名称
    :return: 模型全名字符串
    """
    config = get_provider_config(provider)
    if model_alias:
        models = config["models"]
        if model_alias not in models:
            raise ValueError(
                f"{config['name']} 不支持模型: {model_alias}\n"
                f"支持的模型: {list(models.keys())}"
            )
        return models[model_alias]
    return config["default_model"]


# ========== 全局默认配置 ==========

DEFAULT_TEMPERATURE = 0.3    # 降低随机性，生成更稳定的代码
DEFAULT_MAX_TOKENS = 4096    # 最大输出 token 数
DEFAULT_TIMEOUT = 60         # API 请求超时时间（秒）
DEFAULT_MAX_RETRIES = 3      # 最大重试次数

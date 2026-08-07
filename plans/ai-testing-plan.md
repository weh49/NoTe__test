# ThinkBoard AI 自动化测试方案

> 本文档是 ThinkBoard 项目引入 AI 进行自动化测试的完整设计方案。

---

## 一、什么是 AI 测试？

AI 测试 = **用大语言模型 LLM 来辅助或替代人工编写测试用例、生成断言、分析日志**。

```
传统测试流程：
  人工分析接口 → 人工写用例 → 人工写断言 → 人工分析失败 → 人工修复

AI 测试流程：
  解析接口信息 → AI 生成用例 → AI 生成断言 → AI 分析失败 → AI 建议修复
```

核心思路：**让 AI 做重复性的苦力活，人做决策和审核**。

---

## 二、整体架构设计

```
tests/
├── ai/                              # AI 核心模块（新增）
│   ├── __init__.py
│   ├── client.py                    # LLM 客户端封装
│   ├── prompts/                     # Prompt 模板
│   │   ├── __init__.py
│   │   ├── case_generator.py        # 用例生成 Prompt
│   │   ├── assertion_generator.py   # 断言生成 Prompt
│   │   └── failure_analyzer.py      # 失败分析 Prompt
│   ├── generators/                  # 生成器
│   │   ├── __init__.py
│   │   ├── test_case_generator.py   # 测试用例生成器
│   │   └── test_data_generator.py   # 测试数据生成器
│   ├── analyzers/                   # 分析器
│   │   ├── __init__.py
│   │   └── failure_analyzer.py      # 失败日志分析器
│   └── config.py                    # AI 配置（模型、API Key等）
├── api/                             # 已有
├── testcases/                       # 已有
│   ├── test_notes.py               # 手写用例
│   ├── test_notes_negative.py      # 手写用例
│   └── ai_generated/               # AI 生成的用例（新增）
│       ├── __init__.py
│       └── test_ai_edge_cases.py
├── utils/                           # 已有
│   ├── assertions.py               # 已修复
│   └── report.py                   # AI 分析报告（新增）
├── conftest.py                      # 已修复
└── run_ai_tests.py                 # AI 测试入口脚本（新增）
```

---

## 三、核心模块设计

### 模块 1：LLM 客户端封装 `ai/client.py`

**作用**：统一封装 AI 模型调用，支持切换不同模型。

```python
# 设计思路
class LLMClient:
    def __init__(self, provider="glm", model="glm-4-flash"):
        """
        支持的 provider（均兼容 OpenAI 格式）：
        - glm: 智谱 GLM（glm-4-flash 免费，glm-4 付费）
        - mimo: 小米 MIMO
        """
    
    def chat(self, system_prompt, user_prompt, temperature=0.3):
        """
        统一的对话接口
        temperature=0.3: 降低随机性，生成更稳定的代码
        """
    
    def generate_code(self, task_description):
        """
        专门用于生成代码的接口
        自动添加代码提取、语法检查等逻辑
        """
```

**为什么需要封装？**
- 切换模型只需改一个参数
- 统一处理 API 错误、重试、限流
- 统一管理 API Key（从环境变量读取）
- GLM 和 MIMO 都兼容 OpenAI 格式，共用同一套代码

---

### 模块 2：测试用例生成器 `ai/generators/test_case_generator.py`

**作用**：分析 API 接口，自动生成 pytest 测试用例。

```python
class TestCaseGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def generate_from_routes(self, routes_file):
        """
        输入：后端路由文件路径
        输出：pytest 测试代码字符串
        
        流程：
        1. 读取 routes/notesRoutes.js，提取接口信息
        2. 构建 Prompt，告诉 AI 接口的路径、方法、参数
        3. AI 生成测试用例代码
        4. 语法检查（ast.parse）
        5. 写入 ai_generated/ 目录
        """
    
    def generate_edge_cases(self, api_info):
        """
        专门生成边界值测试用例：
        - 空字符串
        - 超长字符串（10000字符）
        - 特殊字符（<script>alert(1)</script>）
        - SQL注入（' OR 1=1 --）
        - Unicode字符（中文、emoji）
        - None值
        - 数字类型错误
        """
```

**Prompt 设计示例**：

```
你是一个资深测试工程师。请基于以下 API 信息生成 pytest 测试用例。

API 信息：
- 路径：POST /api/notes
- 参数：title(string,必填), content(string,必填)
- 成功响应：201, {"message": "Note created succesfully"}
- 失败响应：500, {"message": "Internal server error"}

要求：
1. 使用现有的 note_api fixture
2. 使用 utils/assertions.py 中的断言函数
3. 添加 @allure 装饰器
4. 覆盖正向和负向场景
5. 每个测试函数有中文注释
```

---

### 模块 3：测试数据生成器 `ai/generators/test_data_generator.py`

**作用**：根据数据模型自动生成测试数据。

```python
class TestDataGenerator:
    def generate_from_model(self, model_info):
        """
        输入：Mongoose Schema 定义
        输出：多组测试数据（JSON格式）
        
        例如输入：
        noteSchema = {
            title: {type: String, required: true},
            content: {type: String, required: true}
        }
        
        输出：
        [
            {"title": "正常标题", "content": "正常内容"},           # 正向
            {"title": "", "content": "有内容"},                    # 空标题
            {"title": "a" * 10000, "content": "内容"},             # 超长
            {"title": "<script>alert(1)</script>", "content": "xss"}, # XSS
            {"title": "' OR 1=1 --", "content": "sql注入"},        # SQL注入
        ]
        """
```

---

### 模块 4：失败分析器 `ai/analyzers/failure_analyzer.py`

**作用**：当测试失败时，AI 自动分析原因并给出修复建议。

```python
class FailureAnalyzer:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_failure(self, test_name, error_trace, response_body=None):
        """
        输入：
        - test_name: 失败的测试名称
        - error_trace: 错误堆栈
        - response_body: API 响应体（可选）
        
        输出：
        {
            "root_cause": "后端缺少参数校验，空字符串通过了验证",
            "category": "后端缺陷",
            "severity": "HIGH",
            "fix_suggestion": "在 notesController.js 的 createNote 中添加参数校验中间件",
            "related_bug": "GUIDE_FRAMEWORK.md 中记录的已知缺陷 #1"
        }
        """
    
    def generate_report(self, test_results):
        """
        输入：pytest 运行结果
        输出：完整的分析报告（Markdown格式）
        """
```

---

### 模块 5：AI 测试入口 `run_ai_tests.py`

**作用**：一键运行 AI 测试流程。

```python
"""
使用方式：
    python run_ai_tests.py --mode generate    # 生成用例
    python run_ai_tests.py --mode run         # 运行所有用例
    python run_ai_tests.py --mode analyze     # 分析失败结果
    python run_ai_tests.py --mode all         # 全流程
"""
```

---

## 四、数据流设计

```
┌─────────────────────────────────────────────────────┐
│                    AI 测试流程                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Step 1: 解析接口信息                                │
│  ┌──────────────┐    ┌──────────────┐               │
│  │ routes/*.js  │───>│ 接口信息提取  │               │
│  └──────────────┘    └──────┬───────┘               │
│                             │                       │
│  Step 2: AI 生成用例         ▼                       │
│  ┌──────────────┐    ┌──────────────┐               │
│  │  LLM Client  │<──>│ Prompt 模板  │               │
│  └──────┬───────┘    └──────────────┘               │
│         │                                           │
│         ▼                                           │
│  Step 3: 写入测试文件                                │
│  ┌──────────────┐                                   │
│  │ai_generated/ │                                   │
│  │test_ai_*.py  │                                   │
│  └──────┬───────┘                                   │
│         │                                           │
│  Step 4: 运行测试                                    │
│         ▼                                           │
│  ┌──────────────┐                                   │
│  │   pytest     │                                   │
│  └──────┬───────┘                                   │
│         │                                           │
│  Step 5: AI 分析结果                                 │
│         ▼                                           │
│  ┌──────────────┐    ┌──────────────┐               │
│  │ Failure      │───>│ 分析报告     │               │
│  │ Analyzer     │    │ .md / allure │               │
│  └──────────────┘    └──────────────┘               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 五、实施计划

### Phase 1：基础搭建（优先级最高）

| 任务 | 文件 | 说明 |
|------|------|------|
| 1.1 LLM 客户端 | `ai/client.py` | 封装 OpenAI API 调用 |
| 1.2 AI 配置 | `ai/config.py` | API Key、模型选择等配置 |
| 1.3 Prompt 模板 | `ai/prompts/` | 用例生成、断言生成、失败分析的 Prompt |
| 1.4 接口解析器 | `ai/parsers/` | 从路由文件提取接口信息 |

### Phase 2：用例生成

| 任务 | 文件 | 说明 |
|------|------|------|
| 2.1 用例生成器 | `ai/generators/test_case_generator.py` | AI 生成 pytest 用例 |
| 2.2 数据生成器 | `ai/generators/test_data_generator.py` | AI 生成边界值/异常数据 |
| 2.3 语法校验 | 集成到生成器 | ast.parse 检查生成的代码 |

### Phase 3：失败分析

| 任务 | 文件 | 说明 |
|------|------|------|
| 3.1 失败分析器 | `ai/analyzers/failure_analyzer.py` | AI 分析测试失败原因 |
| 3.2 报告生成 | `utils/report.py` | 生成 Markdown 分析报告 |

### Phase 4：全流程整合

| 任务 | 文件 | 说明 |
|------|------|------|
| 4.1 入口脚本 | `run_ai_tests.py` | 一键运行全流程 |
| 4.2 pytest 插件 | `ai/pytest_plugin.py` | 集成到 pytest 执行流程 |

---

## 六、技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| LLM 模型 | 智谱 GLM-4-flash / 小米 MIMO | 国产模型，兼容 OpenAI 格式，已有付费账号 |
| API 调用 | openai Python SDK | GLM/MIMO 均兼容 OpenAI 格式，共用 SDK |
| 代码校验 | ast 模块（Python 内置） | 安全的语法检查，无需额外依赖 |
| 配置管理 | python-dotenv | 从 .env 文件读取 API Key |
| 日志 | logging + structlog | 结构化日志 |

---

## 七、新增依赖

```txt
# requirements.txt 新增
openai>=1.30.0        # 兼容 GLM/MIMO 的 OpenAI 格式
python-dotenv>=1.0.0  # 环境变量管理
```

**.env 配置示例：**
```env
# 智谱 GLM
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
GLM_MODEL=glm-4-flash

# 小米 MIMO
MIMO_API_KEY=your_mimo_api_key_here
MIMO_BASE_URL=https://api.mimo.ai/v1/
MIMO_MODEL=mimo-7b

# 当前使用的模型：glm 或 mimo
AI_PROVIDER=glm
```

---

## 八、安全考虑

| 风险 | 措施 |
|------|------|
| API Key 泄露 | 使用 .env 文件，.gitignore 排除 |
| AI 生成恶意代码 | ast.parse 语法检查 + 沙箱执行 |
| API 调用成本 | 设置每日调用上限 + 使用免费模型 glm-4-flash |
| 生成代码质量 | 人工审核 + 自动化回归测试 |

---

## 九、预期成果

| 指标 | 当前 | AI 增强后 |
|------|------|-----------|
| 测试用例数 | 12 个 | 60+ 个 |
| 用例编写时间 | 2 小时/接口 | 5 分钟/接口 |
| 边界值覆盖 | 0% | 90% |
| 失败分析时间 | 30 分钟 | 2 分钟 |
| 简历亮点 | 基础自动化测试 | AI + 测试工程化 |

---

> 方案设计完成，待确认后进入实施阶段。

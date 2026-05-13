# ThinkBoard 接口自动化测试框架搭建指南

> 基于项目实战整理，适合从入门到初级的测试工程师参考。
> 技术栈：Python + pytest + requests + Allure

---

## 一、框架目标

搭建一套接近企业级的接口自动化测试框架，能写在简历里展示的。
不只是"能跑通"，而是能体现你对测试工程化设计的理解。

---

## 二、框架目录结构

```
tests/
├── conftest.py              # 全局 fixtures（测试前置/后置条件）
├── pytest.ini               # pytest 配置
├── requirements.txt         # Python 依赖清单
├── config/
│   ├── __init__.py
│   └── settings.py          # 环境配置（BASE_URL 等集中管理）
├── api/
│   └── notes_api.py         # 接口封装层（每个接口封装成 Python 函数）
├── testcases/
│   ├── __init__.py
│   ├── test_create_note.py  # 创建笔记测试用例
│   ├── test_get_notes.py    # 获取笔记测试用例
│   ├── test_update_note.py  # 更新笔记测试用例
│   └── test_delete_note.py  # 删除笔记测试用例
├── testdata/
│   └── notes_data.py        # 测试数据（正向 + 异常数据）
└── utils/
    └── assertions.py        # 自定义断言工具函数
```

---

## 三、为什么要这样分层？

| 目录 | 作用 | 如果没有会怎样 |
|------|------|---------------|
| `config/` | 环境相关配置集中管理 | 接口地址、端口散落在 100 个用例里，改一次要动 100 个文件 |
| `api/` | 接口请求封装 | 接口地址或参数格式变了，要改每个用例里的 requests 代码 |
| `testcases/` | 按业务模块分文件 | 所有用例堆一个文件，几百行根本没法维护 |
| `testdata/` | 测试数据跟用例分离 | 想换测试数据得去用例代码里翻，容易改错 |
| `utils/` | 通用工具函数 | 同样的断言逻辑在多个用例里重复写 |
| `conftest.py` | pytest 的全局 fixture | 没有它，每个用例都要自己写前置/后置条件 |

---

## 四、分步实施路径

### Step 1：基础配置

**目标：** 把环境相关的值抽出来集中管理。

**文件：**
- `requirements.txt`：pytest, requests, allure-pytest
- `pytest.ini`：告诉 pytest 去哪找测试文件、默认用什么参数
- `config/settings.py`：BASE_URL = "http://localhost:5001"

**核心概念：** 永远不要在用例里硬编码环境地址。用 `settings.BASE_URL` 替代 `"http://localhost:5001"`。

**原理：** 以后部署到测试环境，只需要改 settings.py 一个文件，所有用例自动生效。

---

### Step 2：conftest.py — pytest 的灵魂

**目标：** 用 fixtures 管理测试的前置和后置条件。

**核心概念：**
- fixture 是 pytest 提供的机制，用来在测试用例运行之前准备数据，运行之后清理数据
- 类比：你用 unittest 时的 `setUp()` 和 `tearDown()`，但 fixture 更灵活
- `scope="session"` 表示整个测试会话只执行一次（不是每个用例都执行）
- `yield` 之前的代码是前置条件，之后的代码是后置条件

**关键 fixture：**
- `api_client`：一个 `requests.Session` 对象，复用 TCP 连接，用例里直接注入使用

---

### Step 3：API 封装层

**目标：** 把每个接口封装成一个 Python 函数，用例只调用函数，不直接写 requests。

**错误写法（每个用例都写）：**
```python
def test_create():
    resp = requests.post("http://localhost:5001/api/notes",
                         json={"title": "x", "content": "y"})
    assert resp.status_code == 201
```

**正确写法（调用封装好的函数）：**
```python
def test_create(api_client):
    resp = notes_api.create_note(api_client, title="x", content="y")
    assert resp.status_code == 201
```

**原理：** 如果接口地址从 `/api/notes` 改成 `/api/v2/notes`，只改 api 层，用例不动。

---

### Step 4：测试数据管理

**目标：** 把测试数据从用例里抽出来，用参数化驱动。

**原理：** 用例的逻辑是固定的（创建笔记、检查响应），变的是数据（不同的 title、content、异常输入）。
数据驱动让你用一套代码跑多组数据，pytest 的 `@pytest.mark.parametrize` 就是做这个的。

---

### Step 5-6：测试用例编写

**每个接口至少覆盖：**
1. 正向用例（正常输入 → 预期成功）
2. 异常用例（缺少必填字段 → 预期失败）
3. 边界用例（空字符串、超长字符串）
4. 状态码断言（不仅断言 status_code，还要断言响应体内容）

---

### Step 7：Allure 报告

**运行命令：**
```bash
pytest tests/ --alluredir=./allure-results
allure serve ./allure-results
```

---

## 五、被测项目信息（ThinkBoard）

### 接口清单

| 方法 | 路径 | 功能 | 成功状态码 |
|------|------|------|-----------|
| GET | `/api/notes` | 获取所有笔记（按创建时间倒序） | 200 |
| GET | `/api/notes/:id` | 根据 ID 获取单条笔记 | 200 |
| POST | `/api/notes` | 创建笔记 | 201 |
| PUT | `/api/notes/:id` | 更新笔记 | 200 |
| DELETE | `/api/notes/:id` | 删除笔记 | 200 |

### 数据模型

```
Note:
  - title: String, 必填 (required)
  - content: String, 必填 (required)
  - timestamps: 自动生成 createdAt + updatedAt
```

### 已知缺陷（测试要覆盖的）

1. 没有输入校验中间件 → 非法输入返回 500 而不是 400
2. findByIdAndUpdate 不运行 Schema 校验器 → 空字符串能通过
3. 限流器有拼写 BUG → `resizeBy` 应为 `res`
4. createNote 不返回创建的数据 → 前端拿不到新笔记 ID
5. 没有分页 → 全量查询
6. 没有认证授权

---

## 六、验证方式

```bash
# 运行所有测试
pytest tests/ -v

# 生成 Allure 报告
pytest tests/ --alluredir=./allure-results
allure serve ./allure-results

# 只运行某个接口的测试
pytest tests/testcases/test_create_note.py -v
```

---

> 整理于 2026-05-06 | ThinkBoard 项目实战

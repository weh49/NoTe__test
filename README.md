# ThinkBoard 接口自动化测试框架

针对 **ThinkBoard 笔记管理系统** 的 RESTful 接口自动化测试实践，覆盖笔记增删改查（CRUD）的完整业务链路。

> 被测系统基于开源教程项目 [half-pace/thinkboard-mod-tut](https://github.com/half-pace/thinkboard-mod-tut)，
> 本仓库聚焦于在其之上构建的接口自动化测试工程。

## 一、被测系统

| 层 | 技术 |
|---|---|
| 后端 | Node.js + Express |
| 数据库 | MongoDB（Mongoose） |
| 前端 | React（Vite） |
| 接口 | RESTful，前缀 `/api/notes` |

主要接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/notes` | 获取笔记列表 |
| POST | `/api/notes` | 创建笔记 |
| GET | `/api/notes/:id` | 查询单条笔记 |
| PUT | `/api/notes/:id` | 更新笔记 |
| DELETE | `/api/notes/:id` | 删除笔记 |

## 二、测试技术栈

`pytest` · `requests` · `Allure` · `pytest-html` · `Faker` · `Locust`

## 三、测试设计

- **分层设计**：`api_client`（请求封装）→ `testcases`（断言）→ `fixtures`（测试数据/环境）
- **等价类划分 + 边界值分析**：标题、内容长度的有效/无效/边界取值
- **参数化用例**：`@pytest.mark.parametrize` 驱动多组数据，一份逻辑覆盖多场景
- **数据驱动**：测试数据集中于 `tests/data/`，由 Faker 生成
- **异常与容错**：非法 ID、必填字段缺失、超长输入、非法类型等负向场景
- **性能测试**：Locust 压测脚本位于 `tests/performance/`

当前用例规模：**87 条**（`pytest --collect-only`）。

## 四、目录结构

```
backend/                    # 被测后端（Node.js + Express + MongoDB）
frontend/                   # 被测前端（React）
tests/
├── api/api_client.py       # 接口请求封装层
├── config/setting.py       # 环境配置（BASE_URL 等）
├── conftest.py             # pytest fixtures（会话级前置/清理）
├── data/                   # 测试数据（json + Faker 生成器）
├── fixtures/               # 自定义 fixture
├── performance/            # Locust 性能测试脚本
├── testcases/              # 测试用例
├── utils/assertions.py     # 断言工具
├── pytest.ini              # pytest 配置
└── requirements.txt        # 测试依赖
.github/workflows/test.yml  # CI 流水线
```

## 五、本地运行

```bash
# 1. 启动被测系统（默认 5001 端口，需本地 MongoDB）
cd backend
npm install
# 在 backend/.env 中配置 MONGO_URI=mongodb://127.0.0.1:27017/thinkboard
npm run dev

# 2. 安装测试依赖
cd ../tests
pip install -r requirements.txt

# 3. 执行测试
pytest testcases/ -v
# 生成 Allure 报告
pytest testcases/ --alluredir=report/allure-results
allure serve report/allure-results
```

## 六、CI/CD

`.github/workflows/test.yml`（GitHub Actions）：

```
push 到 main → 拉取代码 → 启动 MongoDB 服务容器
              → 安装后端依赖 → 启动后端 → 等待就绪
              → 安装测试依赖 → 执行 pytest → 产出 Allure 报告
```

任何一次 push 都会在干净的 Ubuntu 环境中完整复现「起服务 → 跑测试」的流程，
用于保证测试套件在无本地环境依赖时依然可执行。

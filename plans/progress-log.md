# ThinkBoard 项目进度记录

> 最后更新：2026-05-30 03:35

---

## 一、重要提醒

### 用户反馈（必须记住）
> "你的代码写的很好，但对我来说我需要时间去理解和解读。我也需要的是一个可以跟我一起做的战友和导师。你做出的东西在我面试时候对我帮助不大，我要的是能够帮助我去学会AI测试。"

**调整方向：**
- 不要一下子生成大量代码
- 每生成一段代码，都要逐行讲解原理
- 让用户自己动手修改和实验
- 重点是教会思路，不是替代思考
- 面试时说的是用户自己做的，不是 AI 做的

---

## 二、已完成的工作

### Day 1（2026-05-29）
1. 项目结构分析 + 代码解释
2. 测试框架评审（评分 4/10）
3. P0 修复（4 个文件修改 + 2 个新文件）
4. AI 测试方案设计

### Day 2（2026-05-30）
1. 更新方案：支持 DeepSeek/Qwen/GLM/MIMO 4 个提供商
2. Phase 1 基础搭建完成：
   - [`tests/ai/__init__.py`](tests/ai/__init__.py) - 模块入口
   - [`tests/ai/config.py`](tests/ai/config.py) - 4 个模型提供商配置
   - [`tests/ai/client.py`](tests/ai/client.py) - LLM 客户端封装
   - [`tests/ai/prompts/case_generator.py`](tests/ai/prompts/case_generator.py) - Prompt 模板
   - [`tests/ai/parsers/route_parser.py`](tests/ai/parsers/route_parser.py) - 接口解析器
   - [`tests/run_ai_tests.py`](tests/run_ai_tests.py) - 入口脚本
3. 验证解析器成功（dry-run 测试通过，提取出 5 个接口）

---

## 三、明天的计划

1. **配置 .env 文件**：填入 DeepSeek API Key
2. **测试 AI 客户端**：调用 DeepSeek 生成第一个测试用例
3. **逐行讲解代码**：确保用户理解每个文件的作用
4. **用户动手实验**：让用户自己修改 Prompt，观察 AI 输出变化

---

## 四、文件清单

```
tests/ai/__init__.py                    # 模块入口
tests/ai/config.py                      # 模型配置（DeepSeek/Qwen/GLM/MIMO）
tests/ai/client.py                      # LLM 客户端（调用 AI 的工具）
tests/ai/prompts/case_generator.py      # Prompt 模板（告诉 AI 做什么）
tests/ai/parsers/route_parser.py        # 接口解析器（从后端代码提取接口）
tests/ai/generators/__init__.py         # 生成器模块（待实现）
tests/ai/analyzers/__init__.py          # 分析器模块（待实现）
tests/testcases/ai_generated/__init__.py # AI 生成用例目录
tests/run_ai_tests.py                   # 入口脚本
tests/.env.example                      # API Key 配置模板
tests/requirements.txt                  # 依赖清单（已添加 openai + python-dotenv）
plans/ai-testing-plan.md                # AI 测试方案文档
```

---

## 五、技术选型

| 组件 | 选择 | 说明 |
|------|------|------|
| AI 模型 | DeepSeek（默认） | 免费额度大，代码能力强 |
| 备选模型 | 千问 Qwen / 智谱 GLM / 小米 MIMO | 都兼容 OpenAI 格式 |
| API SDK | openai Python | 因为所有模型都兼容 OpenAI 格式 |
| 代码校验 | ast 模块 | Python 内置，安全的语法检查 |

---

> 明天继续！记住：教会思路比生成代码更重要。

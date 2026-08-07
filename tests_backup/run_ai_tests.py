"""
AI 测试入口脚本
一键运行 AI 测试流程：解析接口 → AI 生成用例 → 保存文件

使用方式：
    python run_ai_tests.py              # 完整流程
    python run_ai_tests.py --dry-run    # 只解析不生成（测试解析器）
    python run_ai_tests.py --provider glm  # 指定使用 GLM 模型
"""
import os
import sys
import argparse
import logging

# 设置当前目录为 tests/
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from ai.client import LLMClient, LLMError
from ai.parsers.route_parser import parse_routes
from ai.prompts.case_generator import (
    CASE_GENERATOR_SYSTEM,
    build_generate_cases_prompt,
    build_generate_edge_cases_prompt,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ========== 路径配置 ==========
ROUTES_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "src", "routes", "notesRoutes.js")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "src", "models", "Note.js")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "testcases", "ai_generated")


def main():
    parser = argparse.ArgumentParser(description="AI 自动化测试生成器")
    parser.add_argument("--dry-run", action="store_true", help="只解析接口，不调用 AI 生成用例")
    parser.add_argument("--provider", type=str, default=None, help="指定 AI 提供商（deepseek/qwen/glm/mimo）")
    parser.add_argument("--edge-only", action="store_true", help="只生成边界值测试用例")
    args = parser.parse_args()

    print("=" * 60)
    print("[AI] ThinkBoard AI 测试生成器")
    print("=" * 60)

    # ========== Step 1: 解析接口 ==========
    print("\n[Step 1] 解析后端接口...")
    try:
        api_list = parse_routes(ROUTES_FILE)
    except FileNotFoundError:
        logger.error(f"路由文件不存在: {ROUTES_FILE}")
        print(f"[ERROR] 找不到路由文件: {ROUTES_FILE}")
        return 1

    if not api_list:
        logger.warning("未发现任何接口")
        print("[WARN] 未发现任何接口，请检查路由文件")
        return 1

    # 打印解析结果
    print(f"\n[OK] 共发现 {len(api_list)} 个接口：")
    for i, api in enumerate(api_list, 1):
        print(f"  {i}. {api['method']:6s} {api['path']:30s} | {api['description']}")

    # dry-run 模式：只解析不生成
    if args.dry_run:
        print("\n[DRY-RUN] 只解析接口，不调用 AI 生成用例")
        print("解析结果：")
        for api in api_list:
            print(f"\n--- {api['method']} {api['path']} ---")
            for key, value in api.items():
                print(f"  {key}: {value}")
        return 0

    # ========== Step 2: 创建 AI 客户端 ==========
    print(f"\n[Step 2] 初始化 AI 客户端...")
    try:
        client = LLMClient(provider=args.provider)
        print(f"[OK] 使用模型: {client.model_name} ({client.provider})")
    except ValueError as e:
        logger.error(f"AI 客户端初始化失败: {e}")
        print(f"[ERROR] {e}")
        print("\n请在 tests/.env 文件中配置 API Key")
        print("参考 tests/.env.example")
        return 1

    # ========== Step 3: 生成测试用例 ==========
    print(f"\n[Step 3] AI 生成测试用例...")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成 __init__.py
    init_file = os.path.join(OUTPUT_DIR, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# AI 自动生成的测试用例\n")

    generated_files = []
    
    for api in api_list:
        print(f"\n  [RUN] 生成: {api['method']} {api['path']} ...")
        
        try:
            # 选择提示词
            if args.edge_only:
                user_prompt = build_generate_edge_cases_prompt(api)
            else:
                user_prompt = build_generate_cases_prompt(api)
            
            # 调用 AI
            generated_code = client.chat(
                system_prompt=CASE_GENERATOR_SYSTEM,
                user_prompt=user_prompt,
            )
            
            # 语法检查
            try:
                client._validate_syntax(generated_code)
                print(f"    [OK] 语法检查通过")
            except SyntaxError as e:
                print(f"    [WARN] 语法检查失败: {e}")
                print(f"    跳过此接口")
                continue
            
            # 生成文件名
            method = api["method"].lower()
            path_clean = api["path"].replace("/api/notes", "").replace("/", "_").strip("_")
            if not path_clean:
                path_clean = "list"
            filename = f"test_ai_{method}_{path_clean}.py"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 写入文件
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generated_code)
            
            generated_files.append(filename)
            print(f"    [OK] 已保存: {filename}")
            
        except LLMError as e:
            print(f"    [ERROR] AI 调用失败: {e}")
            continue
        except Exception as e:
            print(f"    [ERROR] 未知错误: {e}")
            logger.exception(e)
            continue

    # ========== Step 4: 总结 ==========
    print("\n" + "=" * 60)
    print("[SUMMARY] 生成结果汇总")
    print("=" * 60)
    print(f"  接口总数: {len(api_list)}")
    print(f"  生成成功: {len(generated_files)}")
    print(f"  输出目录: {OUTPUT_DIR}")
    
    if generated_files:
        print(f"\n  生成的文件：")
        for f in generated_files:
            print(f"    - {f}")
        
        print(f"\n  运行测试命令：")
        print(f"    cd tests && pytest testcases/ai_generated/ -v")
    
    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

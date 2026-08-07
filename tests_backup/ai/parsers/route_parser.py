"""
接口解析器
从后端路由文件中提取 API 接口信息

作用：读取 notesRoutes.js，自动提取出：
- 方法（GET/POST/PUT/DELETE）
- 路径（/api/notes, /api/notes/:id）
- 参数信息
"""
import re
import os
import logging

logger = logging.getLogger(__name__)


def parse_routes(routes_file):
    """
    解析路由文件，提取接口信息列表
    
    :param routes_file: 路由文件路径（如 ../backend/src/routes/notesRoutes.js）
    :return: 接口信息列表
    """
    logger.info(f"开始解析路由文件: {routes_file}")
    
    # 1. 读取路由文件内容
    with open(routes_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 2. 用正则表达式提取路由定义
    # 匹配格式：router.get("/", getAllNotes);
    #          router.post("/", createNote);
    pattern = r"router\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, content)
    
    # 3. 构建接口信息列表
    api_list = []
    for method, path in matches:
        api_info = {
            "method": method.upper(),
            "path": f"/api/notes{path}" if path != "/" else "/api/notes",
            "full_path": f"/api/notes{path}" if path != "/" else "/api/notes",
            "description": _get_description(method, path),
            "params": _get_params(method, path),
            "success_code": _get_success_code(method),
            "success_response": _get_success_response(method),
            "error_code": 500,
            "error_response": '{"message": "Internal server error"}',
        }
        api_list.append(api_info)
        logger.info(f"  发现接口: {method.upper()} {api_info['path']}")
    
    logger.info(f"共解析出 {len(api_list)} 个接口")
    return api_list


def parse_model(model_file):
    """
    解析数据模型文件，提取字段信息
    
    :param model_file: 模型文件路径（如 ../backend/src/models/Note.js）
    :return: 模型信息字典
    """
    logger.info(f"开始解析模型文件: {model_file}")
    
    with open(model_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取字段定义
    fields = {}
    
    # 匹配格式：title: { type: String, required: true }
    field_pattern = r"(\w+):\s*\{[^}]*type:\s*(\w+)[^}]*\}"
    field_matches = re.findall(field_pattern, content)
    
    for field_name, field_type in field_matches:
        # 检查是否必填
        required_pattern = rf"{field_name}:\s*\{{[^}}]*required:\s*true"
        is_required = bool(re.search(required_pattern, content))
        
        fields[field_name] = {
            "type": field_type,
            "required": is_required,
        }
        logger.info(f"  字段: {field_name} (type={field_type}, required={is_required})")
    
    return {
        "name": os.path.basename(model_file).replace(".js", ""),
        "fields": fields,
    }


# ========== 辅助函数 ==========

def _get_description(method, path):
    """
    根据方法和路径生成接口描述
    """
    descriptions = {
        ("get", "/"): "获取所有笔记",
        ("get", "/:id"): "根据ID获取单条笔记",
        ("post", "/"): "创建笔记",
        ("put", "/:id"): "更新笔记",
        ("delete", "/:id"): "删除笔记",
    }
    return descriptions.get((method, path), f"{method.upper()} {path}")


def _get_params(method, path):
    """
    根据方法生成参数描述
    """
    if method in ("post",):
        return "title(String, 必填), content(String, 必填)"
    elif method in ("put",):
        return "title(String, 可选), content(String, 可选)"
    elif method == "get" and ":id" in path:
        return "id(String, 路径参数)"
    elif method == "delete" and ":id" in path:
        return "id(String, 路径参数)"
    else:
        return "无"


def _get_success_code(method):
    """
    根据方法返回成功状态码
    """
    codes = {
        "get": 200,
        "post": 201,
        "put": 200,
        "delete": 200,
    }
    return codes.get(method, 200)


def _get_success_response(method):
    """
    根据方法返回成功响应示例
    """
    responses = {
        "get": '[{"_id": "xxx", "title": "...", "content": "..."}]',
        "post": '{"message": "Note created succesfully"}',
        "put": '{"_id": "xxx", "title": "...", "content": "..."}',
        "delete": '{"message": "Note deleted successfully"}',
    }
    return responses.get(method, "{}")

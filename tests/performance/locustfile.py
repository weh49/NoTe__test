"""
ThinkBoard API 性能测试脚本

核心机制：catch_response=True
- 默认情况下，Locust 只根据 HTTP 状态码判断成功/失败
- 开启 catch_response 后，你可以手动校验响应体，决定请求是否算"成功"
- 这样可以发现"后端返回200但数据是空壳"的情况
"""
from locust import HttpUser, task, between
import json
import random
import string

class ThinkBoardUser(HttpUser):
    host = "http://localhost:5001"
    wait_time = between(1, 3)

    # 用于存储已创建的笔记ID，实现 CRUD 闭环
    created_note_ids = []

    @task(5)
    def get_all_notes(self):
        """获取所有笔记 - 校验响应体结构"""
        with self.client.get(
            "/api/notes/",
            catch_response=True,  # 开启手动校验
            name="GET /api/notes/"  # 自定义统计名称
        ) as response:
            # 1. 状态码校验
            if response.status_code != 200:
                response.failure(f"状态码错误: {response.status_code}")
                return

            # 2. JSON 解析校验
            try:
                data = response.json()
            except json.JSONDecodeError:
                response.failure("响应不是有效 JSON")
                return

            # 3. 数据类型校验（必须是列表）
            if not isinstance(data, list):
                response.failure(f"期望列表，实际: {type(data)}")
                return

            # 4. 列表非空校验
            if len(data) == 0:
                response.failure("笔记列表为空")
                return

            # 5. 列表项结构校验（抽样第一条）
            first_note = data[0]
            required_fields = ["_id", "title", "content", "createdAt"]
            for field in required_fields:
                if field not in first_note:
                    response.failure(f"缺少字段: {field}")
                    return

            # 全部通过
            response.success()

    @task(3)
    def create_note(self):
        """创建笔记 - 校验创建成功且返回正确消息"""
        # 使用随机数据避免重复
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        payload = {
            "title": f"性能测试-{random_suffix}",
            "content": f"自动生成的测试内容-{random_suffix}"
        }

        with self.client.post(
            "/api/notes/",
            json=payload,
            catch_response=True,
            name="POST /api/notes/"
        ) as response:
            # 1. 状态码校验
            if response.status_code != 201:
                response.failure(f"状态码错误: {response.status_code}, 响应: {response.text}")
                return

            # 2. JSON 解析校验
            try:
                data = response.json()
            except json.JSONDecodeError:
                response.failure("响应不是有效 JSON")
                return

            # 3. 消息字段校验（后端返回的是 message 字段）
            if "message" not in data:
                response.failure(f"缺少 message 字段: {data}")
                return

            # 4. 消息内容校验
            expected_message = "Note created succesfully"  # 注意：后端拼写错误是已知问题
            if data["message"] != expected_message:
                response.failure(f"消息不匹配: 期望 '{expected_message}', 实际 '{data['message']}'")
                return

            # 全部通过
            response.success()

    @task(2)
    def get_note_by_id(self):
        """获取单个笔记 - 校验返回数据完整性"""
        # 如果没有已创建的笔记，先跳过
        if not self.created_note_ids:
            return

        note_id = random.choice(self.created_note_ids)

        with self.client.get(
            f"/api/notes/{note_id}",
            catch_response=True,
            name="GET /api/notes/:id"
        ) as response:
            # 1. 状态码校验
            if response.status_code != 200:
                response.failure(f"状态码错误: {response.status_code}")
                return

            # 2. JSON 解析校验
            try:
                data = response.json()
            except json.JSONDecodeError:
                response.failure("响应不是有效 JSON")
                return

            # 3. 字段存在性校验
            required_fields = ["_id", "title", "content", "createdAt", "updatedAt"]
            for field in required_fields:
                if field not in data:
                    response.failure(f"缺少字段: {field}")
                    return

            # 4. ID 匹配校验（返回的 _id 必须和请求的一致）
            if data["_id"] != note_id:
                response.failure(f"ID 不匹配: 请求 {note_id}, 返回 {data['_id']}")
                return

            response.success()

    @task(1)
    def update_note(self):
        """更新笔记 - 校验更新生效"""
        if not self.created_note_ids:
            return

        note_id = random.choice(self.created_note_ids)
        new_title = f"更新标题-{random.randint(1000, 9999)}"

        with self.client.put(
            f"/api/notes/{note_id}",
            json={"title": new_title, "content": "更新内容"},
            catch_response=True,
            name="PUT /api/notes/:id"
        ) as response:
            # 1. 状态码校验
            if response.status_code != 200:
                response.failure(f"状态码错误: {response.status_code}")
                return

            # 2. JSON 解析校验
            try:
                data = response.json()
            except json.JSONDecodeError:
                response.failure("响应不是有效 JSON")
                return

            # 3. 更新生效校验（标题必须是我们设置的值）
            if data.get("title") != new_title:
                response.failure(f"更新未生效: 期望 '{new_title}', 实际 '{data.get('title')}'")
                return

            response.success()

    def on_start(self):
        """
        每个虚拟用户启动时执行
        用于初始化数据（获取已有笔记ID列表）
        """
        with self.client.get(
            "/api/notes/",
            catch_response=True,
            name="初始化-获取笔记列表"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        # 取前10个笔记ID用于后续测试
                        self.created_note_ids = [note["_id"] for note in data[:10]]
                        response.success()
                    else:
                        response.failure("初始化失败: 响应不是列表")
                except json.JSONDecodeError:
                    response.failure("初始化失败: JSON 解析失败")
            else:
                response.failure(f"初始化失败: 状态码 {response.status_code}")

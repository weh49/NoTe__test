import pytest
import requests
import os
import sys

# 将 tests/ 目录加入 Python 搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.setting import BASE_URL
from config.setting import API_PREFIX
from api.api_client import NoteAPI


@pytest.fixture(scope="session")
def api_client():
    """
    创建一个 requests.Session 对象，供所有测试用例使用。
    scope="session" 表示整个测试过程只创建一次。
    """
    client = requests.Session()
    client.base_url = BASE_URL + API_PREFIX
    client.headers = {"Content-Type": "application/json"}
    client._timeout = 5
    
    yield client
    client.close()

@pytest.fixture(scope="function")
def api_client_with_auth(api_client):
    """
    创建一个 requests.Session 对象，供所有测试用例使用。
    scope="function" 表示每个测试用例创建一次，确保每个测试用例都有一个干净的会话。
    """
    return NoteAPI(api_client)

@pytest.fixture(scope="function")
def note_api(api_client):
    return NoteAPI(api_client)


from faker import Faker
fake = Faker('zh_CN')
@pytest.fixture(scope="class")
def create_and_cleanup_note(api_client):
    """
    利用 Pytest 的 yield 机制，可以实现“测试前创建，测试后自动清理”，
    无论测试成功还是失败，清理代码都会执行
    """
    # 1. Setup（前置准备）：调用创建接口
    # ⚠️ 后端 createNote 仅返回 {"message": "Note created succesfully"}，不返回 _id
    # 因此需要：创建 → 查询列表 → 取最新一条的 _id
    payload = {"title": fake.sentence(), "content": fake.text()}
    create_resp = NoteAPI(api_client).note_create(payload["title"], payload["content"])
    assert create_resp.status_code == 201, f"创建笔记失败: {create_resp.text}"

    # 查询列表，获取刚创建的笔记ID（后端按 createdAt 降序，最新在最前）
    all_notes = NoteAPI(api_client).note_all()
    assert all_notes.status_code == 200, f"查询笔记列表失败: {all_notes.text}"
    note_id = all_notes.json()[0]["_id"]
    
    # 将数据传递给测试用例
    yield note_id 
    
    # 2. Teardown（后置清理）：测试结束后自动删除
    # 即使测试用例报错，这里的代码也会执行，保证不留脏数据
    NoteAPI(api_client).note_delete(note_id)





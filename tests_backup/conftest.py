import pytest
import requests
import allure
import os
from config.settings import BASE_URL,API_PREFIX
from api.notes_api import NoteAPI

@pytest.fixture(scope="session")
def api_client():
    """
    创建一个 requests.Session 对象，供所有测试用例使用。
    scope="session" 表示整个测试过程只创建一次。
    """
    client_url = f"{BASE_URL}{API_PREFIX}"
    client = requests.Session()
    client.base_url = client_url
    client.headers["Content-Type"] = "application/json"
    client._timeout = 10

    yield client
    client.close()

@pytest.fixture(scope="function")
def note_api(api_client):
    return NoteAPI(api_client)

@pytest.fixture(scope="function")
def created_note_id(note_api):
    """
    创建一个测试笔记，返回其 ID。
    测试用例中可以使用这个 ID 来引用这个笔记。
    
    修复：通过标题精确匹配找到刚创建的笔记，避免取到残留数据。
    """
    test_title = "测试笔记"
    test_content = "这是一条测试笔记"
    note_api.create_note(test_title, test_content)
    
    # 通过标题精确匹配，找到刚创建的笔记（取最后一条匹配的，即最新的）
    notes = note_api.get_all_notes().json()
    matched = [n for n in notes if n["title"] == test_title]
    assert len(matched) > 0, f"未找到标题为 '{test_title}' 的笔记，创建可能失败"
    note_id = matched[0]["_id"]

    yield note_id
    
    # 清理：删除测试笔记（即使测试失败也要清理）
    try:
        note_api.delete_note(note_id)
    except Exception:
        pass  # 清理失败不影响测试结果

@pytest.fixture(scope="session", autouse=True)
def allure_env(request):
    results_dir = request.config.getoption("--alluredir", default=None) or "report/allure-results"
    env_file = os.path.join(results_dir, "environment.properties")
    os.makedirs(os.path.dirname(env_file), exist_ok=True)
    with open(env_file, "w") as f:
        f.write("OS=Windows 11\n")
        f.write("Python=3.14\n")
        f.write("Base_URL=http://localhost:5001\n")
        f.write("Tester=weh49\n")







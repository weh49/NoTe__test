import pytest
import requests
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
    """
    note_api.create_note("测试笔记","这是一条测试笔记")
    notes = note_api.get_all_notes().json()
    note_id = notes[0]["_id"]

    yield note_id
    note_api.delete_note(note_id)








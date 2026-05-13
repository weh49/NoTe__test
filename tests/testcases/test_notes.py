import pytest
import allure

@allure.feature("笔记接口")
@allure.story("获取所有笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("获取所有笔记接口-正常场景")
def test_get_all_notes(note_api):
    """
    测试获取所有笔记接口
    """
    response = note_api.get_all_notes()
    assert response.status_code == 200
    assert isinstance(response.json(),list)

@allure.feature("笔记接口")
@allure.story("创建笔记接口")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("创建笔记接口-正常场景")
def test_create_note(note_api):
    """
    测试创建单个笔记接口
    """
    response = note_api.create_note("测试笔记","这是一条测试笔记")
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Note created succesfully"

@allure.feature("笔记接口")
@allure.story("获取单个笔记接口")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("获取单个笔记接口-正常场景")
def test_get_one_note(note_api,created_note_id):
    """
    测试获取单个笔记接口
    """
    response = note_api.get_one_note(created_note_id)
    assert response.status_code == 200
    
@allure.feature("笔记接口")
@allure.story("更新笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("更新笔记接口-正常场景")
def test_update_note(note_api,created_note_id):
    """
    测试更新笔记接口
    """
    response = note_api.update_note(created_note_id, 
    {"title": "更新后的笔记", "content": "这是一条更新后的笔记"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "更新后的笔记"
    assert data["content"] == "这是一条更新后的笔记"

@allure.feature("笔记接口")
@allure.story("删除笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("删除笔记接口-正常场景")
def test_delete_note(note_api,created_note_id):
    """
    测试删除笔记接口
    """
    response = note_api.delete_note(created_note_id)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Note deleted successfully"



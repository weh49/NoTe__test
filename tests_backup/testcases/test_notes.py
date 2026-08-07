import pytest
import allure
from utils.assertions import (
    assert_status_code,
    assert_json_message,
    assert_is_list,
    assert_json_field_value,
)

@allure.feature("笔记接口")
@allure.story("获取所有笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("获取所有笔记接口-正常场景")
def test_get_all_notes(note_api):
    """
    测试获取所有笔记接口
    """
    response = note_api.get_all_notes()
    assert_status_code(response, 200)
    assert_is_list(response)

@allure.feature("笔记接口")
@allure.story("创建笔记接口")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("创建笔记接口-正常场景")
def test_create_note(note_api):
    """
    测试创建单个笔记接口
    """
    test_title = "测试笔记_创建"
    test_content = "这是一条测试笔记"
    response = note_api.create_note(test_title, test_content)
    assert_status_code(response, 201)
    assert_json_message(response, "Note created succesfully")

    # 清理：通过标题精确匹配刚创建的笔记，而不是盲目取第一条
    notes = note_api.get_all_notes().json()
    matched = [n for n in notes if n["title"] == test_title]
    if matched:
        note_api.delete_note(matched[0]["_id"])

@allure.feature("笔记接口")
@allure.story("获取单个笔记接口")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("获取单个笔记接口-正常场景")
def test_get_one_note(note_api, created_note_id):
    """
    测试获取单个笔记接口
    """
    response = note_api.get_one_note(created_note_id)
    assert_status_code(response, 200)
    
@allure.feature("笔记接口")
@allure.story("更新笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("更新笔记接口-正常场景")
def test_update_note(note_api, created_note_id):
    """
    测试更新笔记接口
    """
    response = note_api.update_note(
        created_note_id,
        {"title": "更新后的笔记", "content": "这是一条更新后的笔记"}
    )
    assert_status_code(response, 200)
    assert_json_field_value(response, "title", "更新后的笔记")
    assert_json_field_value(response, "content", "这是一条更新后的笔记")

@allure.feature("笔记接口")
@allure.story("删除笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("删除笔记接口-正常场景")
def test_delete_note(note_api, created_note_id):
    """
    测试删除笔记接口
    """
    response = note_api.delete_note(created_note_id)
    assert_status_code(response, 200)
    assert_json_message(response, "Note deleted successfully")



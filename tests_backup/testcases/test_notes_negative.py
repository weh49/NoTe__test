import pytest
import allure

@allure.feature("笔记接口")
@allure.story("创建笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("创建笔记接口-负向场景")
@pytest.mark.xfail(reason= "后端缺少参数校验")
@pytest.mark.parametrize("title, content, expected",
[("","hello",400),("测试笔记","",400),(None,"hello",400),
("a"*100,"",400),("","a"*100,400)])
def test_create_note_negative(note_api,title,content,expected):
    """
    测试创建笔记接口的负向场景
    """
    response = note_api.create_note(title,content)
    assert response.status_code == expected

@allure.feature("笔记接口")
@allure.story("获取单个笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("获取单个笔记接口-负向场景")
@pytest.mark.xfail(reason= "后端缺少参数校验,非法ID格式")
def test_get_note_get(note_api):
    """
    测试获取笔记接口的负向场景
    """
    response = note_api.get_one_note("abc")
    assert response.status_code == 400

@allure.feature("笔记接口")
@allure.story("更新笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("更新笔记接口-负向场景")
@pytest.mark.xfail(reason= "后端缺少参数校验,非法ID格式")
def test_get_note_update(note_api):
    """
    测试获取笔记接口的负向场景_更新
    """
    response_1 = note_api.update_note("abc",{"title": "更新后的笔记", "content": "这是一条更新后的笔记"})
    assert response_1.status_code == 400
    
@allure.feature("笔记接口")
@allure.story("删除笔记接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("删除笔记接口-负向场景")
@pytest.mark.xfail(reason= "后端缺少参数校验,非法ID格式")
def test_get_note_delete(note_api):
    """
    测试获取笔记接口的负向场景_删除
    """
    response_2 = note_api.delete_note("abc")
    assert response_2.status_code == 400

@allure.feature("笔记接口")
@allure.story("获取笔记ID接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("获取笔记ID接口-负向场景")
def test_get_ID_get(note_api):
    """
    测试获取笔记ID接口的负向场景
    """
    response = note_api.get_one_note("000000000000000000000000")
    assert response.status_code == 404
    assert response.json()["message"] == "Note not found"

@allure.feature("笔记接口")
@allure.story("更新笔记ID接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("更新笔记ID接口-负向场景")
def test_get_ID_update(note_api):
    """
    测试获取笔记ID接口的负向场景_更新
    """
    response_1 = note_api.update_note("000000000000000000000000",
    {"title": "更新错误笔记", "content": "这是一条更新错误笔记"})
    assert response_1.status_code == 404
    assert response_1.json()["message"] == "Note not found"

@allure.feature("笔记接口")
@allure.story("删除笔记ID接口")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("删除笔记ID接口-负向场景")
def test_get_ID_delete(note_api):
    """
    测试获取笔记ID接口的负向场景_删除
    """
    response_2 = note_api.delete_note("000000000000000000000000")
    assert response_2.status_code == 404
    assert response_2.json()["message"] == "Note not found"

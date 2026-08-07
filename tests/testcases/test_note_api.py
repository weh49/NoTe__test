import pytest
import allure
from api.api_client import NoteAPI
from data.testdata import generate_test_data,generate_boundary_test_data,generate_invalid_test_data
from data.testdata import _build_invalid_params
from faker import Faker
from utils.assertions import assert_status_code,assert_message,assert_list_not_empty
from utils.assertions import assert_field_not_empty, assert_field_value, assert_descending_order
fake = Faker('zh_CN')

@allure.epic("笔记管理系统")
@allure.feature("笔记API——CREATE")
class TestNoteAPI:
    @allure.story("创建笔记")
    @allure.title("创建笔记 - 正向测试")
    @allure.description("使用有效数据创建笔记，验证返回状态码和消息")
    @pytest.mark.create
    @pytest.mark.positive
    @pytest.mark.parametrize("test_data", generate_test_data().to_dict('records'))
    def test_create_note(self, api_client, test_data):
        """创建笔记接口测试"""
        # 正向测试
        
        response = NoteAPI(api_client).note_create(test_data["title"], test_data["content"])
        assert_status_code(response, 201)
        assert_message(response, "Note created succesfully")

    @allure.story("创建笔记")
    @allure.title("创建笔记 - 边界值测试")
    @allure.description("使用边界值和无效数据创建笔记，验证后端校验逻辑")
    @pytest.mark.create
    @pytest.mark.boundary
    @pytest.mark.xfail(reason="BUG-003: 后端统一返回500", strict=True)
    @pytest.mark.parametrize("test_data", generate_boundary_test_data().to_dict('records') + _build_invalid_params())
    def test_create_note_base_data(self, api_client, test_data):
        """创建笔记接口测试"""
        # 边界值测试
        response = NoteAPI(api_client).note_create(test_data["title"], test_data["content"])
        assert_status_code(response, 400)
        assert_message(response, "Internal server error")

    @allure.story("创建笔记")
    @allure.title("创建笔记 - 负向测试")
    @allure.description("使用无效数据创建笔记，验证后端错误处理")
    @pytest.mark.create
    @pytest.mark.negative
    @pytest.mark.parametrize("test_data", _build_invalid_params())
    def test_create_invalid_data(self, api_client, test_data):
        """创建笔记接口测试"""
        # 负向测试
        response = NoteAPI(api_client).note_create(test_data["title"], test_data["content"])
        assert_status_code(response, 400)
        assert_message(response, "Internal server error")

@allure.epic("笔记管理系统")
@allure.feature("笔记API——GET")
class TestNoteAPIGet:
    """测试获取所有笔记列表接口"""
    @allure.story("获取笔记列表")
    @allure.title("获取所有笔记 - 正向测试")
    @allure.description("获取笔记列表，验证返回状态码、列表非空、字段完整性和排序")
    @pytest.mark.read
    @pytest.mark.positive
    def test_get_all_note(self, api_client):
        """获取所有笔记数据接口测试"""
        response = NoteAPI(api_client).note_all()
        notes = response.json()
        assert_status_code(response, 200)
        assert_list_not_empty(notes, "笔记列表为空")
        assert_field_not_empty(notes[0], "_id", "第一条笔记缺少 _id")
        assert_descending_order(notes, "createdAt", "笔记列表不是按创建时间降序排列")

@allure.epic("笔记管理系统")
@allure.feature("笔记API——GET")
class TestNoteAPIGetOne:
    """测试获取单个笔记详情接口的 ID 边界值测试"""
    @allure.story("获取单个笔记")
    @allure.title("获取单个笔记 - ID边界值测试")
    @allure.description("测试不同长度和格式的ID，验证后端边界处理")
    @pytest.mark.read
    @pytest.mark.boundary
    @pytest.mark.parametrize("test_name, note_id, expected_status", [
        # 1. 边界测试：长度 23 (下界 - 1)
        ("边界测试_长度23(下界-1)", fake.hexify(text='^' * 23), 500),
        # 2. 边界测试：长度 24 (下界/上界) - 合法格式但不存在
        ("边界测试_长度24(合法但不存在)", fake.hexify(text='^' * 24), 404),
        # 3. 边界测试：长度 25 (上界 + 1)
        ("边界测试_长度25(上界+1)", fake.hexify(text='^' * 25), 500),
        # 4. 边界测试：字符集越界 (23个合法字符 + 1个非法十六进制字符 'g')
        ("边界测试_非法十六进制字符", fake.hexify(text='^' * 23) + 'g', 500),
        # 5. 边界测试：空 ID (空字符串) - BUG-005: 空ID未拦截，路由匹配到列表路由
        # 预期应返回 400，但后端空ID匹配到列表接口返回 200
        pytest.param("边界测试_空ID", "", 400,
                     marks=pytest.mark.xfail(reason="BUG-005: 空ID未拦截，路由匹配到列表接口返回200"),
                     id="空ID"),
])
    def test_get_note_id_boundary(self, test_name, api_client, note_id, expected_status):
        """
        校验获取单个笔记时，传入边界长度的 ID 是否能正确处理
        """
        response = NoteAPI(api_client).note_one(note_id)
        
        assert response.status_code == expected_status, (
            f"请求ID: {note_id} (长度: {len(note_id)})\n"
            f"预期状态码: {expected_status}\n"
            f"实际状态码: {response.status_code}\n"
            
            f"响应内容: {response.text}\n"
            f"测试 [{test_name}] 结果: {response.status_code}"
        )

    @allure.story("获取单个笔记")
    @allure.title("获取单个笔记 - 正向测试")
    @allure.description("获取单个笔记详情，验证返回状态码、字段完整性")
    @pytest.mark.read
    @pytest.mark.positive
    def test_get_note_id(self, api_client, create_and_cleanup_note):
        """获取单个笔记数据接口测试"""
        response = NoteAPI(api_client).note_one(create_and_cleanup_note)
        assert_status_code(response, 200)
        resp_json = response.json()
        assert_field_not_empty(resp_json, "title", "返回的笔记标题为空")
        assert_field_not_empty(resp_json, "content", "返回的笔记内容为空")
        assert_field_not_empty(resp_json, "createdAt", "返回的创建时间为空")

@allure.epic("笔记管理系统")
@allure.feature("笔记API——UPDATE")
class TestNoteAPIUpdate:
    """测试更新笔记接口"""
    @allure.story("更新笔记")
    @allure.title("更新笔记 - 正向测试")
    @allure.description("更新笔记内容，验证返回状态码、字段完整性")
    @pytest.mark.update
    @pytest.mark.positive
    def test_update_note(self, api_client, create_and_cleanup_note):
        """更新笔记接口测试"""
        response = NoteAPI(api_client).note_update(create_and_cleanup_note,
                        title="Updated Title", content="Updated Content")
        assert_status_code(response, 200)
        resp_json = response.json()
        assert_field_value(resp_json, "title", "Updated Title")
        assert_field_value(resp_json, "content", "Updated Content")

    @allure.story("更新笔记")
    @allure.title("更新笔记 - 负向测试")
    @allure.description("使用无效数据更新笔记，验证后端错误处理")
    @pytest.mark.update
    @pytest.mark.negative
    @pytest.mark.parametrize("test_name, note_id, expected_status", [
        # 1. 边界测试：长度 23 (下界 - 1)
        ("边界测试_长度23(下界-1)", fake.hexify(text='^' * 23), 500),
        # 2. 边界测试：长度 24 (下界/上界) - 合法格式但不存在
        ("边界测试_长度24(合法但不存在)", fake.hexify(text='^' * 24), 404),
        # 3. 边界测试：长度 25 (上界 + 1)
        ("边界测试_长度25(上界+1)", fake.hexify(text='^' * 25), 500),
        # 4. 边界测试：字符集越界 (23个合法字符 + 1个非法十六进制字符 'g')
        ("边界测试_非法十六进制字符", fake.hexify(text='^' * 23) + 'g', 500),
        # 5. 边界测试：空 ID (空字符串) - BUG-005: 空ID未拦截，路由匹配到列表路由
        # 预期应返回 400，但后端空ID匹配到列表接口返回 200
        pytest.param("边界测试_空ID", "", 400,
                     marks=pytest.mark.xfail(reason="BUG-005: 空ID未拦截，路由匹配到列表接口返回200"),
                     id="空ID"),
])
    def test_update_note_invalid_id(self, api_client, test_name, note_id, expected_status):
        """
        校验更新笔记时，传入无效/边界长度的 ID 是否能正确处理
        """
        response = NoteAPI(api_client).note_update(note_id, title="Updated", content="Updated")
        
        assert response.status_code == expected_status, (
            f"测试 [{test_name}] 失败！\n"
            f"请求ID: {note_id} (长度: {len(note_id)})\n"
            f"预期状态码: {expected_status}\n"
            f"实际状态码: {response.status_code}\n"
            f"响应内容: {response.text}"
        )

@allure.epic("笔记管理系统")
@allure.feature("笔记API——DELETE")
class TestNoteAPIDelete:
    """测试删除笔记接口"""
    @allure.story("删除笔记")
    @allure.title("删除笔记 - 正向测试")
    @allure.description("删除笔记，验证返回状态码、消息")
    @pytest.mark.delete
    @pytest.mark.positive
    def test_delete_note(self, api_client, create_and_cleanup_note):
        """删除笔记接口测试"""
        note_id = create_and_cleanup_note
        response = NoteAPI(api_client).note_delete(note_id)
        assert_status_code(response, 200)
        assert_message(response, "Note deleted successfully")
        # 【核心闭环验证】再次查询该笔记，必须返回 404
        get_response = NoteAPI(api_client).note_one(note_id)
        assert_status_code(get_response, 404)
        assert_message(get_response, "Note not found")

    @allure.story("删除笔记")
    @allure.title("删除笔记 - 负向测试")
    @allure.description("尝试删除一个不存在的笔记，验证返回状态码、消息")
    @pytest.mark.delete
    @pytest.mark.negative
    def test_delete_non_existent_note(self, api_client):
        """
        反向测试：尝试删除一个数据库中不存在的笔记
        """
        non_existent_id = fake.hexify(text='^' * 24)
        
        response = NoteAPI(api_client).note_delete(non_existent_id)
        
        # 规范接口应该返回 404 Not Found
        assert response.status_code == 404




 

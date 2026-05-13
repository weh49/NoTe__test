import json
import allure

class NoteAPI:
    def __init__(self,api_client):
        self.api_client = api_client

    def get_all_notes(self):
        """
        获取所有笔记接口
        """
        url = self.api_client.base_url + "/"
        allure.attach(url, name="请求URL", attachment_type=allure.attachment_type.TEXT)

        response = self.api_client.get(url,
                timeout = self.api_client._timeout)

        allure.attach(response.text,
        "响应体", allure.attachment_type.JSON)
        return response

    def get_one_note(self,note_id):
        """
        获取单个笔记接口
        """
        url = self.api_client.base_url + f"/{note_id}"
        allure.attach(url, name="请求URL", attachment_type=allure.attachment_type.TEXT)

        response = self.api_client.get(url,
                timeout = self.api_client._timeout)

        allure.attach(response.text,
        "响应体", allure.attachment_type.JSON)
        return response

    def create_note(self,title,content):
        """
        创建笔记接口
        """
        url = self.api_client.base_url + "/"
        note_data = {
            "title": title,
            "content": content
        }
        allure.attach(url, name="请求URL", attachment_type=allure.attachment_type.TEXT)
        allure.attach(json.dumps(note_data, ensure_ascii=False),
        "请求体", allure.attachment_type.JSON)

        response = self.api_client.post(url,
                json = note_data,
                timeout = self.api_client._timeout)

        allure.attach(response.text,
        "响应体", allure.attachment_type.JSON)
        return response

    def update_note(self,note_id,note_data):
        """
        更新笔记接口
        """
        url = self.api_client.base_url + f"/{note_id}"
        allure.attach(url, name="请求URL", attachment_type=allure.attachment_type.TEXT)
        allure.attach(json.dumps(note_data, ensure_ascii=False),
        "请求体", allure.attachment_type.JSON)

        response = self.api_client.put(url,
                json = note_data,
                timeout = self.api_client._timeout)

        allure.attach(response.text,
        "响应体", allure.attachment_type.JSON)
        return response

    def delete_note(self,note_id):
        """
        删除笔记接口
        """
        url = self.api_client.base_url + f"/{note_id}"
        allure.attach(url, name="请求URL", attachment_type=allure.attachment_type.TEXT)

        response = self.api_client.delete(url,
                timeout = self.api_client._timeout)

        allure.attach(response.text,
        "响应体", allure.attachment_type.JSON)
        return response
    

        



        




class NoteAPI:
    def __init__(self, client):
        self.client = client
    
    def note_all(self):
        """
        获取所有笔记
        """
        url = self.client.base_url + "/"
        response = self.client.get(url,timeout = self.client._timeout)
        return response

    def note_one(self, note_id):
        """
        获取单个笔记
        """
        url = self.client.base_url + f"/{note_id}"
        response = self.client.get(url,timeout = self.client._timeout)
        return response

    def note_create(self, title: str, content: str) -> dict:
        """
        创建笔记接口
        """
        url = self.client.base_url + "/"
        data = {
            "title": title, 
            "content": content
        }
        response = self.client.post(url, json=data, timeout = self.client._timeout)
        return response

    def note_update(self, note_id, title: str = None, content: str = None) -> dict:
        """
        更新笔记
        """
        url = self.client.base_url + f"/{note_id}"
        data = {
            "title": title,
            "content": content
        }
        response = self.client.put(url, json=data, timeout = self.client._timeout)
        return response

    def note_delete(self, note_id):
        """
        删除笔记
        """
        url = self.client.base_url + f"/{note_id}"
        response = self.client.delete(url, timeout = self.client._timeout)
        return response

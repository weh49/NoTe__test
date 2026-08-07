"""
测试数据模块
通过faker生成测试数据，用于接口测试。
生成数据50条。
"""
import pytest
from faker import Faker
import pandas as pd

def _build_invalid_params():
    """将生成的负向数据转换为带 xfail 标记的参数列表"""
    records = generate_invalid_test_data().to_dict('records')
    params = []
    for i, item in enumerate(records):
        title_len = len(item["title"])
        content_len = len(item["content"])

        if item["title"] == "" or item["content"] == "":
            # 空值 → 后端缺少空值校验
            params.append(pytest.param(
                item,
                marks=pytest.mark.xfail(reason="BUG-001: 空值校验缺失"),
                id=f"空值数据-{i}"
            ))
        elif title_len > 20 or content_len > 20:
            # 超长 → 后端缺少 maxlength 校验
            params.append(pytest.param(
                item,
                marks=pytest.mark.xfail(reason="BUG-002: 超长字段校验缺失"),
                id=f"超长数据-{i}"
            ))
        elif title_len < 6 or content_len < 6:
            # 过短 → 后端缺少 minlength 校验
            params.append(pytest.param(
                item,
                marks=pytest.mark.xfail(reason="BUG-002: 过短字段校验缺失"),
                id=f"过短数据-{i}"
            ))
        elif title_len == 20 or content_len == 20:
            # 恰好20字符 = 合法上限，不是无效数据
            params.append(pytest.param(
                item,
                marks=pytest.mark.xfail(reason="合法边界值(20字符=上限)，不应出现在无效数据中"),
                id=f"合法边界-{i}"
            ))
        else:
            params.append(pytest.param(item, id=f"其他无效-{i}"))
    return params

def generate_test_data():

    """
    生成测试数据
    """
    fake = Faker('zh_CN')
    faker_data = [{
        "_id": str(fake.uuid4()),
        "title": fake.sentence(),
        "content": fake.text(),
        "createdAt": fake.date_time(),
        "updatedAt": fake.date_time()}
        for i in range(50)]
    df = pd.DataFrame(faker_data)
    df.to_json('E:\\GIThup\\thinkboard-mod-tut\\tests\\data\\test_data.json', index=False, date_format='iso')
    return df

def generate_boundary_test_data():
    """
    生成边界值测试数据
    """
    fake = Faker('zh_CN')
    base_word = fake.word()
    while len(base_word) < 5:
        base_word += fake.word()
    base_word_min1 = base_word[:5]# 边界值下限-1
    base_word_min = base_word[:6]# 边界值下限
    base_word_max = (base_word * 4)[:20]# 边界值上限
    base_word_max1 = base_word_max + fake.word()
    boundary_data = [
        {"title": base_word_min1, "content": base_word_min},
        {"title": base_word_min, "content": base_word_min1},
        {"title": base_word_max, "content": base_word_min},
        {"title": base_word_min, "content": base_word_max},
        {"title": base_word_max1, "content": base_word_min},
        {"title": base_word_min, "content": base_word_max1},
    ]
    df_boundary_data = pd.DataFrame(boundary_data)
    df_boundary_data.to_json('E:\\GIThup\\thinkboard-mod-tut\\tests\\data\\boundary_data.json', index=False, date_format='iso')
    return df_boundary_data

def generate_invalid_test_data():
    """
    生成负向测试数据
    """
    fake = Faker('zh_CN')
    base_word = fake.word()
    while len(base_word) < 5:
        base_word += fake.word()
    base_word_min1 = base_word[:5]# 边界值下限-1
    base_word_min = base_word[:6]# 边界值下限
    base_word_max = (base_word * 4)[:20]# 边界值上限
    base_word_max1 = base_word_max + fake.word()
    invalid_data = [
        {"title": "", "content": base_word_min},
        {"title": base_word_min, "content": ""},
        {"title": base_word_min1, "content": base_word_min},
        {"title": base_word_min, "content": base_word_min1},
        {"title": base_word_max, "content": base_word_min},
        {"title": base_word_min, "content": base_word_max},
        {"title": base_word_max1, "content": base_word_min},
        {"title": base_word_min, "content": base_word_max1},
    ]
    df_invalid_data = pd.DataFrame(invalid_data)
    df_invalid_data.to_json('E:\\GIThup\\thinkboard-mod-tut\\tests\\data\\invalid_test_data.json', index=False, date_format='iso')
    return df_invalid_data
    
    

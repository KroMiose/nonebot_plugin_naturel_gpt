from typing import Dict, Optional
from .utils import fetch, md5
from .config import config

try:
    import ujson as json
except ImportError:
    import json


def check_presethub_connection():
    try:
        fetch(config.PRESETHUB_BED_URL + "/ping", timeout=30)
        return True
    except Exception:
        return False


def req_preset_hub(api: str, method: str, data: Optional[Dict] = None):
    try:
        res = fetch(
            config.PRESETHUB_BED_URL + api,
            method=method,
            data=data if data else {},
            headers={"Authorization": md5(config.PRESETHUB_ACCESS_TOKEN)},
        )
        print('res =>', res)
        res = json.loads(res)
        if res["code"] == 200:
            return True, res["data"]
        else:
            return False, res.get("msg", "未知错误")
    except Exception:
        import traceback
        traceback.print_exc()
        return False, "与预设库服务端通信出现异常"


def upload_preset(
    name: str,
    preset_key: str,
    self_intro: str,
    uploader: str = "",
    description: str = "",
):
    return req_preset_hub(
        "/preset/create",
        "post",
        {
            "name": name,
            "preset_key": preset_key,
            "self_intro": self_intro,
            "uploader": uploader,
            "description": description,
        },
    )


def get_preset(_id: str, with_use: bool = False):
    return req_preset_hub(f"/preset/detail?_id={_id}&use={with_use}", "get")


def search_preset(keyword: str, page: int = 1, page_size: int = 10):
    return req_preset_hub(
        "/preset/list",
        "post",
        {
            "condition": {
                "page": page,
                "page_size": page_size,
                "order_by": {"field_name": "used_count", "desc": True},
                "keyword": keyword,
                "filters": [],
            }
        },
    )


def delete_preset(_id: str):
    return req_preset_hub(f"/preset/delete?_id={_id}", "delete")

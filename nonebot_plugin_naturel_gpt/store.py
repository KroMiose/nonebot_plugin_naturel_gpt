from collections import deque
import json
from typing import Any, Dict, Union
from typing_extensions import Self
from .logger import logger


class StoreSerializable:
    """
        此类型用于支持自定义对象的Json的序列化与反序列化

        请保证__init__方法在无参数的情况下可以使用，对象的值将通过__dict__直接注入。

        存在列表或字典时请主动构造！
    """

    def _serializable(self) -> Dict[str, Any]:
        """
            序列化对象，该方法在保存时自动调用（通过JSONEncode）
            
            忽略以`_`或`tmp_`起始的属性。
            
            不以下划线开始且值为基础类型或实现了StoreSerializable的字段
        """
        rtn = {}

        for key in self.__dict__:
            if key.startswith("_") or key.startswith("tmp_"):
                continue
            val = self.__dict__[key]
            if not (val is None or isinstance(val, StoreSerializable)
                    or isinstance(val, int) or isinstance(val, str)
                    or isinstance(val, dict) or isinstance(val, float)
                    or isinstance(val, list) or isinstance(val, tuple)
                    or isinstance(val, bool) or isinstance(val, deque)):
                # 如果不是基本类型或者实现了StoreSerializable则会被忽略，并发出警告
                logger.warning(f"{type(self)}的 {key} 中存在无法序列化的对象 {type(val)}")
                continue
            if isinstance(val, deque):
                val = list(val)
            elif isinstance(val, StoreSerializable):
                val = val._serializable()
            rtn[key] = val
        return rtn

    def _init_from_dict(self, self_dict: Dict[str, Any]) -> Self:
        """
            初始化实例，该方法在加载时自动调用。

            如若需要自定义加载，请覆盖此方法。
        """
        self.__dict__.update(self_dict)
        return self

    @classmethod
    def _load_from_dict(cls, self_dict: Union[Dict[str, Any], Self]) -> Self:
        """
            从字典中生成本类的实例，该方法在加载时自动调用，同时也会调用`_init_from_dict`方法
            
            **非必要请勿覆写此方法**
        """
        assert isinstance(self_dict, dict)
        return cls()._init_from_dict(self_dict)


class StoreEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, StoreSerializable):
            return obj._serializable()
        else:
            return super(StoreEncoder, self).default(obj)

# coding=utf8
import copy
import json
from datetime import datetime
from io import StringIO
from typing import Optional, List

import numpy
import pandas
from pydantic import BaseModel

from . import XLContext
from ..Base import AISerializeObject


class XLLinkDE(BaseModel):
    key: str
    data_type: str
    data: object
    encode_type: Optional[str] = ''
    encode_data_off: Optional[int] = 0
    trace_info: Optional[dict] = {}


class XLDE(AISerializeObject):
    def __init__(self, key, data_type, data, encode_type='',
                 encode_data_off=0, trace_info=None):
        # 类型
        self.data_type = data_type
        # key
        self.key = key
        # 数据
        self.data = data
        self.trace_info: dict = {} if trace_info is None else trace_info
        # 是否运行编码
        self.encode_type = encode_type
        self.encode_data_off = encode_data_off
        self.encode_list = []

        self.covertData()
        pass

    def setTrace_info(self, link_id, up_trace_info=None):
        self.trace_info['newest_link_id'] = link_id
        if "link_id_list" in self.trace_info:
            self.trace_info.get("link_id_list").append(link_id)
        else:
            self.trace_info['link_id_list'] = [link_id]
        if up_trace_info is not None:
            self.trace_info['up_trace_info'] = copy.deepcopy(up_trace_info)
        return self
        pass

    def __str__(self):
        if self.data_type == 'datetime' and isinstance(self.data, datetime):
            str_data = self.data.strftime("%Y-%m-%d %H:%M:%S")
        elif self.data_type == 'ndarray' and isinstance(self.data, numpy.ndarray):
            # 将numpy数组转换为列表
            data_list = self.data.tolist()
            # 将数据转换为JSON格式的字符串
            str_data = json.dumps(data_list, ensure_ascii=False)
        elif self.data_type == 'DataFrame':
            str_data = 'DataFrame'
        else:
            str_data = self.data
        return '<{}>{}'.format(self.key, str_data)
        pass

    def covertData(self):
        if self.data_type == 'datetime' and isinstance(self.data, str):
            self.data = datetime.strptime(self.data, "%Y-%m-%d %H:%M:%S")
        if self.data_type == 'ndarray' and isinstance(self.data, str):
            self.data = numpy.asarray(json.loads(self.data))
        if self.data_type == 'DataFrame' and isinstance(self.data, str):
            from ...Util import XLRedisUtil
            data_str = XLRedisUtil().get_data_client().get(self.data)
            if data_str is not None:
                self.data = pandas.read_json(StringIO(data_str))
            else:
                self.data_type = 'expire'
            pass
        pass

    def toLinkDE(self):
        if self.data_type == 'datetime' and isinstance(self.data, datetime):
            str_data = self.data.strftime("%Y-%m-%d %H:%M:%S")
        elif self.data_type == 'ndarray' and isinstance(self.data, numpy.ndarray):
            # 将numpy数组转换为列表
            data_list = self.data.tolist()
            # 将数据转换为JSON格式的字符串
            str_data = json.dumps(data_list, ensure_ascii=False)
        elif self.data_type == 'DataFrame':
            from ...Util import XLRedisUtil
            str_data = datetime.now().strftime("ext-data-DataFrame-%Y%m%d_%H%M%S_%f")
            # 默认10分钟 为了debug 先弄一天
            XLRedisUtil().get_data_client().set(str_data, self.data.to_json(), ex=86400)
        else:
            str_data = self.data

        return {
            'key': self.key,
            'data_type': self.data_type,
            'encode_type': self.encode_type,
            'encode_data_off': self.encode_data_off,
            'data': str_data,
            'trace_id_list': [],
            'trace_info': copy.deepcopy(self.trace_info)
        }
        pass


class XLDataUtil(object):

    @staticmethod
    def INPUT_Build(data_info: XLLinkDE) -> XLDE:
        entity: XLDE = XLDE(key=data_info.key, data_type=data_info.data_type, data=data_info.data,
                            encode_type=data_info.encode_type,
                            encode_data_off=data_info.encode_data_off,
                            trace_info=copy.deepcopy(data_info.trace_info))
        return entity
        pass

    @staticmethod
    def SELF_Build(key, data, context: XLContext, data_type=None, up_trace_info=None) -> XLDE:
        if data_type is None:
            data_type = type(data).__name__
        entity: XLDE = XLDE(key=key, data_type=data_type, data=data)
        entity.setTrace_info(context.context_id, up_trace_info=up_trace_info)
        return entity
        pass

    @staticmethod
    def STEP_Build(data_info: dict, context: XLContext = None, up_trace_info=None) -> XLDE:
        data_type = data_info.get('data_type')
        data = data_info.get('data')
        encode_type = '' if data_info.get('encode_type') is None else data_info.get('encode_type')
        encode_data_off = 0 if data_info.get('encode_data_off') is None else data_info.get('encode_data_off')

        entity: XLDE = XLDE(key=data_info.get('key'), data_type=data_type, data=data, encode_type=encode_type,
                            encode_data_off=encode_data_off, trace_info=copy.deepcopy(data_info.get('trace_info')))
        if context is not None:
            entity.setTrace_info(context.context_id, up_trace_info=up_trace_info)
        return entity
        pass

    @staticmethod
    def FUNC_Build(key, data, link_id, up_trace_info=None) -> XLDE:
        data_type = type(data).__name__
        entity: XLDE = XLDE(key=key, data_type=data_type, data=data)
        entity.setTrace_info(link_id, up_trace_info=up_trace_info)
        return entity
        pass

    @staticmethod
    def LIST_DE_Build(key, data_de_list: list, context: XLContext, up_trace_info=None) -> XLDE:
        run_data_de_list = []
        for data_de in data_de_list:
            if isinstance(data_de, XLDE):
                run_data_de_list.append(data_de.toLinkDE())
            elif isinstance(data_de, XLLinkDE):
                run_data_de_list.append(data_de.__dict__)
            else:
                run_data_de_list.append(data_de)

        data = [de.get('data') for de in run_data_de_list]
        entity: XLDE = XLDE(key=key, data_type="xl_list", data=data)
        entity.setTrace_info(context.context_id, up_trace_info=up_trace_info)
        entity.trace_info['data_remark_info'] = [{"trace_info": copy.deepcopy(de.get('trace_info')), "data_type": de.get('data_type')} for de in data_de_list]
        return entity
        pass


pass

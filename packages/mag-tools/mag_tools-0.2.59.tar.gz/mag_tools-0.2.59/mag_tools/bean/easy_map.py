from typing import Any, Dict, Type, TypeVar, Optional
from datetime import datetime, date
from decimal import Decimal
import json

K = TypeVar('K')
V = TypeVar('V')

class EasyMap(Dict[K, V]):
    """
    Map简化操作类

    @author xlcao
    @version 2.2
    @copyright Copyright (c) 2015
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def builder() -> 'EasyMap[str, Any]':
        return EasyMap()

    def add(self, key: K, value: V) -> 'EasyMap[K, V]':
        """
        添加键值及对应的数值

        :param key: 键值
        :param value: 数值
        :return: self
        """
        if value is not None:
            self[key] = value
        return self

    def get_string(self, key: Any) -> Optional[str]:
        """
        从Map中取字符串

        :param key: 键值
        :return: 字符串
        """
        return str(self.get(key)) if self.get(key) is not None else None

    def get_byte(self, key: Any) -> Optional[bytes]:
        """
        从Map中取字节

        :param key: 键值
        :return: 字节
        """
        value = self.get_string(key)
        return bytes(value, 'utf-8') if value else None

    def get_integer(self, key: Any) -> Optional[int]:
        """
        从Map中取整数

        :param key: 键值
        :return: 整数
        """
        value = self.get_string(key)
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def get_short(self, key: Any) -> Optional[int]:
        """
        从Map中取短整数

        :param key: 键值
        :return: 短整数
        """
        return self.get_integer(key)

    def get_long(self, key: Any) -> Optional[int]:
        """
        从Map中取长整数

        :param key: 键值
        :return: 长整数
        """
        return self.get_integer(key)

    def get_double(self, key: Any) -> Optional[float]:
        """
        从Map中取Double

        :param key: 键值
        :return: Double
        """
        value = self.get_string(key)
        try:
            return float(value) if value else None
        except ValueError:
            return None

    def get_float(self, key: Any) -> Optional[float]:
        """
        从Map中取Float

        :param key: 键值
        :return: Float
        """
        return self.get_double(key)

    def get_big_decimal(self, key: Any) -> Optional[Decimal]:
        """
        从Map中取BigDecimal

        :param key: 键值
        :return: BigDecimal
        """
        value = self.get_string(key)
        try:
            return Decimal(value) if value else None
        except ValueError:
            return None

    def get_date(self, key: Any) -> Optional[date]:
        """
        从Map中取日期

        :param key: 键值
        :return: 日期
        """
        value = self.get_string(key)
        try:
            return datetime.strptime(value, '%Y-%m-%d').date() if value else None
        except ValueError:
            return None

    def get_local_date_time(self, key: Any) -> Optional[datetime]:
        """
        从Map中取日期时间

        :param key: 键值
        :return: 日期时间
        """
        value = self.get_string(key)
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if value else None
        except ValueError:
            return None

    def get_local_date(self, key: Any) -> Optional[date]:
        """
        从Map中取日期

        :param key: 键值
        :return: 日期
        """
        return self.get_date(key)

    def get_local_time(self, key: Any) -> Optional[datetime.time]:
        """
        从Map中取时间

        :param key: 键值
        :return: 时间
        """
        value = self.get_string(key)
        try:
            return datetime.strptime(value, '%H:%M:%S').time() if value else None
        except ValueError:
            return None

    def get_timestamp(self, key: str) -> Optional[datetime]:
        """
        从Map中取时间戳

        :param key: 键值
        :return: 时间戳
        """
        return self.get_local_date_time(key)

    def get_boolean(self, key: Any) -> bool:
        """
        从Map中取布尔值

        :param key: 键值
        :return: 布尔值
        """
        value = self.get_string(key)
        return value.lower() in ('y', 'yes', 't', 'true', '1') if value else False

    def get_enum(self, key: Any, enum_type: Type[V]) -> Optional[V]:
        """
        从Map中取枚举

        :param key: 键值
        :param enum_type: 枚举类型
        :return: 枚举值
        """
        value = self.get_string(key)
        if value and enum_type:
            try:
                return enum_type[value]
            except KeyError:
                return None
        return None

    def get_string_by_json(self, key: Any) -> Optional[str]:
        """
        从Map中取字符串（JSON）

        :param key: 键值
        :return: 字符串
        """
        return json.dumps(self.get(key))

    def get_byte_by_json(self, key: Any) -> Optional[bytes]:
        """
        从Map中取字节（JSON）

        :param key: 键值
        :return: 字节
        """
        value = self.get_string_by_json(key)
        return bytes(value, 'utf-8') if value else None

    def get_short_by_json(self, key: Any) -> Optional[int]:
        """
        从Map中取短整数（JSON）

        :param key: 键值
        :return: 短整数
        """
        return self.get_integer_by_json(key)

    def get_integer_by_json(self, key: Any) -> Optional[int]:
        """
        从Map中取整数（JSON）

        :param key: 键值
        :return: 整数
        """
        value = self.get_string_by_json(key)
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def get_long_by_json(self, key: Any) -> Optional[int]:
        """
        从Map中取长整数（JSON）

        :param key: 键值
        :return: 长整数
        """
        return self.get_integer_by_json(key)

    def get_double_by_json(self, key: Any) -> Optional[float]:
        """
        从Map中取Double（JSON）

        :param key: 键值
        :return: Double
        """
        value = self.get_string_by_json(key)
        try:
            return float(value) if value else None
        except ValueError:
            return None

    def get_float_by_json(self, key: Any) -> Optional[float]:
        """
        从Map中取Float（JSON）

        :param key: 键值
        :return: Float
        """
        return self.get_double_by_json(key)

    def get_big_decimal_by_json(self, key: Any) -> Optional[Decimal]:
        """
        从Map中取BigDecimal（JSON）

        :param key: 键值
        :return: BigDecimal
        """
        value = self.get_string_by_json(key)
        try:
            return Decimal(value) if value else None
        except ValueError:
            return None

    def get_date_by_json(self, key: Any) -> Optional[date]:
        """
        从Map中取日期（JSON）

        :param key: 键值
        :return: 日期
        """
        value = self.get_string_by_json(key)
        try:
            return datetime.strptime(value, '%Y-%m-%d').date() if value else None
        except ValueError:
            return None

    def get_local_date_time_by_json(self, key: Any) -> Optional[datetime]:
        """
        从Map中取日期时间（JSON）

        :param key: 键值
        :return: 日期时间
        """
        value = self.get_string_by_json(key)
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if value else None
        except ValueError:
            return None

    def get_local_date_by_json(self, key: Any) -> Optional[date]:
        """
        从Map中取日期（JSON）

        :param key: 键值
        :return: 日期
        """
        return self.get_date_by_json(key)

    def get_local_time_by_json(self, key: Any) -> Optional[datetime.time]:
        """
        从Map中取时间（JSON）

        :param key: 键值
        :return: 时间
        """
        value = self.get_string_by_json(key)
        try:
            return datetime.strptime(value, '%H:%M:%S').time() if value else None
        except ValueError:
            return None

    def get_timestamp_by_json(self, key: str) -> Optional[datetime]:
        """
        从Map中取时间戳（JSON）

        :param key: 键值
        :return: 时间戳
        """
        return self.get_local_date_time_by_json(key)

    def get_boolean_by_json(self, key: Any) -> bool:
        """
        从Map中取布尔值（JSON）

        :param key: 键值
        :return: 布尔值
        """
        value = self.get_string_by_json(key)
        return value.lower() in ('y', 'yes', 't', 'true', '1') if value else False

    def get_enum_by_json(self, key: Any, enum_type: Type[V]) -> Optional[V]:
        """
        从Map中取枚举（JSON）

        :param key: 键值
        :param enum_type: 枚举类型
        :return: 枚举值
        """
        value = self.get_string_by_json(key)
        if value and enum_type:
            try:
                return enum_type[value]
            except KeyError:
                return None
        return None

    def put(self, key: K, value: V) -> V:
        """
        添加键值及对应的数值

        :param key: 键值
        :param value: 数值
        :return: 数值
        """
        return super().__setitem__(key, value)

    def to_map(self) -> Dict[K, V]:
        """
        转为Map

        :return: Map
        """
        return dict(self)

    def get_by_json(self, key: Any, clazz: Type[V]) -> Optional[V]:
        """
        从Map中取对象（JSON）

        :param key: 键值
        :param clazz: 类类型
        :return: 对象
        """
        value = self.get(key)
        return json.loads(value, object_hook=clazz) if value else None

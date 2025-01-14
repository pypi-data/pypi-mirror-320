import inspect
from collections import OrderedDict


# Singleton, TtlSingleton metaclass
# 클래스를 Singleton으로 만들어주는 메타클래스
# Singleton: 클래스 명, init parameter 명, init parameter 값이 동일한 경우 동일한 인스턴스 반환
# TtlSingleton: Singleton과 동일하나, TTL(Time To Live)이 지원되는 Singleton
#
# 작성자: 황용호 (jogakdal@gmail.com)
class Singleton(type):
    """
    Singleton metaclass
    기능:
        클래스 명, init parameter 명, init parameter 값이 동일한 경우 동일한 인스턴스 반환
        셋 중 어느 하나라도 일치하지 않으면 새로운 인스턴스 생성
    사용법:
        class SomeClass(metaclass=Singleton):
    version: v1.2
    history:
        [v1.2][2025/01/13] 클래스 이름만으로도 동일한 인스턴스 여부를 파악하게 하는 옵션 추가(use_class_name_only)
        [v1.1][2024/06/12] 클래스 명 뿐만 아니라 생성자의 파라미터까지 일치해야 동일한 인스턴스로 판단
        [v1.0] 최초 작성
    """

    def __new__(cls, name, bases, dct, **kwargs):
        dct['_use_class_name_only'] = kwargs.get('use_class_name_only', False)
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, **kwargs):
        super().__init__(name, bases, dct, **kwargs)
        cls._instances = cls._make_buffer(cls)

    def __call__(cls, *args, **kwargs):
        instance_key = cls if cls._use_class_name_only \
            else (cls, tuple(Singleton.__get_param_dict(cls, False, *args, **kwargs).items()))

        if instance_key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[instance_key] = instance

        return cls._instances[instance_key]

    @staticmethod
    def _make_buffer(cls):
        return {}

    @staticmethod
    def __get_param_dict(cls, include_self=False, *args, **kwargs):
        params = [
            (p.name, p.default) for p in inspect.signature(cls.__init__).parameters.values()
            if include_self or p.name != 'self'
        ]

        for arg_value, param in zip(args, params):
            param_name, _ = param
            params[params.index(param)] = (param_name, arg_value)

        params_dict = OrderedDict(params)
        for k, v in kwargs.items():
            if k in params_dict:
                params_dict[k] = v

        return params_dict

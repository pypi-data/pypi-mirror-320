from expiringdict import ExpiringDict

from advanced_python_singleton.singleton import Singleton


class TtlSingleton(Singleton):
    """
    TtlSingleton metaclass
    기능:
        Singleton과 동일하나, TTL(Time To Live)이 지원되는 Singleton
        TTL이 지나면 새로운 인스턴스 생성
    사용법:
        class SomeClass(metaclass=TtlSingleton, ttl=60):
    version: v1.2
    history:
        [v1.2][2025/01/13] 클래스 이름만으로도 동일한 인스턴스 여부를 파악하게 하는 옵션 추가(use_class_name_only)
        [v1.0][2024/07/04] 최초 작성
    """

    __DEFAULT_TTL = 60
    __MAX_BUFFER_SIZE = 1000

    def __new__(cls, name, bases, dct, **kwargs):
        dct['_ttl'] = kwargs.get('ttl', TtlSingleton.__DEFAULT_TTL)
        return super().__new__(cls, name, bases, dct, **kwargs)

    @staticmethod
    def _make_buffer(cls):
        return ExpiringDict(max_len=TtlSingleton.__MAX_BUFFER_SIZE, max_age_seconds=cls._ttl)

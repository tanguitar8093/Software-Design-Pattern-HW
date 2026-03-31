from typing import Type, Callable, Optional, Any, TypeVar, overload, Union

T = TypeVar('T')

class Validator:
    def __init__(self, expected_type: Type[T], allow_none: bool = False, rule: Optional[Callable[[T], bool]] = None):
        self.expected_type = expected_type
        self.allow_none = allow_none
        self.rule = rule

    def __set_name__(self, owner, name):
        # 修正：避免與 Big2Game 定義的 _players 衝突，建議改名或統一
        self.private_name = f"_val_{name}" 

    @overload
    def __get__(self, obj: None, objtype: Any) -> 'Validator': ...
    
    @overload
    def __get__(self, obj: Any, objtype: Any) -> T: ...

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = getattr(obj, self.private_name, None)
        # 如果不允許 None 但拿到 None，這通常是初始化順序問題，但在 runtime 應報錯
        return value

    def __set__(self, obj, value):
        if value is None:
            if not self.allow_none:
                raise ValueError(f"屬性不能為 None")
        else:
            if not isinstance(value, self.expected_type):
                raise TypeError(f"期待 {self.expected_type.__name__}")
            if self.rule and not self.rule(value):
                raise ValueError(f"未通過規則驗證")
        setattr(obj, self.private_name, value)
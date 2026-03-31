from typing import Type, Callable, Optional, Any

class Validator:
    """
    [高端技巧] 描述符 (Descriptor) 模式
    用來取代傳統落落長的 @property / @setter，能將所有的變數驗證邏輯封裝並重用，
    既保有 obj.attr = value 的優雅賦值寫法，又做到嚴格的 setter 攔截與防呆。
    """
    def __init__(self, expected_type: Type, allow_none: bool = False, rule: Optional[Callable] = None):
        self.expected_type = expected_type
        self.allow_none = allow_none
        self.rule = rule

    def __set_name__(self, owner, name):
        # 自動建立對應的私有變數名稱，例如定義 players 屬性，背後就會存進 _players
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        # 拿取時依然是去拿背後的 _private 變數
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        # 1. 基礎驗證：檢查 Null
        if value is None:
            if not self.allow_none:
                raise ValueError(f"{self.private_name} 不能被設定為 None")
        else:
            # 2. 型別驗證：擋掉不合法的型別
            if not isinstance(value, self.expected_type):
                raise TypeError(f"設定錯誤: 期待 {self.expected_type.__name__} 型別，但收到了 {type(value).__name__}")
            
            # 3. 商業邏輯驗證：檢查自訂規則
            if self.rule:
                if not self.rule(value):
                    raise ValueError(f"{self.private_name} 設定的數值未通過規則驗證")
        
        # 通過所有驗證後，才真正寫入底層私有屬性
        setattr(obj, self.private_name, value)

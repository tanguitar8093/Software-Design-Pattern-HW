from __future__ import annotations
from abc import ABC, abstractmethod
from models.card import Card
from utils.enums import PlyaerId

class Player(ABC):
    def __init__(self, player_id: PlyaerId):
        self._id: PlyaerId = player_id
        self._hands: list[Card] = []
        self._point: int = 0
        self._name: str = ""
        self._exchange_used: bool = False # 自行補充的屬性, 給 exchange_hands 用的
        self._exchange_partner: Player | None = None # 自行補充的屬性, 給 exchange_hands 用的
        self._exchange_rounds_left: int = 0 # 自行補充的屬性, 給 exchange_hands 用的

    @property
    def id(self) -> PlyaerId:
        return self._id 

    @property
    def hands(self) -> list[Card]:
        return self._hands

    @hands.setter
    def hands(self, cards: list[Card]) -> None:
        self._hands = cards

    @property
    def point(self) -> int:
        return self._point

    @point.setter
    def point(self, value: int) -> None:
        self._point = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def exchange_used(self) -> bool:
        return self._exchange_used

    @exchange_used.setter
    def exchange_used(self, used: bool) -> None:
        self._exchange_used = used

    @property
    def exchange_partner(self) -> Player | None:
        return self._exchange_partner

    @exchange_partner.setter
    def exchange_partner(self, partner: Player | None) -> None:
        self._exchange_partner = partner

    @property
    def exchange_rounds_left(self) -> int:
        return self._exchange_rounds_left

    @exchange_rounds_left.setter
    def exchange_rounds_left(self, rounds: int) -> None:
        self._exchange_rounds_left = rounds

    @abstractmethod
    def name_himself(self) -> None:
        pass

    @abstractmethod
    def exchange_hands(self, players: list[Player]) -> None:
        pass

    @abstractmethod
    def show(self) -> Card:
        pass

    def add_hand(self, card: Card) -> None:
        self._hands.append(card)

    def add_point(self) -> None:
        self._point += 1

    def _do_show(self, card_index: int) -> Card:
        if not self.hands:
            raise ValueError("沒有手牌可出")
        return self.hands.pop(card_index)

    def _do_exchange_hands(self, player: Player) -> None:
        if self._exchange_used:
            raise ValueError("已使用交換手牌特權，無法再次交換")
        self.exchange_partner = player
        self.exchange_rounds_left = 3
        self.hands, player.hands = player.hands, self.hands
        self.exchange_used = True
        print(f"{self.name} 和 {player.name} 交換手牌")

    def resolve_exchange(self) -> None:
        if not self.exchange_partner:
            return
        self.exchange_rounds_left -= 1
        if self.exchange_rounds_left == 0:
            self.hands, self.exchange_partner.hands = self.exchange_partner.hands, self.hands
            print(f"手牌已復原給 {self.name} 和 {self.exchange_partner.name}")
            self.exchange_partner = None
 
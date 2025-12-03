from models.player.human_player import HumanPlayer
from models.player.ai_player import AIPlayer  
from models.desk import Desk
from models.player.player import Player
from models.card import Card
from utils.enums import PlyaerId


class Game:
    def __init__(self, players: list[Player],desk: Desk):
        self._turn: int = 0
        self._players: list[Player] = players
        self._desk: Desk = desk
        self._round_moves: list[tuple[Player, Card]] = [] # 紀錄本回合玩家出牌情況, 覺得有點多餘, 但目前只知道這樣設
        # 驗證初始值
        ids = [player.id for player in self._players]
        if len(ids) != len(set(ids)):
            raise ValueError("玩家 ID 重複")
        if not isinstance(desk, Desk):
            raise TypeError("desk 必須是 Desk 實例")
    @property
    def turn(self) -> int:
        return self._turn

    @turn.setter
    def turn(self, value: int) -> None:
        if value > 13:
            raise ValueError(f"回合數不能超過 13")
        self._turn = value

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def desk(self) -> Desk:
        return self._desk
    def _print_round_moves(self) -> None:
            for player, card in self._round_moves:
                print(f"{player.name} 出牌: {card}")
    def _set_round_victor(self) -> None:
        round_victor_player: Player | None = None
        max_score_card: Card | None = None
        for player, card in self._round_moves:
            if not max_score_card or card > max_score_card:
                max_score_card = card
                round_victor_player = player
        if round_victor_player:
            round_victor_player.add_point()
            print(f"{round_victor_player.name} 贏得此回合！")
    def takes_a_turn(self) -> None: 
        print(f"==== 第 {self.turn + 1} 回合 ====")
        # 檢查目前手牌情況, 並交換手牌
        for player in self._players:
            player.resolve_exchange()
            player.exchange_hands(self._players)
            if player.hands:
                self._round_moves.append((player, player.show()))
        # 不想把很多邏輯塞到這個 function, 所以又分了幾個 function 出來, 但感覺這樣的做法不太對
        # 我對於判斷的演算法沒辦法寫得很精簡, 所以就先這樣寫了
        # Q1: 顯示本回合出牌情況, 以下皆表達得有點醜, 但不知架構如何規劃, 循序圖是否要記錄以下私有方法? 目前是沒有紀錄
        self._print_round_moves()
        # 決定本回合勝者, 表達得有點醜
        self._set_round_victor()
        self._round_moves.clear()
        self.turn += 1
    def print_victor(self) -> None:
        print("==== 遊戲結果 ====")        
        for player in self._players:
            print(f"{player.name} 總分: {player.point}")
    def debug(self) -> None:
        print("==== 玩家資訊 ====")
        for player in self._players:
            print(f"{player.name} (ID: {player.id.name}) - 分數: {player.point}, 手牌數量: {len(player.hands)}, 是否使用交換手牌特權: {player.exchange_used}")
    def start(self) -> None:
        # 為玩家命名
        for player in self._players:
            player.name_himself()
        # 洗牌
        self._desk.shuffle()       
        # 發牌
        for _ in range(13):
            for player in self._players:
                card = self._desk.draw_card()
                player.add_hand(card)   
        # 進行遊戲回合
        for _ in range(13):
            self.takes_a_turn()
        # 印出遊戲結果
        self.print_victor()
        # Q2: Debug 資訊, 主要是確認交換手牌等機制,看起來結果可能會產生多餘手牌, 但不知道如何驗證
        self.debug()

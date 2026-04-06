from __future__ import annotations
from models.player.player import Player
from models.card import Card
from models.pattern import CardPattern

class AIPlayer(Player):
    def name_himself(self, player_index: int) -> None:
        self._name = f"AIplayer_{player_index}"

    def play(self, top_play: CardPattern | None) -> list[Card] | None:
        import itertools
        from functools import cmp_to_key
        from models.handler import SingleHandler, PairHandler, StraightHandler, FullHouseHandler
        from models.enums import Suit, Rank
        from models.pattern import _is_card_less_than

        # 先確保手牌排序，這樣組合出來的牌也會有由小到大的趨勢
        self._hand_cards.sort(key=cmp_to_key(lambda c1, c2: -1 if _is_card_less_than(c1, c2) else 1))

        handler = SingleHandler(PairHandler(StraightHandler(FullHouseHandler())))
        valid_plays = []
        
        # 若是自由出牌則找所有可能長度 (1, 2, 5)，若有上家牌則只找相同數量的牌
        lengths_to_check = [1, 2, 5] if top_play is None else [len(top_play.cards)]

        for length in lengths_to_check:
            if length > len(self._hand_cards):
                continue
            for combo in itertools.combinations(self._hand_cards, length):
                cards_list = list(combo)
                pattern = handler.handle(cards_list)
                
                if pattern:
                    if top_play is None:
                        valid_plays.append((pattern, cards_list))
                    elif type(pattern) is type(top_play) and top_play < pattern:
                        valid_plays.append((pattern, cards_list))
        
        if not valid_plays:
            return None

        # 基礎策略：盡量留大牌，並優先出張數多的組合來消耗手牌
        # 我們自定義一個排序函數，以 (牌型張數, 代表牌大小) 來排序
        def play_key(play_tuple):
            pattern, _ = play_tuple
            # 這裡我們不直接跨型別比較，而是給予權重：同張數我們希望出最小的
            # 若第一手自由出牌，我們優先打 5 張（或按需求），這裡以張數多反而排前面，代表牌最小排前面
            return (-len(pattern.cards), 0)

        # 找出是否擁有梅花 3
        has_club_3 = any(c.suit == Suit.CLUBS and c.rank == Rank.THREE for c in self._hand_cards)

        if top_play is None and has_club_3:
            # 必須出包含梅花 3 的牌型
            club_3_plays = [
                pt for pt in valid_plays 
                if any(c.suit == Suit.CLUBS and c.rank == Rank.THREE for c in pt[1])
            ]
            if club_3_plays:
                # 從包含梅花 3 的合法出牌中挑選最好的出牌
                # 因為手牌已經順排過，第一組抓到的往往就是包含梅花3又相對最小的組合
                return club_3_plays[0][1]

        # 針對找到的所有合法出牌，選擇張數盡量多、且牌值盡量小的那組
        # 由於 itertools.combinations 是照手牌順序生成的，最先被加入 list 的通常代表其組成牌較小
        # 我們可以直接分群後取第一個，或是簡單的排序 (但 CardPattern 間不同 class 不能互比大小)
        # 所以依長度分群，取長度最大中的第一組（也就是最小的組合）
        valid_plays.sort(key=lambda x: -len(x[1]))
        return valid_plays[0][1]
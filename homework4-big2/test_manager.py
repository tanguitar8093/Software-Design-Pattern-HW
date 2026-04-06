import sys
import builtins
import os
from models.deck import Deck
from models.card import Card
from models.enums import Suit, Rank

class TestManager:
    def __init__(self, filename):
        self.filename = filename
        test_dir = os.path.join(os.path.dirname(__file__), "test_data")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        file_path = os.path.join(test_dir, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            self.lines = [line.removesuffix("\n") for line in f.readlines()]
            
        self.cards_line = self.lines[0]
        self.lines = self.lines[1:]
        self.lines.insert(0, "4")
            
        self.out_path = os.path.join(test_dir, filename.replace(".in", ".out_test"))
        self.out_file = open(self.out_path, "w", encoding="utf-8")
        
        self.input_index = 0
        
        self.last_turn_player = None
        
        # Original functions
        self.original_print = builtins.print
        self.original_input = builtins.input
        self.original_shuffle = Deck.shuffle
        
    def mock_input(self, prompt=""):
        if self.input_index < len(self.lines):
            val = self.lines[self.input_index]
            self.input_index += 1
            return val
        return ""
        
    def mock_print(self, *args, **kwargs):
        text = " ".join(str(a) for a in args)
        
        # Filters for test output
        if text == "=== 歡迎來到大老二 (Big-2) 遊戲 ===": return
        if text == "正在準備遊戲...": return
        if "錯誤：" in text: return
        if text.startswith("第 ") and "回合開始！" in text:
            self.out_file.write("新的回合開始了。\n")
            self.last_turn_player = None
            return
        if text.startswith("輪到玩家："):
            name = text.split("：")[1]
            if name != self.last_turn_player:
                self.out_file.write(f"輪到{name}了\n")
                self.last_turn_player = name
            return
        if text.startswith("目前牌面："):
            return # ignore
        if "出牌成功：" in text:
            # "玩家 [name] 出牌成功：[pattern_name] [cards]"
            parts = text.split(" 出牌成功：")
            name = parts[0].replace("玩家 ", "")
            pattern_and_cards = parts[1]
            self.out_file.write(f"玩家 {name} 打出了 {pattern_and_cards}\n")
            return
        if "選擇 Pass" in text:
            name = text.replace("玩家 ", "").replace(" 選擇 Pass", "")
            self.out_file.write(f"玩家 {name} PASS.\n")
            return
        if text == "遊戲結束！":
            return
        if text.startswith("恭喜玩家 "):
            name = text.replace("恭喜玩家 ", "").replace(" 獲勝！", "")
            self.out_file.write(f"遊戲結束，遊戲的勝利者為 {name}\n")
            return
        if text.startswith("玩家 ") and "無法 Pass" in text:
            self.out_file.write("你不能在新的回合中喊 PASS\n")
            return
        if text.startswith("玩家 ") and "出牌失敗" in text:
            self.out_file.write("此牌型不合法，請再嘗試一次。\n")
            return
        if text.startswith("玩家 ") and "擁有梅花 3" in text:
            return
            
        # Write generic output (like card arrays)
        self.out_file.write(text + "\n")
        
    def mock_shuffle(self, deck_instance):
        # Read the first line of inputs to parse cards
        card_strs = self.cards_line.split()
        
        def parse_suit(s):
            return {"C": Suit.CLUBS, "D": Suit.DIAMONDS, "H": Suit.HEARTS, "S": Suit.SPADES}[s]
        
        def parse_rank(r):
            rank_map = {"3": Rank.THREE, "4": Rank.FOUR, "5": Rank.FIVE, "6": Rank.SIX, "7": Rank.SEVEN, 
                        "8": Rank.EIGHT, "9": Rank.NINE, "10": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN, 
                        "K": Rank.KING, "A": Rank.ACE, "2": Rank.TWO}
            return rank_map[r]
            
        cards = []
        for cstr in card_strs:
            suit_str = cstr[0]
            # Since card format is like C[3], find '[' and ']'
            start_idx = cstr.index('[') + 1
            end_idx = cstr.index(']')
            rank_str = cstr[start_idx:end_idx]
            cards.append(Card(parse_rank(rank_str), parse_suit(suit_str)))
            
        deck_instance._cards = cards

    def run(self):
        builtins.print = self.mock_print
        builtins.input = self.mock_input
        def shuffle_wrapper(deck_inst):
            self.mock_shuffle(deck_inst)
        Deck.shuffle = shuffle_wrapper
        
        return self

    def cleanup(self):
        builtins.print = self.original_print
        builtins.input = self.original_input
        Deck.shuffle = self.original_shuffle
        self.out_file.close()


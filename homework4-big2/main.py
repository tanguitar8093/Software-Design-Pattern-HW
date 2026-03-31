from models.player import HumanPlayer, AIPlayer
from models.game import Big2Game

def main():
    print("=== 歡迎來到大老二 (Big-2) 遊戲 ===")
    
    # 讓使用者設定人類玩家與AI玩家的數量 (總數必須為 4)
    while True:
        try:
            num_humans = int(input("請輸入人類玩家數量 (1~4): "))
            if 1 <= num_humans <= 4:
                break
            else:
                print("錯誤：玩家數量必須介於 1 到 4 之間！")
        except ValueError:
            print("錯誤：請輸入有效的數字！")

    num_ai = 4 - num_humans
    players = []

    for _ in range(num_humans):
        players.append(HumanPlayer(""))
    
    for _ in range(num_ai):
        players.append(AIPlayer(""))
    
    # 建立遊戲實體，將 4 位玩家傳入
    game = Big2Game(players)
    
    # 啟動遊戲 (依據循序圖：將依序執行 玩家命名 -> 牌堆洗牌)
    print("正在準備遊戲...")
    game.start()

    print("\n--- 遊戲初始化已完成 ---")
    print("以下是本局遊戲的玩家陣容：")
    for player in game.players:
        print(f"- 玩家名稱: {player.name}, 手牌數量: {len(player.hand_cards)} 張")

if __name__ == "__main__":
    main()

from models.Game import Game
from models.Player.HumanPlayer import HumanPlayer
from models.Player.AIPlayer import AIPlayer

def main():
    # 詢問人類玩家數量，並確保在 0~4 之間
    while True:
        try:
            num_humans = int(input("Enter number of human players (0-4): "))
            if 0 <= num_humans <= 4:
                break
            print("Please enter a number between 0 and 4.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    players = []
    
    # 建立人類玩家
    for _ in range(num_humans):
        players.append(HumanPlayer())
        
    # 其餘補上 AI 玩家，並給予編號
    for i in range(4 - num_humans):
        players.append(AIPlayer(name=str(i + 1)))
    
    # 初始化 Game 並將玩家傳入
    game = Game(players)
    
    # 開始遊戲流程
    game.start()

if __name__ == "__main__":
    main()
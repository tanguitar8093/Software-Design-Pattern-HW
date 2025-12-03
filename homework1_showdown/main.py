from models.desk import Desk
from models.game import Game
from models.player.player import Player
from utils.enums import PlyaerId
from models.player.human_player import HumanPlayer
from models.player.ai_player import AIPlayer
def main():
    """主程式入口"""
    players: list[Player]=[]
    desk: Desk =Desk()
    human_count = int(input(f"請輸入人類玩家數量 (0-4): "))
    # 自動決定 id
    for i in range(4):
        id= PlyaerId(i + 1)
        if i < human_count:
            player = HumanPlayer(id)
        else:
            player = AIPlayer(id)  
        players.append(player)

    game = Game(players=players,desk=desk)
    game.start()

if __name__ == "__main__":
    main()


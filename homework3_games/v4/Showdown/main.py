from models.Game import Game
from models.Player.HumanPlayer import HumanPlayer
from models.Player.AIPlayer import AIPlayer


def main():
    while True:
        try:
            num_humans = int(input("Enter number of human players (0-4): "))
            if 0 <= num_humans <= 4:
                break
            print("Please enter a number between 0 and 4.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    players = []
    for _ in range(num_humans):
        players.append(HumanPlayer())
    for i in range(4 - num_humans):
        players.append(AIPlayer(name=str(i + 1)))

    game = Game(players)
    game.start()


if __name__ == "__main__":
    main()

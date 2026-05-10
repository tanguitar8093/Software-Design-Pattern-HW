from models.unit import Unit
from models.troop import Troop
from models.player import HumanPlayer, AIPlayer
from models.rpg import RPG

if __name__ == '__main__':
    while True:
        try:
            troop_size = int(input("Enter troop size (e.g. 3): "))
            if troop_size >= 1:
                break
            print("Size must be at least 1.")
        except ValueError:
            print("Invalid input. Enter a number.")

    t1_units = [Unit("Hero", 500, 500, 100, HumanPlayer())]
    for i in range(1, troop_size):
        t1_units.append(Unit(f"Ally_{i}", 300, 200, 50, AIPlayer()))
    t1 = Troop(t1_units)

    t2_units = []
    for i in range(troop_size):
        t2_units.append(Unit(f"Enemy_{i+1}", 300, 200, 50, AIPlayer()))
    t2 = Troop(t2_units)

    game = RPG(t1, t2)
    game.start()

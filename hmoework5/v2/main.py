from models.unit import Unit
from models.troop import Troop
from models.player import HumanPlayer, AIPlayer
from models.rpg import RPG
from models.actions import get_all_actions

if __name__ == '__main__':
    while True:
        try:
            troop_size = int(input("Enter troop size (e.g. 3): "))
            if troop_size >= 1:
                break
            print("Size must be at least 1.")
        except ValueError:
            print("Invalid input.")

    t1_units = [Unit("Hero", 500, 500, 100, HumanPlayer())]
    for i in range(1, troop_size):
        t1_units.append(Unit(f"Ally_{i}", 300, 200, 50, AIPlayer()))
    t1 = Troop(t1_units)

    t2_units = []
    for i in range(troop_size):
        t2_units.append(Unit(f"Enemy_{i+1}", 300, 200, 50, AIPlayer()))
    t2 = Troop(t2_units)

    # Initialize Skills using Command Pattern
    all_units = t1.units + t2.units
    for u in all_units:
        u.skills = get_all_actions()

    game = RPG(t1, t2)
    game.start()

class Troop:
    def __init__(self, units):
        self.units = units
        for u in self.units:
            u.troop = self

    def is_annihilated(self):
        return all(u.is_dead for u in self.units)

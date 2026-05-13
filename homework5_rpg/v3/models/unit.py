class Unit:
    def __init__(
        self,
        name: str,
        hp: int,
        mp: int,
        str_: int,
        is_hero: bool = False,
    ) -> None:
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.is_hero = is_hero

        from models.states.normal_state import NormalState

        self.current_state: "State" = NormalState()
        self.strategy: "DecisionStrategy | None" = None
        self.skills: list["Action"] = []
        self.observers: list["DeathObserver"] = []
        self.troop: list["Unit"] = []
        self.enemy_troop: list["Unit"] = []
        self.troop_id = 0

    def attack(self, target: "Unit") -> None:
        self.cause_damage(target, self.str)

    def cause_damage(self, target: "Unit", amount: int) -> None:
        from models.states.cheered_up_state import CheeredUpState

        bonus = 0
        if isinstance(self.current_state, CheeredUpState):
            bonus = self.current_state.bonus
        print(f"[{self.troop_id}]{self.name} 對 [{target.troop_id}]{target.name} 造成 {amount + bonus} 點傷害。")
        target.take_damage(amount + bonus)

    def take_damage(self, amt: int) -> None:
        if self.hp <= 0:
            return
        self.hp -= amt
        if self.hp <= 0:
            self.hp = 0
            print(f"[{self.troop_id}]{self.name} 死亡。")
            self.notify()

    def heal(self, amt: int) -> None:
        if self.hp > 0:
            self.hp += amt

    def change_state(self, new_state: "State") -> None:
        self.current_state = new_state

    def attach(self, obs: "DeathObserver") -> None:
        if obs not in self.observers:
            self.observers.append(obs)

    def notify(self) -> None:
        for obs in self.observers:
            obs.on_unit_death(self)

from models.Individual import Individual
from enums import MatchingType,Gender
from models.MatchmakingSystem import MatchmakingSystem


users=[
    Individual(1, Gender.MALE, 18, '我是直男', ['尬聊', '打手~機', '找飲水機小姐'], (1, 1)),
    Individual(2, Gender.FEMALE, 20, '我是女生', ['追劇', '逛網拍', '逛街','化妝品'], (2, 2)),
    Individual(3, Gender.MALE, 20, '我是牛耳', ['化妝品'], (3, 3)),
]

me = Individual(4, Gender.MALE, 25, '我是社畜', ['追劇', '打手~機', '睡覺'], (5, 5))

print("Distance Matchmaking: reversed = False/True")
system = MatchmakingSystem(matching_type=MatchingType.DISTANCE, me=me, users=users,is_reversed=False)
print("預期 id: 3", system.match_user().id)

system = MatchmakingSystem(matching_type=MatchingType.DISTANCE, me=me, users=users,is_reversed=True)
print("預期 id: 1", system.match_user().id)

print("Habit Matchmaking: reversed = False/True")
system = MatchmakingSystem(matching_type=MatchingType.HABIT, me=me, users=users,is_reversed=False)
print("預期 id: 1", system.match_user().id)
system = MatchmakingSystem(matching_type=MatchingType.HABIT, me=me, users=users,is_reversed=True)
print("預期 id: 3", system.match_user().id)


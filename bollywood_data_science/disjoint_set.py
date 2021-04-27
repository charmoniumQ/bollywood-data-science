from typing import Dict, Generic, Set, TypeVar

T = TypeVar("T")

# https://stackoverflow.com/a/3067672/1078199


class DisjointSet(Generic[T]):
    def __init__(self) -> None:
        self.leader: Dict[T, T] = {}  # maps a member to the group's leader
        self.group: Dict[
            T, Set[T]
        ] = {}  # maps a group leader to the group (which is a set)

    def add(self, a: T, b: T) -> None:
        leadera = self.leader.get(a)
        leaderb = self.leader.get(b)
        if leadera is not None:
            if leaderb is not None:
                if leadera == leaderb:
                    return  # nothing to do
                groupa = self.group[leadera]
                groupb = self.group[leaderb]
                if len(groupa) < len(groupb):
                    a, leadera, groupa, b, leaderb, groupb = (
                        b,
                        leaderb,
                        groupb,
                        a,
                        leadera,
                        groupa,
                    )
                groupa |= groupb
                del self.group[leaderb]
                for k in groupb:
                    self.leader[k] = leadera
            else:
                self.group[leadera].add(b)
                self.leader[b] = leadera
        else:
            if leaderb is not None:
                self.group[leaderb].add(a)
                self.leader[a] = leaderb
            else:
                self.leader[a] = self.leader[b] = a
                self.group[a] = set([a, b])

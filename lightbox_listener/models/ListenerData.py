from dataclasses import dataclass


@dataclass
class ListenerData:
    connections: list[str]
    reward: any

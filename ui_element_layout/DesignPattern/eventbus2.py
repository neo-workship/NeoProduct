from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Callable, Any

# ---------- 事件 ----------
@dataclass
class PingEvent:  sender: str
@dataclass
class PongEvent:  sender: str

# ---------- 总线 ----------
class EventBus:
    def __init__(self) -> None:
        self._listeners: Dict[type, List[Callable[[Any], None]]] = {}

    def register(self, event_type: type, fn: Callable[[Any], None]) -> None:
        self._listeners.setdefault(event_type, []).append(fn)

    def publish(self, event: Any) -> None:
        for fn in self._listeners.get(type(event), []):
            fn(event)

# ---------- 参与者 ----------
class NodeA:
    def __init__(self, bus: EventBus, name: str = "A") -> None:
        self.bus = bus
        self.name = name
        bus.register(PongEvent, self._on_pong)

    def ping(self) -> None:
        print(f"[{self.name}] 发送 Ping")
        self.bus.publish(PingEvent(self.name))

    def _on_pong(self, ev: PongEvent) -> None:
        print(f"[{self.name}] 收到来自 {ev.sender} 的 Pong")

class NodeB:
    def __init__(self, bus: EventBus, name: str = "B") -> None:
        self.bus = bus
        self.name = name
        bus.register(PingEvent, self._on_ping)

    def pong(self) -> None:
        print(f"[{self.name}] 发送 Pong")
        self.bus.publish(PongEvent(self.name))

    def _on_ping(self, ev: PingEvent) -> None:
        print(f"[{self.name}] 收到来自 {ev.sender} 的 Ping → 自动回 Pong")
        self.pong()

# ---------- 运行 ----------
if __name__ == "__main__":
    bus = EventBus()
    a = NodeA(bus)
    b = NodeB(bus)

    a.ping()          # A 发 Ping，B 回 Pong，A 再收 Pong
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Callable, Any

# -------------------------------------------------
# 1. 事件对象：纯数据载体
@dataclass
class OrderCreatedEvent:
    order_id: int
    amount: float

# -------------------------------------------------
# 2. 事件总线：发布-订阅核心
class EventBus:
    def __init__(self) -> None:
        # event_type -> list[callable]
        self._listeners: Dict[type, List[Callable[[Any], None]]] = {}

    def register(self, event_type: type, listener: Callable[[Any], None]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def publish(self, event: Any) -> None:
        for listener in self._listeners.get(type(event), []):
            listener(event)

# -------------------------------------------------
# 3. 发布者：OrderService
class OrderService:
    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def create_order(self, amount: float) -> None:
        order = OrderCreatedEvent(order_id=hash(amount) & 0xFFFF, amount=amount)
        print(f"[OrderService] 订单 {order.order_id} 创建，金额 {amount}")
        self._bus.publish(order)

# -------------------------------------------------
# 4. 订阅者：EmailSender
class EmailSender:
    def __init__(self, bus: EventBus) -> None:
        bus.register(OrderCreatedEvent, self._on_order_created)

    def _on_order_created(self, event: OrderCreatedEvent) -> None:
        print(f"[EmailSender] 给订单 {event.order_id} 发送确认邮件。")

# -------------------------------------------------
# 5. 组装 & 运行
if __name__ == "__main__":
    bus = EventBus()
    order_service = OrderService(bus)
    email_sender = EmailSender(bus)   # 自动完成注册

    # 触发业务
    order_service.create_order(99.9)
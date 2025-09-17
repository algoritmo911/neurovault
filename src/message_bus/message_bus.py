from collections import defaultdict

class MessageBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_type, handler):
        """Подписывает обработчик на определенный тип события."""
        self._handlers[event_type].append(handler)
        print(f"Handler {handler.__name__} subscribed to {event_type}")

    def publish(self, event_type, data=None):
        """Публикует событие, вызывая всех подписанных обработчиков."""
        if event_type in self._handlers:
            print(f"Publishing event {event_type} with data: {data}")
            for handler in self._handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error handling event {event_type} in {handler.__name__}: {e}")
        else:
            print(f"No handlers for event {event_type}")

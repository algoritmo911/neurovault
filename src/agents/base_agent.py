from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Абстрактный базовый класс для всех агентов в системе.
    Определяет общий интерфейс, которому должны следовать все агенты.
    """
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self._running = False

    @abstractmethod
    def start(self):
        """Запускает работу агента."""
        self._running = True
        print(f"Agent {self.__class__.__name__} started.")

    @abstractmethod
    def stop(self):
        """Останавливает работу агента."""
        self._running = False
        print(f"Agent {self.__class__.__name__} stopped.")

    @abstractmethod
    def handle_command(self, command_type, data):
        """Обрабатывает входящую команду из шины сообщений."""
        pass

    @abstractmethod
    def heartbeat(self):
        """Отправляет сигнал о том, что агент активен."""
        pass

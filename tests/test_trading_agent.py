import unittest
from unittest.mock import Mock, call
from src.agents.trading_agent import TradingAgent
from src.message_bus.message_bus import MessageBus

class TestTradingAgent(unittest.TestCase):
    """
    Тесты для TradingAgent.
    """
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Используем настоящий MessageBus, но могли бы и мокать его
        self.bus = MessageBus()
        # Мокаем методы шины, чтобы отслеживать вызовы
        self.bus.subscribe = Mock()
        self.bus.publish = Mock()

        self.agent = TradingAgent(self.bus)

    def test_agent_subscribes_on_start(self):
        """Проверяем, что агент подписывается на команды при старте."""
        self.agent.start()

        # Ожидаем, что агент подписался на два типа команд
        expected_calls = [
            call("TRADE_EXECUTE", self.agent.handle_command),
            call("PRICE_REQUEST", self.agent.handle_command)
        ]
        self.bus.subscribe.assert_has_calls(expected_calls, any_order=True)

        self.agent.stop() # Очистка

    def test_price_request_publishes_report(self):
        """Проверяем, что запрос цены публикует отчет о цене."""
        # Имитируем команду, отправленную в шину
        command = {"type": "PRICE_REQUEST", "data": {"ticker": "BTC-USD"}}
        self.agent.handle_command(command)

        # Проверяем, что агент опубликовал отчет о цене в шину
        self.bus.publish.assert_called_with("PRICE_REPORT", {"ticker": "BTC-USD", "price": "50000.00"})

    def test_trade_execute_publishes_result(self):
        """Проверяем, что команда на сделку публикует результат."""
        command = {"type": "TRADE_EXECUTE", "data": {"ticker": "BTC-USD", "side": "buy", "amount": 0.1}}
        self.agent.handle_command(command)

        # Проверяем, что агент опубликовал результат сделки
        self.bus.publish.assert_called_with("TRADE_RESULT", {
            "status": "filled",
            "id": "mock-order-12345",
            "side": "buy",
            "amount": 0.1
        })

if __name__ == "__main__":
    unittest.main()

import time
import threading
from .base_agent import BaseAgent
from ..clients.coinbase_client import CoinbaseClient

class TradingAgent(BaseAgent):
    """
    Торговый агент Katana для взаимодействия с Coinbase.
    """
    def __init__(self, message_bus):
        super().__init__(message_bus)
        self.coinbase_client = CoinbaseClient()
        self._heartbeat_thread = None

        # Risk Limits (as placeholders)
        self.max_position_usd = 10000.0
        self.max_daily_loss_usd = 500.0
        self.kill_switch_activated = False

    def start(self):
        """Запускает агента, подписывается на события и запускает heartbeat."""
        super().start()
        self._subscribe_to_commands()
        self._start_heartbeat()
        print("TradingAgent started and subscribed to commands.")

    def stop(self):
        """Останавливает агента и heartbeat."""
        super().stop()
        if self._heartbeat_thread:
            self._heartbeat_thread.join() # Wait for the thread to finish
        print("TradingAgent stopped.")

    def _subscribe_to_commands(self):
        """Подписывается на команды из шины сообщений."""
        self.message_bus.subscribe("TRADE_EXECUTE", self.handle_command)
        self.message_bus.subscribe("PRICE_REQUEST", self.handle_command)

    def handle_command(self, command_data):
        """Центральный обработчик команд."""
        command_type = command_data.get("type")
        data = command_data.get("data")

        if self.kill_switch_activated:
            print(f"KILL SWITCH ON: Command {command_type} ignored.")
            return

        if command_type == "TRADE_EXECUTE":
            self._handle_trade_execute(data)
        elif command_type == "PRICE_REQUEST":
            self._handle_price_request(data)
        else:
            print(f"Unknown command type: {command_type}")

    def _handle_trade_execute(self, data):
        """Обработка команды на исполнение сделки."""
        print(f"Handling TRADE_EXECUTE command: {data}")
        # Basic risk check
        if data.get("amount_usd", 0) > self.max_position_usd:
            result = {"status": "rejected", "reason": "Exceeds max position limit"}
            self.message_bus.publish("TRADE_RESULT", result)
            return

        result = self.coinbase_client.execute_order(
            ticker=data.get("ticker"),
            side=data.get("side"),
            amount=data.get("amount")
        )
        self.message_bus.publish("TRADE_RESULT", result)

    def _handle_price_request(self, data):
        """Обработка запроса цены."""
        print(f"Handling PRICE_REQUEST command: {data}")
        price_data = self.coinbase_client.get_price(ticker=data.get("ticker"))
        self.message_bus.publish("PRICE_REPORT", price_data)

    def _start_heartbeat(self):
        """Запускает цикл heartbeat в отдельном потоке."""
        self._heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def heartbeat_loop(self):
        """Петля, вызывающая heartbeat каждые 10 секунд."""
        while self._running:
            self.heartbeat()
            time.sleep(10)

    def heartbeat(self):
        """Отправляет сигнал 'heartbeat' и отчет о балансе."""
        print("HEARTBEAT: TradingAgent is alive.")

        # Publish heartbeat event
        heartbeat_data = {"agent": "TradingAgent", "timestamp": time.time()}
        self.message_bus.publish("AGENT_HEARTBEAT", heartbeat_data)

        # Publish balance report
        balance_data = self.coinbase_client.get_balance()
        self.message_bus.publish("BALANCE_REPORT", balance_data)

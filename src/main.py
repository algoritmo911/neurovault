import time
from .message_bus.message_bus import MessageBus
from .agents.trading_agent import TradingAgent

def main():
    """
    Главная функция для инициализации и запуска системы.
    """
    print("Initializing system...")
    # 1. Создаем шину сообщений
    bus = MessageBus()

    # 2. Создаем и запускаем торгового агента
    trading_agent = TradingAgent(bus)
    trading_agent.start()

    # Даем агенту время на запуск и подписку
    time.sleep(1)

    # 3. Симулируем отправку команд в шину
    print("\n--- Simulating Commands ---")

    # Запрос цены
    price_request_command = {
        "type": "PRICE_REQUEST",
        "data": {"ticker": "BTC-USD"}
    }
    bus.publish("PRICE_REQUEST", price_request_command)
    time.sleep(0.5)

    # Исполнение сделки
    trade_command = {
        "type": "TRADE_EXECUTE",
        "data": {"ticker": "ETH-USD", "side": "buy", "amount": 0.05}
    }
    bus.publish("TRADE_EXECUTE", trade_command)

    print("\nSystem is running. Press Ctrl+C to stop.")
    print("Heartbeat messages will appear every 10 seconds.")

    try:
        # Держим главный поток живым, чтобы фоновые потоки (heartbeat) могли работать
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
    finally:
        # 4. Корректно останавливаем агента
        trading_agent.stop()
        print("System stopped.")

if __name__ == "__main__":
    main()

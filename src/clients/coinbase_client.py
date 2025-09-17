import os
from dotenv import load_dotenv

class CoinbaseClient:
    """
    Клиент для взаимодействия с Coinbase API (Sandbox).
    В этой версии используются мок-данные для разработки.
    """
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("COINBASE_API_KEY")
        self.api_secret = os.getenv("COINBASE_API_SECRET")
        self.api_base_url = "https://api-public.sandbox.pro.coinbase.com"

        if not self.api_key or not self.api_secret:
            print("WARNING: Coinbase API Key/Secret not found in .env file.")
            # В реальном приложении здесь следовало бы выбросить исключение
            # raise ValueError("API keys must be set in .env file")

    def get_price(self, ticker="BTC-USD"):
        """
        Получает цену для указанной торговой пары.
        Возвращает мок-данные.
        """
        print(f"MOCK [CoinbaseClient]: Getting price for {ticker}")
        return {"ticker": ticker, "price": "50000.00"}

    def get_balance(self):
        """
        Получает баланс счета.
        Возвращает мок-данные.
        """
        print("MOCK [CoinbaseClient]: Getting account balance")
        return {"USD": {"balance": "10000.00"}, "BTC": {"balance": "0.5"}}

    def execute_order(self, ticker="BTC-USD", side="buy", amount=0.01):
        """
        Выполняет торговый ордер.
        Имитирует исполнение ордера (paper trading).
        """
        print(f"MOCK [CoinbaseClient]: Executing PAPER {side} order for {amount} {ticker.split('-')[0]}")
        return {"status": "filled", "id": "mock-order-12345", "side": side, "amount": amount}

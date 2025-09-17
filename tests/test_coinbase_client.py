import unittest
from src.clients.coinbase_client import CoinbaseClient

class TestCoinbaseClient(unittest.TestCase):
    """
    Тесты для клиента Coinbase.
    Так как клиент пока использует мок-данные, тесты проверяют
    корректность вызова методов и формат ответов.
    """
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.client = CoinbaseClient()

    def test_get_price(self):
        """Тестирование получения цены."""
        price_data = self.client.get_price("BTC-USD")
        self.assertIsNotNone(price_data)
        self.assertIn("price", price_data)
        self.assertEqual(price_data["ticker"], "BTC-USD")

    def test_get_balance(self):
        """Тестирование получения баланса."""
        balance_data = self.client.get_balance()
        self.assertIsNotNone(balance_data)
        self.assertIn("USD", balance_data)
        self.assertIn("BTC", balance_data)

    def test_execute_order(self):
        """Тестирование исполнения ордера."""
        order_result = self.client.execute_order(side="buy", amount=0.1)
        self.assertIsNotNone(order_result)
        self.assertEqual(order_result["status"], "filled")
        self.assertEqual(order_result["side"], "buy")

if __name__ == "__main__":
    unittest.main()

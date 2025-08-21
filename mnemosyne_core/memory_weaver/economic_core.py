import os
import threading

class Wallet:
    """
    Manages the agent's economic resources.

    This class handles a simple balance, persisting it to a file
    and ensuring thread-safe operations for a multi-threaded server environment.
    """

    def __init__(self, filepath='wallet.dat', initial_balance=1000.0):
        self._filepath = filepath
        self._initial_balance = initial_balance
        self._lock = threading.Lock()
        self._balance = self._load_balance()

    def _load_balance(self) -> float:
        """Loads the balance from the file."""
        with self._lock:
            if not os.path.exists(self._filepath):
                self._save_balance_unsafe(self._initial_balance)
                return self._initial_balance

            try:
                with open(self._filepath, 'r') as f:
                    return float(f.read())
            except (ValueError, IOError):
                # If file is corrupt or unreadable, reset to initial balance
                self._save_balance_unsafe(self._initial_balance)
                return self._initial_balance

    def _save_balance_unsafe(self, balance: float):
        """Saves the balance to the file (unsafe, requires external lock)."""
        with open(self._filepath, 'w') as f:
            f.write(str(balance))

    def get_balance(self) -> float:
        """Returns the current balance in a thread-safe way."""
        with self._lock:
            return self._balance

    def debit(self, amount: float) -> bool:
        """
        Subtracts an amount from the balance.
        Returns True if successful, False if funds are insufficient.
        """
        if amount < 0:
            return False # Cannot debit a negative amount

        with self._lock:
            if self._balance >= amount:
                self._balance -= amount
                self._save_balance_unsafe(self._balance)
                print(f"Wallet: Debited {amount}. New balance: {self._balance}")
                return True
            else:
                print(f"Wallet: Debit failed. Insufficient funds for amount {amount}. Balance: {self._balance}")
                return False

    def credit(self, amount: float):
        """Adds an amount to the balance."""
        if amount < 0:
            return # Cannot credit a negative amount

        with self._lock:
            self._balance += amount
            self._save_balance_unsafe(self._balance)
            print(f"Wallet: Credited {amount}. New balance: {self._balance}")

# Create a single, globally accessible instance of the Wallet.
# This acts as a singleton for the application.
wallet = Wallet()

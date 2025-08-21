from .economic_core import Wallet

class ResourceNotFound(Exception):
    """Custom exception for when a resource is not in the catalog."""
    pass

class ResourceCatalog:
    """
    A catalog of external resources that can be purchased by the agent.
    In a real system, this might be a dynamic registry or an external API.
    """
    _resources = {
        "compute_instance_small": {
            "description": "A small compute instance for 1 hour.",
            "cost": 100.0
        },
        "compute_instance_large": {
            "description": "A large compute instance for 1 hour.",
            "cost": 500.0
        },
        "premium_data_api_access": {
            "description": "1000 calls to a premium data provider API.",
            "cost": 50.0
        }
    }

    @classmethod
    def get_resource(cls, resource_id: str) -> dict | None:
        return cls._resources.get(resource_id)

class EidolonGateway:
    """
    The Eidolon Gateway acts as a bridge for the agent to interact with the
    external world, such as purchasing resources.
    """

    def __init__(self):
        self.catalog = ResourceCatalog()

    def purchase_resource(self, resource_id: str, wallet: Wallet) -> bool:
        """
        Attempts to purchase a resource for the agent.

        Args:
            resource_id: The ID of the resource to purchase.
            wallet: The agent's wallet instance to debit the cost from.

        Returns:
            True if the purchase was successful, False otherwise.

        Raises:
            ResourceNotFound: If the resource_id does not exist in the catalog.
        """
        resource = self.catalog.get_resource(resource_id)
        if not resource:
            raise ResourceNotFound(f"Resource '{resource_id}' not found in catalog.")

        cost = resource['cost']

        # The debit method returns True on success and False on failure (insufficient funds)
        purchase_successful = wallet.debit(cost)

        if purchase_successful:
            print(f"EidolonGateway: Successfully purchased '{resource_id}' for {cost}.")
        else:
            print(f"EidolonGateway: Failed to purchase '{resource_id}'. Insufficient funds.")

        return purchase_successful

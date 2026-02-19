from typing import List, Dict
from dataclasses import dataclass

# ============================================================================
# DATA MODELS 
# ============================================================================
@dataclass
class Product:
    """Represents a physical item in the store."""
    id: str  # Changed to str to match ProductCatalog keys
    name: str
    price: float

@dataclass
class Customer:
    """Represents a user of the system."""
    id: int
    name: str
    email: str
    address: str

@dataclass
class Order:
    """The result of a successful transaction."""
    id: int
    customer: Customer
    products: List[Product]
    total_amount: float   

# ============================================================================
# MODULAR COMPONENTS
# ============================================================================

class InventoryManager:
    """Handles stock levels. Independent of pricing or shipping logic."""
    def __init__(self):
        self.products = {}

    def add_product(self, product: Product, quantity: int):
        self.products[product.id] = {"product": product, "quantity": quantity}
        print(f"Product '{product.name}' added with quantity {quantity}.")

    def check_stock(self, product_id: str) -> int:
        if product_id in self.products:
            return self.products[product_id]["quantity"]
        return 0

class ProductCatalog:
    """The 'Source of Truth' for product information."""
    def __init__(self):
        # Initializing with some dummy data
        self.products = {
            "P1": Product("P1", "Laptop", 1200.0), 
            "P2": Product("P2", "Mouse", 25.0)
        }
    
    def get_product(self, product_id: str) -> Product:
        return self.products.get(product_id)
    
class CartManager:
    """Manages temporary state (items a user intends to buy)."""
    def __init__(self):
        self.carts = {}

    def add_to_cart(self, customer_id: int, product: Product):
        if customer_id not in self.carts:
            self.carts[customer_id] = []
        self.carts[customer_id].append(product)
        print(f"Product '{product.name}' added to cart for customer {customer_id}.")

class ShippingManager:
    """Specialized logic for logistics and distance-based costs."""
    def calculate_cost(self, items_count: int) -> float:
        return 10.0 + (items_count * 2.0)
    
class PaymentProcessor:
    """Handles sensitive financial transactions."""
    def process_payment(self, amount: float) -> bool:
        print(f"Processing payment of ${amount}...")
        return True 
    
class NotificationManager:
    """Communication layer (Email/SMS)."""
    def notify(self, message: str):
        print(f"[NOTIFICATION]: {message}")

# ============================================================================
# ORCHESTRATOR 
# ============================================================================

class ECommerceSystem:
    """
    The Facade: Provides a single, simple interface to a complex system.
    
    It 'orchestrates' the modules. The user just calls 'place_order', 
    and this class coordinates the inventory, payment, and shipping.
    """
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.product_catalog = ProductCatalog()
        self.cart_manager = CartManager()
        self.shipping_manager = ShippingManager()
        self.notification_manager = NotificationManager()
        self.payment_processor = PaymentProcessor()

    def place_order(self, customer: Customer, product_ids: List[str]):
        """
        Coordinates a multi-step workflow across different components.
        """
        products = []
        total_amount = 0.0

        print(f"\n--- Processing Order for {customer.name} ---")

        for pid in product_ids:
            product = self.product_catalog.get_product(pid)
            
            # Coordination: Checking stock before committing to the order
            if product and self.inventory_manager.check_stock(product.id) > 0:
                products.append(product)
                total_amount += product.price
                # Update inventory (Reducing quantity)
                self.inventory_manager.add_product(product, self.inventory_manager.check_stock(product.id) - 1)
            else:
                print(f"Product with ID '{pid}' is out of stock or does not exist.")

        if not products:
            print("Order failed: No valid items found.")
            return

        # Calculate shipping via ShippingManager
        shipping_fee = self.shipping_manager.calculate_cost(len(products))
        grand_total = total_amount + shipping_fee

        # Process payment via PaymentProcessor
        if self.payment_processor.process_payment(grand_total):
            self.notification_manager.notify(f"Order successful! Total: ${grand_total}")
        else:
            self.notification_manager.notify("Order failed during payment.")
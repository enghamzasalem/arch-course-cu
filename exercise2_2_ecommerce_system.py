#!/usr/bin/env python3
"""
Exercise 2.2: Design a Modular E-commerce System 🟡

This example demonstrates:
- Designing a complex system from scratch using modularity principles
- Identifying distinct business domains and bounded contexts
- Defining clean interfaces between independent components
- Creating testable, swappable modules with dependency injection
- Orchestrating components into a cohesive system

Business Scenario: E-commerce Platform
- 7+ independent components with single responsibilities
- Clear contracts between components
- Support for multiple implementations
- Independent development and testing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import uuid
import json
import random
from decimal import Decimal, ROUND_HALF_UP


# ============================================================================
# PART 1: CORE DOMAIN MODELS (Shared across components)
# ============================================================================
# These are the "nouns" of our system - the data structures that flow
# between components. They define the language of our domain.

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"

class ShippingMethod(Enum):
    STANDARD = "standard"      # 5-7 days
    EXPRESS = "express"        # 2-3 days
    OVERNIGHT = "overnight"    # 1 day
    ECONOMY = "economy"        # 7-10 days

@dataclass
class Money:
    """Value object for monetary amounts"""
    amount: Decimal
    currency: Currency = Currency.USD
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, multiplier: float) -> 'Money':
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency.value} {self.amount:.2f}"
    
    @classmethod
    def zero(cls, currency: Currency = Currency.USD):
        return cls(Decimal('0'), currency)

@dataclass
class Address:
    """Value object for shipping/billing addresses"""
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_residential: bool = True
    
    def full_address(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"

@dataclass
class Customer:
    """Customer entity"""
    customer_id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    default_shipping_address: Optional[Address] = None
    default_billing_address: Optional[Address] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

@dataclass
class Product:
    """Product entity"""
    product_id: str
    sku: str
    name: str
    description: str
    price: Money
    category: str
    weight_kg: float
    dimensions_cm: Tuple[float, float, float] = (0, 0, 0)
    is_active: bool = True
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class InventoryItem:
    """Inventory item entity"""
    product_id: str
    quantity_available: int
    quantity_reserved: int = 0
    reorder_threshold: int = 10
    reorder_quantity: int = 50
    location: str = "Warehouse A"
    last_restocked: datetime = field(default_factory=datetime.now)
    
    @property
    def quantity_on_hand(self) -> int:
        return self.quantity_available + self.quantity_reserved
    
    @property
    def is_low_stock(self) -> bool:
        return self.quantity_available <= self.reorder_threshold

@dataclass
class CartItem:
    """Shopping cart item"""
    product: Product
    quantity: int
    added_at: datetime = field(default_factory=datetime.now)
    
    @property
    def subtotal(self) -> Money:
        return self.product.price * self.quantity

@dataclass
class Cart:
    """Shopping cart aggregate"""
    cart_id: str
    customer_id: Optional[str] = None
    items: Dict[str, CartItem] = field(default_factory=dict)  # product_id -> CartItem
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.values())
    
    @property
    def subtotal(self) -> Money:
        if not self.items:
            return Money.zero()
        # Assume all items same currency for simplicity
        currency = next(iter(self.items.values())).product.price.currency
        total = Decimal('0')
        for item in self.items.values():
            total += item.subtotal.amount
        return Money(total, currency)
    
    def add_item(self, product: Product, quantity: int = 1):
        if product.product_id in self.items:
            self.items[product.product_id].quantity += quantity
        else:
            self.items[product.product_id] = CartItem(product, quantity)
        self.updated_at = datetime.now()
    
    def remove_item(self, product_id: str):
        if product_id in self.items:
            del self.items[product_id]
            self.updated_at = datetime.now()
    
    def update_quantity(self, product_id: str, quantity: int):
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self.items[product_id].quantity = quantity
                self.updated_at = datetime.now()
    
    def clear(self):
        self.items.clear()
        self.updated_at = datetime.now()

@dataclass
class Order:
    """Order aggregate"""
    order_id: str
    customer_id: str
    items: Dict[str, CartItem]  # Snapshot of cart items at order time
    subtotal: Money
    shipping_cost: Money
    tax_amount: Money
    total_amount: Money
    shipping_address: Address
    billing_address: Address
    shipping_method: ShippingMethod
    status: OrderStatus = OrderStatus.PENDING
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.values())

@dataclass
class Payment:
    """Payment entity"""
    payment_id: str
    order_id: str
    customer_id: str
    amount: Money
    method: str  # credit_card, paypal, etc.
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Shipment:
    """Shipment entity"""
    shipment_id: str
    order_id: str
    carrier: str
    tracking_number: str
    shipping_method: ShippingMethod
    shipping_cost: Money
    estimated_delivery: datetime
    actual_delivery: Optional[datetime] = None
    status: str = "pending"  # pending, picked_up, in_transit, delivered
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Notification:
    """Notification entity"""
    notification_id: str
    customer_id: str
    type: str  # order_confirmation, shipping_confirmation, payment_receipt, etc.
    channel: str  # email, sms, push
    subject: str
    content: str
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed


# ============================================================================
# PART 2: COMPONENT INTERFACES (Contracts between components)
# ============================================================================
# These ABCs define the contracts between components. Each component
# implements its interface, and components depend on interfaces, not
# concrete implementations.

class CatalogService(ABC):
    """Interface for product catalog operations"""
    
    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        pass
    
    @abstractmethod
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        pass
    
    @abstractmethod
    def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        """Search products by name, description, or tags"""
        pass
    
    @abstractmethod
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products in a category"""
        pass
    
    @abstractmethod
    def get_product_price(self, product_id: str) -> Optional[Money]:
        """Get current price for product"""
        pass
    
    @abstractmethod
    def create_product(self, product: Product) -> Product:
        """Create a new product"""
        pass
    
    @abstractmethod
    def update_product(self, product_id: str, **kwargs) -> Optional[Product]:
        """Update product information"""
        pass
    
    @abstractmethod
    def deactivate_product(self, product_id: str) -> bool:
        """Deactivate a product (soft delete)"""
        pass


class InventoryService(ABC):
    """Interface for inventory management operations"""
    
    @abstractmethod
    def get_inventory(self, product_id: str) -> Optional[InventoryItem]:
        """Get inventory for a product"""
        pass
    
    @abstractmethod
    def check_availability(self, product_id: str, quantity: int) -> bool:
        """Check if product is available in requested quantity"""
        pass
    
    @abstractmethod
    def reserve_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Reserve inventory for an order"""
        pass
    
    @abstractmethod
    def release_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Release reserved inventory (cancelled order)"""
        pass
    
    @abstractmethod
    def confirm_inventory_use(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Confirm inventory use (shipped order)"""
        pass
    
    @abstractmethod
    def restock_inventory(self, product_id: str, quantity: int) -> bool:
        """Add inventory to stock"""
        pass
    
    @abstractmethod
    def get_low_stock_products(self) -> List[InventoryItem]:
        """Get products below reorder threshold"""
        pass


class CartService(ABC):
    """Interface for shopping cart operations"""
    
    @abstractmethod
    def create_cart(self, customer_id: Optional[str] = None) -> Cart:
        """Create a new shopping cart"""
        pass
    
    @abstractmethod
    def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID"""
        pass
    
    @abstractmethod
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1) -> Optional[Cart]:
        """Add item to cart"""
        pass
    
    @abstractmethod
    def remove_from_cart(self, cart_id: str, product_id: str) -> Optional[Cart]:
        """Remove item from cart"""
        pass
    
    @abstractmethod
    def update_cart_item(self, cart_id: str, product_id: str, quantity: int) -> Optional[Cart]:
        """Update item quantity in cart"""
        pass
    
    @abstractmethod
    def clear_cart(self, cart_id: str) -> bool:
        """Remove all items from cart"""
        pass
    
    @abstractmethod
    def get_cart_subtotal(self, cart_id: str) -> Optional[Money]:
        """Calculate cart subtotal"""
        pass
    
    @abstractmethod
    def delete_cart(self, cart_id: str) -> bool:
        """Delete abandoned cart"""
        pass


class PricingService(ABC):
    """Interface for pricing and tax calculations"""
    
    @abstractmethod
    def calculate_tax(self, amount: Money, address: Address) -> Money:
        """Calculate tax for given amount and shipping address"""
        pass
    
    @abstractmethod
    def apply_discount(self, amount: Money, discount_code: str) -> Money:
        """Apply discount code to amount"""
        pass
    
    @abstractmethod
    def calculate_order_total(self, subtotal: Money, shipping_cost: Money, 
                             tax: Money, discount: Optional[Money] = None) -> Money:
        """Calculate final order total"""
        pass
    
    @abstractmethod
    def get_currency_conversion(self, amount: Money, target_currency: Currency) -> Money:
        """Convert amount to different currency"""
        pass


class ShippingService(ABC):
    """Interface for shipping calculations and label generation"""
    
    @abstractmethod
    def calculate_shipping_cost(self, items: List[CartItem], address: Address, 
                               method: ShippingMethod) -> Money:
        """Calculate shipping cost based on weight, dimensions, and destination"""
        pass
    
    @abstractmethod
    def get_estimated_delivery_date(self, method: ShippingMethod, address: Address) -> datetime:
        """Calculate estimated delivery date"""
        pass
    
    @abstractmethod
    def create_shipment(self, order: Order) -> Shipment:
        """Create shipment and generate tracking number"""
        pass
    
    @abstractmethod
    def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        """Get tracking information"""
        pass
    
    @abstractmethod
    def get_shipping_methods(self, address: Address) -> List[Dict[str, Any]]:
        """Get available shipping methods with costs"""
        pass


class PaymentService(ABC):
    """Interface for payment processing operations"""
    
    @abstractmethod
    def process_payment(self, order: Order, payment_method: str, 
                       payment_details: Dict[str, Any]) -> Payment:
        """Process payment for an order"""
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: str, amount: Optional[Money] = None) -> Payment:
        """Refund a payment (full or partial)"""
        pass
    
    @abstractmethod
    def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get status of a payment"""
        pass
    
    @abstractmethod
    def authorize_payment(self, order: Order, payment_method: str,
                         payment_details: Dict[str, Any]) -> Payment:
        """Authorize but don't capture payment"""
        pass
    
    @abstractmethod
    def capture_payment(self, payment_id: str) -> Payment:
        """Capture previously authorized payment"""
        pass
    
    @abstractmethod
    def void_payment(self, payment_id: str) -> Payment:
        """Void an authorized payment"""
        pass


class OrderService(ABC):
    """Interface for order processing operations"""
    
    @abstractmethod
    def create_order_from_cart(self, cart: Cart, customer_id: str,
                              shipping_address: Address, billing_address: Address,
                              shipping_method: ShippingMethod) -> Order:
        """Create order from shopping cart"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        pass
    
    @abstractmethod
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer"""
        pass
    
    @abstractmethod
    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def process_refund(self, order_id: str, amount: Optional[Money] = None) -> bool:
        """Process refund for an order"""
        pass


class NotificationService(ABC):
    """Interface for customer notification operations"""
    
    @abstractmethod
    def send_order_confirmation(self, order: Order) -> Notification:
        """Send order confirmation email"""
        pass
    
    @abstractmethod
    def send_shipping_confirmation(self, order: Order, shipment: Shipment) -> Notification:
        """Send shipping confirmation with tracking"""
        pass
    
    @abstractmethod
    def send_payment_receipt(self, payment: Payment) -> Notification:
        """Send payment receipt"""
        pass
    
    @abstractmethod
    def send_order_cancellation(self, order: Order) -> Notification:
        """Send order cancellation notification"""
        pass
    
    @abstractmethod
    def send_delivery_confirmation(self, order: Order, shipment: Shipment) -> Notification:
        """Send delivery confirmation"""
        pass
    
    @abstractmethod
    def send_welcome_email(self, customer: Customer) -> Notification:
        """Send welcome email to new customer"""
        pass
    
    @abstractmethod
    def send_abandoned_cart_reminder(self, cart: Cart) -> Notification:
        """Send reminder for abandoned cart"""
        pass


# ============================================================================
# PART 3: COMPONENT IMPLEMENTATIONS
# ============================================================================

# ----------------------------------------------------------------------------
# COMPONENT 1: Catalog Service Implementation
# ----------------------------------------------------------------------------

class SimpleCatalogService(CatalogService):
    """Product catalog management"""
    
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._sku_index: Dict[str, str] = {}  # sku -> product_id
        self._category_index: Dict[str, Set[str]] = {}  # category -> product_ids
        print("  [CatalogService] Initialized")
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        product_id = self._sku_index.get(sku)
        return self.get_product(product_id) if product_id else None
    
    def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        query = query.lower()
        results = []
        
        for product in self._products.values():
            if not product.is_active:
                continue
            if category and product.category != category:
                continue
                
            if (query in product.name.lower() or 
                query in product.description.lower() or
                any(query in tag.lower() for tag in product.tags)):
                results.append(product)
        
        return results
    
    def get_products_by_category(self, category: str) -> List[Product]:
        product_ids = self._category_index.get(category, set())
        return [self._products[pid] for pid in product_ids if self._products[pid].is_active]
    
    def get_product_price(self, product_id: str) -> Optional[Money]:
        product = self.get_product(product_id)
        return product.price if product else None
    
    def create_product(self, product: Product) -> Product:
        self._products[product.product_id] = product
        self._sku_index[product.sku] = product.product_id
        
        if product.category not in self._category_index:
            self._category_index[product.category] = set()
        self._category_index[product.category].add(product.product_id)
        
        print(f"  [CatalogService] Created product: {product.name} ({product.sku})")
        return product
    
    def update_product(self, product_id: str, **kwargs) -> Optional[Product]:
        product = self.get_product(product_id)
        if not product:
            return None
        
        # Handle category change (update index)
        if 'category' in kwargs and kwargs['category'] != product.category:
            # Remove from old category
            if product.category in self._category_index:
                self._category_index[product.category].discard(product_id)
            
            # Add to new category
            new_category = kwargs['category']
            if new_category not in self._category_index:
                self._category_index[new_category] = set()
            self._category_index[new_category].add(product_id)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        print(f"  [CatalogService] Updated product: {product.name}")
        return product
    
    def deactivate_product(self, product_id: str) -> bool:
        product = self.get_product(product_id)
        if product:
            product.is_active = False
            print(f"  [CatalogService] Deactivated product: {product.name}")
            return True
        return False
    
    def generate_product_id(self) -> str:
        return f"P{str(uuid.uuid4())[:8].upper()}"


# ----------------------------------------------------------------------------
# COMPONENT 2: Inventory Service Implementation
# ----------------------------------------------------------------------------

class SimpleInventoryService(InventoryService):
    """Inventory management"""
    
    def __init__(self, catalog_service: CatalogService):
        self.catalog_service = catalog_service
        self._inventory: Dict[str, InventoryItem] = {}  # product_id -> InventoryItem
        self._reservations: Dict[str, Dict[str, int]] = {}  # order_id -> {product_id: quantity}
        print("  [InventoryService] Initialized")
    
    def get_inventory(self, product_id: str) -> Optional[InventoryItem]:
        return self._inventory.get(product_id)
    
    def check_availability(self, product_id: str, quantity: int) -> bool:
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False
        return inventory.quantity_available >= quantity
    
    def reserve_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        inventory = self.get_inventory(product_id)
        if not inventory or inventory.quantity_available < quantity:
            return False
        
        # Reserve inventory
        inventory.quantity_available -= quantity
        inventory.quantity_reserved += quantity
        
        # Track reservation by order
        if order_id not in self._reservations:
            self._reservations[order_id] = {}
        self._reservations[order_id][product_id] = quantity
        
        print(f"  [InventoryService] Reserved {quantity} of {product_id} for order {order_id}")
        return True
    
    def release_inventory(self, product_id: str, quantity: int, order_id: str) -> bool:
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False
        
        # Release reserved inventory
        inventory.quantity_available += quantity
        inventory.quantity_reserved -= quantity
        
        # Update reservation tracking
        if order_id in self._reservations:
            if product_id in self._reservations[order_id]:
                del self._reservations[order_id][product_id]
        
        print(f"  [InventoryService] Released {quantity} of {product_id} from order {order_id}")
        return True
    
    def confirm_inventory_use(self, product_id: str, quantity: int, order_id: str) -> bool:
        inventory = self.get_inventory(product_id)
        if not inventory:
            return False
        
        # Move from reserved to used (permanent)
        inventory.quantity_reserved -= quantity
        # quantity_available already decreased, don't decrease again
        
        print(f"  [InventoryService] Confirmed use of {quantity} of {product_id} for order {order_id}")
        return True
    
    def restock_inventory(self, product_id: str, quantity: int) -> bool:
        inventory = self.get_inventory(product_id)
        if not inventory:
            # Create inventory if it doesn't exist
            inventory = InventoryItem(
                product_id=product_id,
                quantity_available=quantity,
                last_restocked=datetime.now()
            )
            self._inventory[product_id] = inventory
        else:
            inventory.quantity_available += quantity
            inventory.last_restocked = datetime.now()
        
        print(f"  [InventoryService] Restocked {quantity} of {product_id}")
        return True
    
    def get_low_stock_products(self) -> List[InventoryItem]:
        return [item for item in self._inventory.values() if item.is_low_stock]


# ----------------------------------------------------------------------------
# COMPONENT 3: Cart Service Implementation
# ----------------------------------------------------------------------------

class SimpleCartService(CartService):
    """Shopping cart management"""
    
    def __init__(self, catalog_service: CatalogService):
        self.catalog_service = catalog_service
        self._carts: Dict[str, Cart] = {}
        self._customer_carts: Dict[str, str] = {}  # customer_id -> cart_id
        print("  [CartService] Initialized")
    
    def create_cart(self, customer_id: Optional[str] = None) -> Cart:
        cart_id = f"C{str(uuid.uuid4())[:8].upper()}"
        cart = Cart(cart_id=cart_id, customer_id=customer_id)
        self._carts[cart_id] = cart
        
        if customer_id:
            self._customer_carts[customer_id] = cart_id
        
        print(f"  [CartService] Created cart {cart_id} for customer {customer_id}")
        return cart
    
    def get_cart(self, cart_id: str) -> Optional[Cart]:
        return self._carts.get(cart_id)
    
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1) -> Optional[Cart]:
        cart = self.get_cart(cart_id)
        if not cart:
            return None
        
        product = self.catalog_service.get_product(product_id)
        if not product or not product.is_active:
            print(f"  [CartService] Product {product_id} not found or inactive")
            return None
        
        cart.add_item(product, quantity)
        print(f"  [CartService] Added {quantity} x {product.name} to cart {cart_id}")
        
        return cart
    
    def remove_from_cart(self, cart_id: str, product_id: str) -> Optional[Cart]:
        cart = self.get_cart(cart_id)
        if not cart:
            return None
        
        cart.remove_item(product_id)
        print(f"  [CartService] Removed product {product_id} from cart {cart_id}")
        
        return cart
    
    def update_cart_item(self, cart_id: str, product_id: str, quantity: int) -> Optional[Cart]:
        cart = self.get_cart(cart_id)
        if not cart:
            return None
        
        cart.update_quantity(product_id, quantity)
        print(f"  [CartService] Updated {product_id} quantity to {quantity} in cart {cart_id}")
        
        return cart
    
    def clear_cart(self, cart_id: str) -> bool:
        cart = self.get_cart(cart_id)
        if not cart:
            return False
        
        cart.clear()
        print(f"  [CartService] Cleared cart {cart_id}")
        return True
    
    def get_cart_subtotal(self, cart_id: str) -> Optional[Money]:
        cart = self.get_cart(cart_id)
        if not cart:
            return None
        return cart.subtotal
    
    def delete_cart(self, cart_id: str) -> bool:
        cart = self.get_cart(cart_id)
        if not cart:
            return False
        
        if cart.customer_id:
            del self._customer_carts[cart.customer_id]
        del self._carts[cart_id]
        
        print(f"  [CartService] Deleted cart {cart_id}")
        return True
    
    def get_customer_cart(self, customer_id: str) -> Optional[Cart]:
        cart_id = self._customer_carts.get(customer_id)
        return self.get_cart(cart_id) if cart_id else None


# ----------------------------------------------------------------------------
# COMPONENT 4: Pricing Service Implementation
# ----------------------------------------------------------------------------

class SimplePricingService(PricingService):
    """Pricing and tax calculations"""
    
    def __init__(self):
        self._tax_rates = {
            'US': {
                'CA': 0.0825,
                'NY': 0.08875,
                'TX': 0.0625,
                'FL': 0.07,
                'WA': 0.065,
                'default': 0.07
            },
            'CA': 0.12,  # Canada
            'UK': 0.20,  # UK VAT
            'DE': 0.19,  # Germany
            'JP': 0.10,  # Japan
            'default': 0.10
        }
        
        self._discounts = {
            'SAVE10': 0.10,
            'SAVE20': 0.20,
            'WELCOME15': 0.15,
            'FLASH25': 0.25
        }
        
        self._exchange_rates = {
            Currency.USD: 1.0,
            Currency.EUR: 0.92,
            Currency.GBP: 0.79,
            Currency.JPY: 150.23
        }
        
        print("  [PricingService] Initialized")
    
    def calculate_tax(self, amount: Money, address: Address) -> Money:
        # Get tax rate based on location
        country = address.country.upper()
        rate = self._tax_rates.get(country, self._tax_rates['default'])
        
        if country == 'US':
            state = address.state.upper()
            rate = self._tax_rates['US'].get(state, self._tax_rates['US']['default'])
        
        tax_amount = amount.amount * Decimal(str(rate))
        return Money(tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), amount.currency)
    
    def apply_discount(self, amount: Money, discount_code: str) -> Money:
        if discount_code not in self._discounts:
            return amount
        
        discount_rate = self._discounts[discount_code]
        discount_amount = amount.amount * Decimal(str(discount_rate))
        discounted = amount.amount - discount_amount
        
        return Money(discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), amount.currency)
    
    def calculate_order_total(self, subtotal: Money, shipping_cost: Money, 
                             tax: Money, discount: Optional[Money] = None) -> Money:
        total = subtotal.amount + shipping_cost.amount + tax.amount
        if discount:
            total -= discount.amount
        return Money(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), subtotal.currency)
    
    def get_currency_conversion(self, amount: Money, target_currency: Currency) -> Money:
        if amount.currency == target_currency:
            return amount
        
        # Convert to USD first (base), then to target
        if amount.currency != Currency.USD:
            usd_amount = amount.amount / Decimal(str(self._exchange_rates[amount.currency]))
        else:
            usd_amount = amount.amount
        
        target_amount = usd_amount * Decimal(str(self._exchange_rates[target_currency]))
        return Money(target_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), target_currency)


# ----------------------------------------------------------------------------
# COMPONENT 5: Shipping Service Implementation
# ----------------------------------------------------------------------------

class SimpleShippingService(ShippingService):
    """Shipping calculation and management"""
    
    def __init__(self):
        self._base_rates = {
            ShippingMethod.ECONOMY: 5.99,
            ShippingMethod.STANDARD: 7.99,
            ShippingMethod.EXPRESS: 14.99,
            ShippingMethod.OVERNIGHT: 24.99
        }
        
        self._weight_rate = 0.50  # per kg
        self._distance_rate = 0.10  # per km
        self._shipments: Dict[str, Shipment] = {}
        
        print("  [ShippingService] Initialized")
    
    def calculate_shipping_cost(self, items: List[CartItem], address: Address, 
                               method: ShippingMethod) -> Money:
        # Calculate total weight
        total_weight = sum(item.product.weight_kg * item.quantity for item in items)
        
        # Base rate for shipping method
        base_rate = self._base_rates.get(method, 7.99)
        
        # Weight surcharge
        weight_surcharge = total_weight * self._weight_rate
        
        # Distance surcharge (simplified - based on country)
        distance_factor = 1.0
        if address.country != 'US':
            distance_factor = 2.5  # International
        
        total = Decimal(str(base_rate + weight_surcharge)) * Decimal(str(distance_factor))
        
        return Money(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def get_estimated_delivery_date(self, method: ShippingMethod, address: Address) -> datetime:
        now = datetime.now()
        
        # Base delivery days
        days = {
            ShippingMethod.ECONOMY: 10,
            ShippingMethod.STANDARD: 7,
            ShippingMethod.EXPRESS: 3,
            ShippingMethod.OVERNIGHT: 1
        }.get(method, 7)
        
        # International takes longer
        if address.country != 'US':
            days += 5
        
        return now + timedelta(days=days)
    
    def create_shipment(self, order: Order) -> Shipment:
        shipment_id = f"S{str(uuid.uuid4())[:8].upper()}"
        
        # Generate tracking number
        carriers = ['UPS', 'FedEx', 'USPS', 'DHL']
        carrier = random.choice(carriers)
        tracking_number = f"{carrier[:2]}{random.randint(1000000000, 9999999999)}"
        
        shipment = Shipment(
            shipment_id=shipment_id,
            order_id=order.order_id,
            carrier=carrier,
            tracking_number=tracking_number,
            shipping_method=order.shipping_method,
            shipping_cost=order.shipping_cost,
            estimated_delivery=self.get_estimated_delivery_date(
                order.shipping_method, order.shipping_address
            ),
            status='pending'
        )
        
        self._shipments[shipment_id] = shipment
        print(f"  [ShippingService] Created shipment {shipment_id} for order {order.order_id}")
        print(f"  [ShippingService] Carrier: {carrier}, Tracking: {tracking_number}")
        
        return shipment
    
    def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        # Find shipment by tracking number
        for shipment in self._shipments.values():
            if shipment.tracking_number == tracking_number:
                return {
                    'tracking_number': tracking_number,
                    'carrier': shipment.carrier,
                    'status': shipment.status,
                    'estimated_delivery': shipment.estimated_delivery.isoformat(),
                    'actual_delivery': shipment.actual_delivery.isoformat() if shipment.actual_delivery else None
                }
        
        return {'error': 'Shipment not found'}
    
    def get_shipping_methods(self, address: Address) -> List[Dict[str, Any]]:
        methods = []
        for method in ShippingMethod:
            # Example weights for calculation
            dummy_items = []
            cost = self.calculate_shipping_cost(dummy_items, address, method)
            delivery_date = self.get_estimated_delivery_date(method, address)
            days = (delivery_date - datetime.now()).days
            
            methods.append({
                'method': method.value,
                'cost': f"{cost}",
                'estimated_days': days,
                'estimated_delivery': delivery_date.strftime('%Y-%m-%d')
            })
        
        return methods


# ----------------------------------------------------------------------------
# COMPONENT 6: Payment Service Implementation
# ----------------------------------------------------------------------------

class SimplePaymentService(PaymentService):
    """Payment processing"""
    
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
        self._order_payments: Dict[str, str] = {}  # order_id -> payment_id
        self._mock_gateway = MockPaymentGateway()
        print("  [PaymentService] Initialized")
    
    def process_payment(self, order: Order, payment_method: str,
                       payment_details: Dict[str, Any]) -> Payment:
        # Create payment record
        payment_id = f"PY{str(uuid.uuid4())[:8].upper()}"
        payment = Payment(
            payment_id=payment_id,
            order_id=order.order_id,
            customer_id=order.customer_id,
            amount=order.total_amount,
            method=payment_method,
            status=PaymentStatus.PENDING
        )
        
        # Process through payment gateway
        gateway_result = self._mock_gateway.charge(
            amount=order.total_amount,
            method=payment_method,
            details=payment_details
        )
        
        if gateway_result['success']:
            payment.status = PaymentStatus.CAPTURED
            payment.transaction_id = gateway_result['transaction_id']
            print(f"  [PaymentService] ✅ Payment processed: {payment_id}, TXN: {payment.transtion_id}")
        else:
            payment.status = PaymentStatus.FAILED
            payment.error_message = gateway_result['error']
            print(f"  [PaymentService] ❌ Payment failed: {gateway_result['error']}")
        
        self._payments[payment_id] = payment
        self._order_payments[order.order_id] = payment_id
        
        return payment
    
    def refund_payment(self, payment_id: str, amount: Optional[Money] = None) -> Payment:
        payment = self._payments.get(payment_id)
      if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        refund_amount = amount or payment.amount
        
        # Process refund through gateway
        gateway_result = self._mock_gateway.refund(
            transaction_id=payment.transaction_id,
            amount=refund_amount
        )
        
        if gateway_result['success']:
            payment.status = PaymentStatus.REFUNDED
            print(f"  [PaymentService] ✅ Refund processed: {payment_id}, ount: {refund_amount}")
        else:
            print(f"  [PaymentService] ❌ Refund failed: {gateway_result['error']}")
        
        return payment
    
    def get_payment_status(self, payment_id: str) -> PaymentStatus:
        payment = self._payments.get(payment_id)
        return payment.status if payment else PaymentStatus.PENDING
    
    def authorize_payment(self, order: Order, payment_method: str,
                         payment_details: Dict[str, Any]) -> Payment:
        payment_id = f"Pstr(uuid.uuid4())[:8].upper()}"
        payment = Payment(
            payment_id=payment_id,
            order_id=order.order_id,
            customer_id=order.customer_id,
            amount=order.total_amount,
            method=payment_method,
            status=PaymentStatus.PENDING
        )
        
        # Authorize through gateway
        gateway_result = self._mock_gateway.authorize(
            amount=order.total_amount,
            method=payment_method,
            details=payment_details
        )
        
        if gateway_result['success']:
            payment.status = PaymentStatus.AUTHORIZED
            payment.transaction_id = gateway_result['transaction_id']
            print(f"  [PaymentService] ✅ Payment authorized: {payment_id}")
        else:
            payment.status = PaymentStatus.FAILED
            payment.error_message = gateway_result['error']
        
        self._payments[payment_id] = payment
        self._order_payments[order.order_id] = payment_id
        
        retn payment
    
    def capture_payment(self, payment_id: str) -> Payment:
        payment = self._payments.get(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != PaymentStatus.AUTHORIZED:
            raise ValueError(f"Payment {payment_id} is not authorized")
        
        # Capture through gateway
        gateway_result = self._mock_gateway.capture(
            transaction_id=payment.transaction_id
        )
        
        if gateway_result['success']:
            payment.status = PaymentStatus.CAPTURED
            print(f"  [PaymentService] ✅ Payment captured: {payment_id}")
        
        return payment
    
    def void_payment(self, payment_id: str) -> Payment:
        payment = self._payments.get(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != PaymentStatus.AUTHORIZED:
            raise ValueError(f"Payment {payment_id}  not authorized")
        
        # Void through gateway
        gateway_result = self._mock_gateway.void(
            transaction_id=payment.transaction_id
        )
        
        if gateway_result['success']:
            payment.status = PaymentStatus.PENDING  # Reset
            print(f"  [PaymentService] ✅ Payment voided: {payment_id}")
        
        return payment


class MockPaymentGateway:
    """Mock external payment gateway for testing"""
    
    def charge(self, amount: Money, method: st details: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate successful payment 90% of time
        if random.random() < 0.9:
            return {
                'success': True,
                'transaction_id': f"TXN{random.randint(10000000, 99999999)}",
                'amount': str(amount)
            }
        else:
            return {
                'success': False,
                'error': 'Card declined',
                'amount': str(amount)
            }
    
    def authorize(self, amount: Money, method: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return self.charge(amount, method, details)
    
    def capture(self, transaction_id: str) -> Dict[str, Any]:
        return {'success': True, 'transaction_id': transaction_id}
    
    def refund(self, transaction_id: str, amount: Money) -> Dict[str, Any]:
        return {'success': True, 'transaction_id': transaction_id}
    
    def void(self, transaction_id: str) -> Dict[str, Any]:
        return {'success': True, 'transaction_id': transaction_id}


# ----------------------------------------------------------------------------
# COMPONENT 7: Order Service Implementation
# ----------------------------------------------------------------------------

class SimpleOrderService(OrderService):
    """Order processing and management"""
    
    def __init__(self, inventory_service: InventoryService, 
                 pricing_service: PricingService,
                 shipping_service: ShippingService,
                 payment_service: PaymentService,
                 notification_service: 'NotificationService'):
        self.inventory_service = inventory_service
        self.pricing_service = pricing_service
        self.shipping_service = shipping_service
        self.payment_service = payment_service
        self.notification_service = notification_service
        self._orders: Dict[str, Order] = {}
        self._customer_orders: Dict[str, List[str]] = {}  # customer_id -> order_ids
        print("  [OrderService] Initialized")
    
    def create_order_from_cart(self, cart: Cart, customer_id: str,
                              shipping_address: Address, billing_address: Address,
                              shipping_method: ShippingMethod) -> Order:
        # Check inventory availability
        for item in cart.items.values():
            if not self.inventory_service.check_availability(item.product.product_id, item.quantity):
                raise ValueError(f"Product {item.product.name} not available in requested quantity")
        
        # Calculate shipping cost
        shipping_cost = self.shipping_service.calculate_shipping_cost(
            list(cart.items.values()), shipping_address, shipping_method
        )
        
        # Calculate tax
        tax = self.pricing_service.calculate_tax(cart.subtotal, shipping_address)
        
        # Calculate total
        total = self.pricing_service.calculate_order_total(
            cart.subtotal, shipping_cost, tax
        )
        
        # Create order
        order_id = f"O{str(uuid.uuid4())[:8].upper()}"
        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            items=cart.items.copy(),
            subtotal=cart.subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax,
            total_amount=total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            shipping_method=shipping_method
        )
        
        # Reserve inventory
        for item in cart.items.values():
            self.inventory_service.reserve_inventory(
                item.product.product_id, item.quantity, order_id
            )
        
        # Store order
        self._orders[order_id] = order
        if customer_id not in self._customer_orders:
            self._customer_orders[customer_id] = []
        self._customer_orders[customer_id].append(order_id)
        
        print(f"  [OrderService] Created order {order_id} for customer {customer_id}")
        print(f"  [OrderService] Total: {total}")
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        order_ids = self._customer_orders.get(customer_id, [])
        return [self._orders[oid] for oid in order_ids if oid in self._orders]
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        order = self.get_order(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.now()
            print(f"  [OrderService] Order {order_id} status updated to {status.value}")
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        order = self.get_order(order_id)
        if not order or order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            return False
        
        # Release inventory
        for item in order.items.values():
            self.inventory_service.release_inventory(
                item.product.product_id, item.quantity, order_id
            )
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        print(f"  [OrderService] Order {order_id} cancelled")
        return True
    
    def process_refund(self, order_id: str, amount: Optional[Money] = None) -> bool:
        order = self.get_order(order_id)
        if not order:
            return False
        
        # Process refund through payment service
        # In real system, we'd look up the payment ID
        print(f"  [OrderService] Processing refund for order {order_id}")
        return True


# ----------------------------------------------------------------------------
# COMPONENT 8: Notification Service Implementation
# ----------------------------------------------------------------------------

class SimpleNotificationService(NotificationService):
    """Customer notifications"""
    
    def __init__(self):
        self._notifications: List[Notification] = []
        self._email_gateway = MockEmailGateway()
        print("  [NotificationService] Initialized")
    
    def send_order_confirmation(self, order: Order) -> Notification:
        subject = f"Order Confirmation: #{order.order_id}"
        content = f"""
        Thank you for your order!
        
        Order Number: {order.order_id}
        Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
        
        Items:
        {self._format_order_items(order)}
        
        Subtotal: {order.subtotal}
        Shipping: {order.shipping_cost}
        Tax: {order.tax_amount}
        Total: {order.total_amount}
        
        Shipping to:
        {order.shipping_address.full_address()}
        
        You will receive shipping confirmation when your order ships.
        
        Thank you for shopping with us!
        """
        
        notification = self._create_notification(
            order.customer_id,
            "order_confirmation",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_shipping_confirmation(self, order: Order, shipment: Shipment) -> Notification:
        subject = f"Your Order #{order.order_id} Has Shipped!"
        content = f"""
        Good news! Your order has shipped.
        
        Order Number: {order.order_id}
        Carrier: {shipment.carrier}
        Tracking Number: {shipment.tracking_number}
        Estimated Delivery: {shipment.estimated_delivery.strftime('%Y-%m-%d')}
        
        Track your package: https://track.{shipment.carrier.lower()}.com/{shipment.tracking_number}
        
        Items in this shipment:
        {self._format_order_items(order)}
        """
        
        notification = self._create_notification(
            order.customer_id,
            "shipping_confirmation",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_payment_receipt(self, payment: Payment) -> Notification:
        subject = f"Payment Receipt: #{payment.payment_id}"
        content = f"""
        Payment Receipt
        
        Payment ID: {payment.payment_id}
        Order ID: {payment.order_id}
        Amount: {payment.amount}
        Payment Method: {payment.method}
        Transaction ID: {payment.transaction_id}
        Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}
        
        Thank you for your payment!
        """
        
        notification = self._create_notification(
            payment.customer_id,
            "payment_receipt",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_order_cancellation(self, order: Order) -> Notification:
        subject = f"Order #{order.order_id} Has Been Cancelled"
        content = f"""
        Your order has been cancelled as requested.
        
        Order Number: {order.order_id}
        Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
        Cancellation Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        If you were charged, a refund has been processed.
        Please allow 3-5 business days for the refund to appear on your statement.
        
        If you have any questions, please contact customer support.
        """
        
        notification = self._create_notification(
            order.customer_id,
            "order_cancellation",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_delivery_confirmation(self, order: Order, shipment: Shipment) -> Notification:
        subject = f"Your Order #{order.order_id} Has Been Delivered"
        content = f"""
        Your order has been delivered!
        
        Order Number: {order.order_id}
        Delivery Date: {shipment.actual_delivery.strftime('%Y-%m-%d') if shipment.actual_delivery else datetime.now().strftime('%Y-%m-%d')}
        
        We hope you enjoy your purchase!
        
        If you have any issues with your order, please contact us within 30 days.
        """
        
        notification = self._create_notification(
            order.customer_id,
            "delivery_confirmation",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_welcome_email(self, customer: Customer) -> Notification:
        subject = f"Welcome, {customer.first_name}!"
        content = f"""
        Welcome to our store, {customer.first_name}!
        
        We're excited to have you as a customer.
        
        Here's a special welcome discount code for your first purchase: WELCOME15
        
        Start shopping now and discover our amazing products!
        
        Happy shopping!
        The Team
        """
        
        notification = self._create_notification(
            customer.customer_id,
            "welcome",
            "email",
            subject,
            content.strip()
        )
        
        self._send_notification(notification)
        return notification
    
    def send_abandoned_cart_reminder(self, cart: Cart) -> Notification:
        if not cart.customer_id:
            return None
        
        subject = "You left items in your cart!"
        content = f"""
        You have {cart.total_items} item(s) waiting in your cart:
        
        {self._format_cart_items(cart)}
        
        Subtotal: {cart.subtotal}
        
        Complete your purchase now and your items won't sell out!
        
        👉 https://store.example.com/cart/{cart.cart_id}
        """
        
        notification = self._create_notification(
            cart.customer_id,
            "abandoned_cart",
            "email",
            subject,
            content.stri)
        )
        
        self._send_notification(notification)
        return notification
    
    def _create_notification(self, customer_id: str, notif_type: str,
                            channel: str, subject: str, content: str) -> Notification:
        notification = Notification(
            notification_id=f"N{str(uuid.uuid4())[:8].upper()}",
            customer_id=customer_id,
            type=notif_type,
            channel=channel,
            subject=subject,
            content=content
        )
        self._notifications.append(notification)
        return notification
    
    def _send_notification(self, notification: Notification):
        # Simulate sending
        self._email_gateway.send(
            to="customer@example.com",  # Would be real email
            subject=notification.subject,
            body=notification.content
        )
        notification.sent_at = datetime.now()
        notification.status = "sent"
        print(f"  [NotificationService] 📧 Sent {notificationype} to customer {notification.customer_id}")
    
    def _format_order_items(self, order: Order) -> str:
        lines = []
        for item in order.items.values():
            lines.append(f"  • {item.quantity}x {item.product.name} - {item.subtotal}")
        return '\n'.join(lines)
    
    def _format_cart_items(self, cart: Cart) -> str:
        lines = []
        for item in cart.items.values():
            lines.append(f"  • {item.quantity}x {item.product.name} - {item.subtotal}")
        return'.join(lines)


class MockEmailGateway:
    """Mock email service"""
    def send(self, to: str, subject: str, body: str):
        # In real system, would call SendGrid/AWS SES/etc.
        pass


# ----------------------------------------------------------------------------
# COMPONENT 9: Customer Service (Additional component)
# ----------------------------------------------------------------------------

class CustomerService:
    """Customer management (separate from core order flow)"""
    
    def __init__(self):
        self._customers: Dict[str, Customer] = {}
        self._email_index: Dict[str, str] = {}  # email -> customer_id
        print("  [CustomerService] Initialized")
    
    def create_customer(self, email: str, first_name: str, last_name: str,
                       phone: Optional[str] = None) -> Customer:
        if email in self._email_index:
            raise ValueError(f"Customer with email {email} already exists")
        
        customer_id = f"CUST{str(uuid.uuid4())[:8].upper()}"
        customer = Customer(
            customer_id=customer_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        self._customers[customer_id] = customer
        self._email_index[email] = customer_id
        
        print(f"  [CustomerService] Created customer: {customer.full_name} ({customer_id})")
        return customer
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self._customers.get(customer_id)
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        customer_id = self._email_index.get(email)
        return self.get_customer(customer_id) if customer_id else None
    
    def update_customer(self, customer_id: str, **kwargs) -> Optional[Customer]:
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        return customer
    
    def add_shipping_address(self, customer_id: str, address: Address) -> bool:
        customer = self.get_customer(customer_id)
        if customer:
            customer.default_shipping_address = address
            return True
        return False
    
    def add_billing_address(self, customer_id: str, address: Address) -> bool:
        customer = self.get_customer(customer_id)
        if customer:
            customer.default_billing_address = address
            return True
        return False


# ============================================================================
# PART 4: E-COMMERCE ORCHESTRATOR
# ============================================================================

class ECommerceSystem:
    """
    Main orchestrator that composes all e-commerce components.
    
    This class:
    1. Initializes all components with proper dependencies
    2. Provides a unified facade for clients
    3. Coordinates workflows across multiple components
    4. Contains NO business logic - only delegation and orchestration
    """
    
    def __init__(self):
        # Initialize core services in dependency order
        self.catalog_service = SimpleCatalogService()
        self.customer_service = CustomerService()
        
        # These depend on catalog
        self.inventory_service = SimpleInventoryService(self.catalog_service)
        self.cart_service = SimpleCartService(self.catalog_service)
        
        # Independent services
        self.pricing_service = SimplePricingService()
        self.shipping_service = SimpleShippingService()
        self.payment_service = SimplePaymentService()
        
        # Notification depends on customers
        self.notification_service = SimpleNotificationService()
        
        # Order depends on almost everything
        self.order_service = SimpleOrderService(
            self.inventory_service,
            self.pricing_service,
            self.shipping_service,
            self.payment_service,
            self.notification_service
        )
        
        print("\n" + "="*70)
        print("🛒 E-COMMERCE SYSTEM INITIALIZED")
        print("="*70)
        print("Components:")
        print("  • CatalogService     - Product catalog and search")
        print("  • InventoryService   - Stock management")
        print("  • CartService        - Shopping cart")
        print("  • PricingService     - Tax and discounts")
        print("  • ShippingService    - Shiplations")
        print("  • PaymentService     - Payment processing")
        print("  • OrderService       - Order management")
        print("  • NotificationService- Customer communications")
        print("  • CustomerService    - Customer profiles")
        print("="*70)
    
    # ======== Catalog Operations ========
    def create_product(self, sku: str, name: str, description: str, 
                      price: float, category: str, weight_kg: float) -> Product:
        product = Product(
    product_id=self.catalog_service.generate_product_id(),
            sku=sku,
            name=name,
            description=description,
            price=Money(Decimal(str(price))),
            category=category,
            weight_kg=weight_kg
        )
        self.catalog_service.create_product(product)
        
        # Initialize inventory with 0 stock
        self.inventory_service.restock_inventory(product.product_id, 0)
        
        return product
    
    def restock_product(self, product_id: str, quantity: int):
        return self.inventory_service.restock_inventory(product_id, quantity)
    
    def search_products(self, query: str, category: Optional[str] = None):
        return self.catalog_service.search_products(query, category)
    
    # ======== Customer Operations ========
    def register_customer(self, email: str, first_name: str, 
                         last_name: str, phone: Optional[str] = None) -> Customer:
        customer = self.customer_service.create_customer(
            email, first_name, last_name, phone
        )
        # Send welcome email
        self.notification_service.send_welcome_email(customer)
        return customer
    
    def get_customer(self, customer_id: str):
        return self.customer_service.get_customer(customer_id)
    
    # ======== Cart Operations ========
    def create_cart(self, customer_id: Optional[str] = None) -> Cart:
        return self.cart_service.create_cart(customer_id)
    
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1):
        return self.cart_service.add_to_cart(cart_id, product_id, quantity)
    
    def get_cart(self, cart_id: str):
        return self.cart_service.get_cart(cart_id)
    
    # ======== Shipping Operations ========
    def get_shipping_methods(self, address: Address) -> List[Dict]:
        return self.shipping_service.get_shipping_methods(address)
    
    # ======== Order Operations ========
    def checkout(self, cart_id: str, customer_id: str, 
                shipping_address: Address, billing_address: Address,
                shipping_method: ShippingMethod, payment_method: str,
                payment_details: Dict[str, Any]) -> Dict[str, Any]:
        
        print(f"\n🛍️  CHECKOUT FLOW - Cart: {cart_id}, Customer: {customer_id}")
        print("-" * 50)
        
        # 1. Get cart
        cart = self.cart_service.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        print(f"   Cart subtotal: {cart.subtotal}"      
        # 2. Create order
        order = self.order_service.create_order_from_cart(
            cart, customer_id, shipping_address, billing_address, shipping_method
        )
        print(f"   Order created: {order.order_id}")
        
        # 3. Process payment
        payment = self.payment_service.process_payment(
            order, payment_method, payment_details
        )
        
        if payment.status == PaymentStatus.CAPTURED:
            # 4. Update order status
            self.order_service.update_order_status(order.order_id, OrderStatus.PAID)
            
            # 5. Create shipment
            shipment = self.shipping_service.create_shipment(order)
            order.tracking_number = shipment.tracking_number
            
            # 6. Update order status
            self.order_service.update_order_status(order.order_id, OrderStatus.PROCESSING)
            
            # 7. Confirm inventory use
            for item in order.items.values():
                self.inventory_service.confirm_inventory_use(
                    item.product.product_id, item.quantity, order.order_id
                )
            
            # 8. Clear cart
            self.cart_service.clear_cart(cart_id)
            
            # 9. Send notifications
            self.notification_service.send_order_confirmation(order)
            self.notification_service.send_shipping_confirmation(order, shipment)
            self.notification_service.send_payment_receipt(payment)
            
            print(f"   ✅ Checkout complete!")
            
            return {
                'success': True,
                'order_id': order.order_id,
                'payment_id': payment.payment_id,
                'tracking_number': shipment.tracking_number,
                'estimated_delivery': shipment.estimated_delivery.isoformat(),
                'total': str(order.total_amount)
            }
        else:
            # Payment failed - release inventory
            self.order_service.cancel_order(order.order_)
            print(f"   ❌ Checkout failed: {payment.error_message}")
            
            return {
                'success': False,
                'error': payment.error_message,
                'order_id': order.order_id
            }
    
    def get_order(self, order_id: str):
        return self.order_service.get_order(order_id)
    
    def get_customer_orders(self, customer_id: str):
        return self.order_service.get_customer_orders(customer_id)
    
    # ======== Utility Operations ======
    def get_low_stock_alert(self) -> List[Dict]:
        low_stock = self.inventory_service.get_low_stock_products()
        alerts = []
        
        for item in low_stock:
            product = self.catalog_service.get_product(item.product_id)
            alerts.append({
                'product_id': item.product_id,
                'product_name': product.name if product else 'Unknown',
                'sku': product.sku if product else 'Unknown',
                'available': item.quantity_available,
                'threshold': item.reorder_threshold,
                'reorder_quantity': item.reorder_quantity
            })
        
        return alerts


# ============================================================================
# ARCHITECTURE DIAGRAM
# ============================================================================

def display_architecture_diagram():
    """Display ASCII component diagram showing modular e-commerce architecture"""
    
    diagram = """
╔════════════════════════════════════════════════════════════════════════════════════╗
║                         MODULAR E-COMMERCE SYSTEM ARCHITECTURE                        ║
║                               Component & Interface Diagram                           ║
╚═════════════════════════════â════════════════════════════════════════╝

                                    ┌─────────────────────┐
                                    │   E-COMMERCE        │
                                    │    ORCHESTRATOR     │
                                    │     (Facade)        │
                                    └──────────┬────â   ┌───────────────────────────────────┼───────────────────────────────────┐
            │                                   │                                   │
            ▼                                   ▼                                   ▼
    ┌───────────────┐                  ┌─────────â┐                  ┌───────────────┐
    │   CATALOG     │                  │   CUSTOMER    │                  │    CART       │
    │   SERVICE     │◄────────────────►│   SERVICE     │◄────────────────►│   SERVICE     │
    │               │                  │               │                  │               │
    │ • Products    │                  │ • │                  │ • Add/Remove  │
    │ • Search      │                  │ • Addresses   │                  │ • Quantity    │
    │ • Categories  │                  │ • History     │                  │ • Subtotal    │
    └───────────────┘                  └───────────────┘                  └───────────────┘
            │                                   â                             │
            ▼                                   ▼                                   ▼
    ┌───────────────┐                  ┌───────────────┐                  ┌───────────────┐
    │  INVENTORY    │                  │   SHIPPING    │                  │   PRICING     │
    │   SERVICE     │                  │   SERVICE     │                  │   ICE     │
    │               │                  │               │                  │               │
    │ • Availability│                  │ • Cost Calc   │                  │ • Tax Calc    │
    │ • Reservation │                  │ • Methods     │                  │ • Discounts   │
    │ • Low Stock   │                  │ • Tracking    │                  │ • Conversion  │
    └───────────────┘            └───────────────┘                  └───────────────┘
            │                                   │                                   │
            └───────────────┬───────────────────┼───────────────────┬───────────────┘
                            │                   │                   │
                            ▼                   ▼                   ▼
                    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
                    │    ORDER      │  │   PAYMENT     │  │ NOTIFICATION  │
                    │   SERVICE     │  │   SERVICE     │  │   SERVICE     │
                    │               │  │               │  │               │
                    │ • Creation    │  │ • Process     │  │ • Order Conf  │
                    │ • Status      │  │ • Refund      │  │ • Shipping    │
                    │ • History     │  │ • Auth/Capture│  │ • Receipts    │
                    └───────────────┘  └───────────────┘  └───────────────┘

━━━━━━━━━━━â━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEGEND:
◄────► Bidirectional dependency/communication
─────► Unidirectional flow
┌────┐ Independent component with single responsibility
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━â━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY DESIGN PRINCIPLES:
1. Single Responsibility - Each component has ONE job
2. Interface Segregation - Clean, focused method sets
3. Dependency Inversion - Components depend on interfaces
4. Composition over Inheritance - Orchestrator composes components
5. Independent Deployability - Components can be developed/tested in isolation
━━━━━━━━━━━━━━━â━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(diagram)


# ============================================================================
# INTERFACE DEFINITIONS
# ============================================================================

def display_interface_definitions():
    """Display the formal contracts between components"""
 terfaces = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           COMPONENT INTERFACE DEFINITIONS                             ║
║                            (Contracts between modules)                                ║
╚═════════════â══════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 1. CATALOG SERVICE INTERFACE                                               │
├──────────────────────────────────────────────────────────────────────────────────────┤
│   get_product(product_id: str) -> Optional[Product]                                  │
│   search_products(query: str, category: str = None) -> List[Product]                │
│   get_products_bategory: str) -> List[Product]                          │
│   get_product_price(product_id: str) -> Optional[Money]                             │
│   create_product(product: Product) -> Product                                        │
│   update_product(product_id: str, **kwargs) -> Optional[Product]                    │
│   deactivate_product(product_id: str) -> bool                                        │
└──────────────────────────â──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 2. INVENTORY SERVICE INTERFACE                                                       ────────────────────────────────────────────────────────────────────────────────┤
│   get_inventory(product_id: str) -> Optional[InventoryItem]                         │
│   check_availability(product_id: str, quantity: int) -> bool                         │
│   reserve_inventory(product_id: str, quantity: int, order_id: str) -> bool     elease_inventory(product_id: str, quantity: int, order_id: str) -> bool          │
│   confirm_inventory_use(product_id: str, quantity: int, order_id: str) -> bool      │
│   restock_inventory(product_id: str, quantity: int) -> bool                          │
│   get_low_stock_products() -> List[InventoryItem]                                   │
└────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 3. CART SERVICE INTERFACE                                                            │
├─────────────â──────────────────────────────────────────────────────────────┤
│   create_cart(customer_id: str = None) -> Cart                                      │
│   get_cart(cart_id: str) -> Optional[Cart]                                          │
│   add_to_cart(cart_id: str, product_id: str, quantity: int = 1) -> Optional[Cart]  │
│   remove_from_cart(cart_id: str, productptional[Cart]                 │
│   update_cart_item(cart_id: str, product_id: str, quantity: int) -> Optional[Cart] │
│   clear_cart(cart_id: str) -> bool                                                  │
│   get_cart_subtotal(cart_id: str) -> Optional[Money]                                │
└──────────────────────────────────────────────────────────────────â─────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 4. PRICING SERVICE INTERFACE                                                         │
├──────────────────────────────────â─────────────────────────────────────────┤
│   calculate_tax(amount: Money, address: Address) -> Money                           │
│   apply_discount(amount: Money, discount_code: str) -> Money                        │
│   calculate_order_total(subtotal: Money, shipping: Money, tax: Money) -> Money      │
│   get_currency_conversion(amount: Money, target: Currency) -> Money                 │
└───â──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 5. SHIPPING SERVICE INTERFACE                                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│   calculate_shipping_cost(items: List[CartItem], address: Address,                  │
│                          method: ShippingMethod) -> Money                           │
│   get_estimated_d(method: ShippingMethod, address: Address) -> datetime │
│   create_shipment(order: Order) -> Shipment                                          │
│   track_shipment(tracking_number: str) -> Dict                                      │
│   get_shipping_methods(address: Address) -> List[Dict]                              │
└─────────────────────────────────────────────────────────â────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 6. PAYMENT SERVICE INTERFACE                                                         │
├───────────────────────â────────────────────────────────────────────────────┤
│   process_payment(order: Order, method: str, details: Dict) -> Payment              │
│   refund_payment(payment_id: str, amount: Money = None) -> Payment                  │
│   get_payment_status(payment_id: str) -> PaymentStatus                               │
│   authorize_payment(order: Order, method: str, details: Dict) -> Pay      │
│   capture_payment(payment_id: str) -> Payment                                        │
│   void_payment(payment_id: str) -> Payment                                           │
└──────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────â──────────────────────────────────────────────────────────┐
│ 7. ORDER SERVICE INTERFACE                                                           │
├──────────────────────────────────────────────────────────────────────────────â create_order_from_cart(cart: Cart, customer_id: str, shipping_addr: Address,      │
│                         billing_addr: Address, method: ShippingMethod) -> Order      │
│   get_order(order_id: str) -> Optional[Order]                                       │
│   get_customer_orders(customer_id: str) -> List[Order]                              │
│   update_order_status(order_id: str, status: OrderStatus) -> Optional[Order]        │
│   cancel_order(order_id: str) -> bool                                            │
│   process_refund(order_id: str, amount: Money = None) -> bool                       │
└──────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────â─────────────────────────────────────────┐
│ 8. NOTIFICATION SERVICE INTERFACE                                                    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│   send_order_confirm Order) -> Notification                              │
│   send_shipping_confirmation(order: Order, shipment: Shipment) -> Notification       │
│   send_payment_receipt(payment: Payment) -> Notification                             │
│   send_order_cancellation(order: Order) -> Notification                              │
│   send_delivery_confirmation(order: Order, shipment: Shipment) -> Notification       │
│   send_welcome_email(customer: Customer) -> Notification                         │
│   send_abandoned_cart_reminder(cart: Cart) -> Notification                           │
└──────────────────────────────────────────────────────────────────────────────────────┘
"""
    print(interfaces)


# ============================================================================
# DEMONSTRATION
# ======================================================================

def demonstrate_ecommerce_system():
    """Demonstrate the modular e-commerce system"""
    
    print("\n" + "="*80)
    print("EXERCISE 2.2: Design a Modular E-commerce System 🟡")
    print("="*80)
    
    # Display architecture diagram
    display_architecture_diagram()
    
    # Display interface definitions
    display_interface_definitions()
    
    # Initialize the system
    print("\n🚀 INITIALIZING E-COMMERCE SYSTEM")
    print("="*80)
    st= ECommerceSystem()
    
    # ======== SCENARIO 1: Add Products ========
    print("\n📦 SCENARIO 1: Adding Products to Catalog")
    print("-"*60)
    
    # Add electronics
    laptop = store.create_product(
        sku="LAP-001",
        name="UltraBook Pro 15",
        description="15-inch laptop, 16GB RAM, 512GB SSD",
        price=1299.99,
        category="Electronics",
        weight_kg=2.5
    )
    store.restock_product(laptop.product_id, 15)
    
    phone = store.create_product(
        sku="N-001",
        name="SmartPhone X12",
        description="6.7-inch display, 128GB storage, 5G",
        price=899.99,
        category="Electronics",
        weight_kg=0.3
    )
    store.restock_product(phone.product_id, 30)
    
    # Add books
    book1 = store.create_product(
        sku="BK-001",
        name="Clean Architecture",
        description="A craftsman's guide to software structure and design",
        price=45.99,
        category="Books",
        weight_kg=0.8
    )
    store.restock_product(book1.product_id, 25)
    
    book2 = store.create_product(
        sku="BK-002",
        name="Design Patterns",
        description="Elements of Reusable Object-Oriented Software",
        price=52.99,
        category="Books",
        weight_kg=0.9
    )
    store.restock_product(book2.product_id, 20)
    
    # Add clothing
    shirt = store.create_product(
        sku="CL-001",
        name="Cotton T-Shirt",
        description="100% organic cotton, crew neck",
        price=24.99,
        category="Clothing",
        weight_kg=0.2
    )
    store.restock_product(shirt.product_id, 50)
    
    print(f"\n  ✅ Added 5 products to catalog")
    
    # ======== SCENARIO 2: Customer Registration ========
    print("\n👤 SCENARIO 2: Customer Registration")
    print("-"*60)
    
    customer = store.register_customer(
        email="alice.johnson@email.com",
        first_name="Alice",
        last_name="Johnson",
        phone="555-123-4567"
    )
    print(f"\n  ✅ Registered customer: {customer.fue} ({customer.customer_id})")
    
    # Add shipping address
    shipping_address = Address(
        street="123 Main Street",
        city="Seattle",
        state="WA",
        postal_code="98101",
        country="US"
    )
    store.customer_service.add_shipping_address(customer.customer_id, shipping_address)
    
    billing_address = Address(
        street="123 Main Street",
        city="Seattle",
        state="WA",
        postal_code="98101",
        country="US"
    )
    store.customer_service.add_billing_address(customer.customer_id, billing_address)
    print(f"  ✅ Added shipping/billing address")
    
    # ======== SCENARIO 3: Shopping Cart ========
    print("\n🛒 SCENARIO 3: Shopping Cart")
    print("-"*60)
    
    cart = store.create_cart(customer.customer_id)
    print(f"  ✅ Created cart: {cart.cart_id}")
    
    # Add items to cart
    store.add_to_cart(cart.cart_id, laptop.product_id, 1)
    store.add_to_cart(cart.cart_id, book1.product_id, 2)
    store.add_to_cart(cart.cart_irt.product_id, 3)
    
    cart = store.get_cart(cart.cart_id)
    print(f"\n  📋 Cart Contents:")
    for item in cart.items.values():
        print(f"     • {item.quantity}x {item.product.name} - {item.subtotal}")
    print(f"\n  💰 Cart Subtotal: {cart.subtotal}")
    
    # ======== SCENARIO 4: Shipping Options ========
    print("\n🚚 SCENARIO 4: Shipping Options")
    print("-"*60)
    
    shipping_methods = store.get_shipping_methods(shipping_address)
    print(f"\n  📦 Available Shipping )
    for method in shipping_methods:
        print(f"     • {method['method'].upper()}: {method['cost']} - {method['estimated_days']} days")
    
    # ======== SCENARIO 5: Checkout ========
    print("\n💳 SCENARIO 5: Checkout Process")
    print("-"*60)
    
    # Mock payment details
    payment_details = {
        'card_number': '4111111111111111',
        'expiry': '12/25',
        'cvv': '123',
        'cardholder_name': 'Alice Johnson'
    }
    
    result = store.checkout(
        cart_id=cartt_id,
        customer_id=customer.customer_id,
        shipping_address=shipping_address,
        billing_address=billing_address,
        shipping_method=ShippingMethod.EXPRESS,
        payment_method='credit_card',
        payment_details=payment_details
    )
    
    # ======== SCENARIO 6: Order History ========
    print("\n📋 SCENARIO 6: Order History")
    print("-"*60)
    
    orders = store.get_customer_orders(customer.customer_id)
    print(f"\n  Customer Orders ({len(orders)}):")
    for ordein orders:
        print(f"     • Order #{order.order_id}: {order.status.value} - {order.total_amount}")
        print(f"       Items: {order.item_count}, Tracking: {order.tracking_number or 'N/A'}")
    
    # ======== SCENARIO 7: Low Stock Alert ========
    print("\n⚠️ SCENARIO 7: Low Stock Alert")
    print("-"*60)
    
    # Simulate low stock
    store.inventory_service.get_inventory(laptop.product_id).quantity_available = 5
    store.inventory_service.get_inventory(phone.product_id).quantity_ave = 8
    
    low_stock = store.get_low_stock_alert()
    print(f"\n  Low Stock Products:")
    for alert in low_stock:
        print(f"     • {alert['product_name']}: {alert['available']} left (threshold: {alert['threshold']})")
    
    # ======== SCENARIO 8: Independent Component Testing ========
    print("\n" + "="*80)
    print("🧪 DEMONSTRATION: Independent Component Testing")
    print("="*80)
    print("""
    Each component can be tested in isolation with mocks:
    
    ✅ CatalogService Te      catalog = SimpleCatalogService()
        product = catalog.create_product(mock_product)
        assert catalog.get_product(product.product_id) == product
    
    ✅ InventoryService Test:
        inventory = SimpleInventoryService(mock_catalog)
        inventory.restock_inventory("P123", 10)
        assert inventory.check_availability("P123", 5) == True
    
    ✅ CartService Test:
        cart = SimpleCartService(mock_catalog)
        cart.create_cart()
        cart.add_to_cart(cart_id, "P123", 2      assert cart.get_cart_subtotal(cart_id) == expected
    
    ✅ PricingService Test:
        pricing = SimplePricingService()
        tax = pricing.calculate_tax(Money(100), address)
        assert tax.amount == Decimal('8.25')
    
    ✅ ShippingService Test:
        shipping = SimpleShippingService()
        cost = shipping.calculate_shipping_cost(items, address, method)
        assert cost.amount > 0
    
    ✅ PaymentService Test:
        payment = SimplePaymentService()
        result = paymecess_payment(order, "credit_card", details)
        assert result.status in [PaymentStatus.CAPTURED, PaymentStatus.FAILED]
    
    ✅ OrderService Test:
        order_service = SimpleOrderService(mock_inventory, mock_pricing, ...)
        order = order_service.create_order_from_cart(cart, customer_id, ...)
        assert order.order_id is not None
    
    ✅ NotificationService Test:
        notifier = SimpleNotificationService()
        notif = notifier.send_order_confirmation(order)
        assert notype == "order_confirmation"
    """)


def main():
    """Main entry point"""
    demonstrate_ecommerce_system()
    
    print("\n" + "="*80)
    print("📌 DESIGN DECISIONS & MODULARITY PRINCIPLES")
    print("="*80)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  KEY DESIGN DECISION 1: Inteace-First Design                             │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │  We defined ABC interfaces BEFORE implementations. This:                   │
    │  • Establishes clear contracts between components                          │
    │  • Allows multiple implementations , UPS/FedEx)              │
    │  • Enables mocking for unit tests                                          │
    │  • Follows Dependency Inversion Principle                                  │
    └─────────────────────────────────────────────────────────────────────────────┘
    
    ┌────────────────â────────────────────────────────────────────┐
    │  KEY DESIGN DECISION 2: Single Responsibility Components                   │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │  Each component has ONE reason to change:                                  │
    │  • CatalogService     → Product data & search                              │
    │  • InventoryService   → Stock levels & reservations                        │
    │  • CartService        → Shopping cart state                                │
    │  • PricingService     → Tax, discounts, currency                           │
    │  • ShippingService    → Cost, methods, tracking                            │
    │  • P    → Payment processing & refunds                       │
    │  • OrderService       → Order lifecycle                                    │
    │  • NotificationService→ Customer communications                            │
    │  • CustomerService    → Customer profiles                                  │
    └────────────────────────────────────────────────────────â─────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  KEY DESIGN DECISION 3: Dependency Injection                               │
    ├─────────────────────────────────────────────────â─────────────────────┤
    │  Dependencies are injected via constructors, not hardcoded:               │
    │                                                                           │
│  inventory = SimpleInventoryService(catalog)  # Depends on interface      │
    │  order = SimpleOrderService(inventory, pricing, shipping, ...)           │
    │                                                                           │
    │  Benefits                                                             │
    │  • Components can be swapped at runtime                                   │
    │  • Testing with mocks is trivial                                          │
    │  • Dependencies are explicit, not hidden                                  │
    └──────────────────────────────────────────────────────────â──────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  KEY DESIGN DECISION 4: Orchestrator Pattern                              │
    ├───────────────────────────────────────────────────────────────────────┤
    │  ECommerceSystem contains NO business logic - only composition:           │
    │  • Initializes all components with proper dependencies                    │
    │  • Delegates all operations to specialized components                     │
    │  • Coordinates workflows (checkout) across components                     │
    │  • Provides unified facade for clients                                    │
    ────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  KEY DESIGN DECISION 5: Rich Domain Models                      │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │  Domain objects contain behavior, not just data:                          │
    │  • Money: currency-safe arithmetic                                        │
    │  • Cart: subtotal calculation, item management                       • Product: availability logic                                            │
    │  • Order: status management                                               │
    │                                                                           │
    │  This follows the "rich domain model" pattern vs. anemic models.          │
    └──────────────────────────────────────────────────────â────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  BENEFITS OF THIS MODULAR DESIGN                                          │
    ├───────────────────────────────────────────────────────────────────────┤
    │  ✅ PARALLEL DEVELOPMENT: 9 devs can work on 9 components simultaneously  │
    │  ✅ TESTABILITY: Each component can be tested in isolation                │
    │  ✅ SWAPPABLE: Replace UPS with FedEx by implementing ShippingService     │
    │  ✅ MAINTAINABLE: Bug in tax calculation? Only touch PricingService       │
    │  ✅ EXTENSIBLE: Add WishlistService withouting existing code        │
    │  ✅ UNDERSTANDABLE: New dev learns one component at a time                │
    │  ✅ DEPLOYABLE: Components can be versioned independently                 │
    └─────────────────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Example 2: Components and Connectors

This example demonstrates:
- Components: Computational units that encapsulate functionality
- Connectors: Communication mechanisms between components
- Component interfaces: How components expose their functionality
- Connector types: Different ways components communicate
- Component composition: Building systems from components

Key Concept: Architecture = Components + Connectors
"""

from typing import Dict, List, Optional, Protocol, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json


# ============================================================================
# BUSINESS SCENARIO: Online Banking System
# ============================================================================
# Components: Account Service, Transaction Service, Notification Service
# Connectors: REST API, Message Queue, Database Connection


# ============================================================================
# COMPONENT: A computational unit with a clear interface
# ============================================================================

class ComponentType(Enum):
    """Types of components"""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    GATEWAY = "gateway"


@dataclass
class ComponentInterface:
    """Interface that a component exposes"""
    name: str
    methods: List[str]
    input_types: Dict[str, str]
    output_types: Dict[str, str]
    
    def describe(self):
        print(f"  Interface: {self.name}")
        for method in self.methods:
            inputs = self.input_types.get(method, "()")
            output = self.output_types.get(method, "void")
            print(f"    - {method}{inputs} -> {output}")


class Component:
    """A component in the architecture"""
    
    def __init__(self, name: str, component_type: ComponentType):
        self.name = name
        self.type = component_type
        self.interface: Optional[ComponentInterface] = None
        self.responsibilities: List[str] = []
        self.state: Dict = {}
    
    def set_interface(self, interface: ComponentInterface):
        """Define the component's interface"""
        self.interface = interface
        print(f"✓ Component '{self.name}' interface defined")
    
    def add_responsibility(self, responsibility: str):
        """Add a responsibility to the component"""
        self.responsibilities.append(responsibility)
    
    def describe(self):
        """Describe the component"""
        print(f"\nComponent: {self.name}")
        print(f"  Type: {self.type.value}")
        print(f"  Responsibilities: {', '.join(self.responsibilities)}")
        if self.interface:
            self.interface.describe()


# ============================================================================
# CONNECTOR: Communication mechanism between components
# ============================================================================

class ConnectorType(Enum):
    """Types of connectors"""
    REST_API = "rest_api"
    MESSAGE_QUEUE = "message_queue"
    DATABASE_CONNECTION = "database_connection"
    EVENT_BUS = "event_bus"
    DIRECT_CALL = "direct_call"
    FILE_SYSTEM = "file_system"


@dataclass
class Connector:
    """A connector between components"""
    name: str
    connector_type: ConnectorType
    source_component: str
    target_component: str
    protocol: str
    data_format: str
    properties: Dict[str, str] = field(default_factory=dict)
    
    def describe(self):
        print(f"\nConnector: {self.name}")
        print(f"  Type: {self.connector_type.value}")
        print(f"  From: {self.source_component} → To: {self.target_component}")
        print(f"  Protocol: {self.protocol}")
        print(f"  Data Format: {self.data_format}")
        if self.properties:
            print(f"  Properties: {self.properties}")


# ============================================================================
# ARCHITECTURE: Components + Connectors
# ============================================================================

class SystemArchitecture:
    """An architecture defined by components and connectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.components: Dict[str, Component] = {}
        self.connectors: List[Connector] = []
    
    def add_component(self, component: Component):
        """Add a component to the architecture"""
        self.components[component.name] = component
        print(f"✓ Added component: {component.name}")
    
    def add_connector(self, connector: Connector):
        """Add a connector to the architecture"""
        # Validate that components exist
        if connector.source_component not in self.components:
            raise ValueError(f"Source component '{connector.source_component}' not found")
        if connector.target_component not in self.components:
            raise ValueError(f"Target component '{connector.target_component}' not found")
        
        self.connectors.append(connector)
        print(f"✓ Added connector: {connector.name}")
    
    def describe(self):
        """Describe the complete architecture"""
        print("\n" + "="*70)
        print(f"ARCHITECTURE: {self.name}")
        print("="*70)
        
        print(f"\nCOMPONENTS ({len(self.components)}):")
        for component in self.components.values():
            component.describe()
        
        print(f"\nCONNECTORS ({len(self.connectors)}):")
        for connector in self.connectors:
            connector.describe()
        
        print("\n" + "="*70)
        print("ARCHITECTURE SUMMARY")
        print("="*70)
        print(f"Total Components: {len(self.components)}")
        print(f"Total Connectors: {len(self.connectors)}")
        print(f"\nComponent Types:")
        type_count = {}
        for component in self.components.values():
            type_count[component.type] = type_count.get(component.type, 0) + 1
        for comp_type, count in type_count.items():
            print(f"  - {comp_type.value}: {count}")
        
        print(f"\nConnector Types:")
        connector_type_count = {}
        for connector in self.connectors:
            connector_type_count[connector.connector_type] = \
                connector_type_count.get(connector.connector_type, 0) + 1
        for conn_type, count in connector_type_count.items():
            print(f"  - {conn_type.value}: {count}")


# ============================================================================
# EXAMPLE: Online Banking System
# ============================================================================

def demonstrate_components_and_connectors():
    """Show components and connectors in a banking system"""
    
    print("\n" + "="*70)
    print("EXAMPLE: Online Banking System Architecture")
    print("="*70)
    
    architecture = SystemArchitecture("Online Banking System")
    
    # ========================================================================
    # COMPONENTS
    # ========================================================================
    
    # Account Service Component
    account_service = Component("Account Service", ComponentType.SERVICE)
    account_service.add_responsibility("Manage user accounts")
    account_service.add_responsibility("Handle account creation and updates")
    account_service.add_responsibility("Validate account information")
    
    account_interface = ComponentInterface(
        name="AccountServiceAPI",
        methods=["createAccount", "getAccount", "updateAccount", "deleteAccount"],
        input_types={
            "createAccount": "(userId: str, accountType: str)",
            "getAccount": "(accountId: str)",
            "updateAccount": "(accountId: str, updates: dict)",
            "deleteAccount": "(accountId: str)"
        },
        output_types={
            "createAccount": "Account",
            "getAccount": "Account",
            "updateAccount": "Account",
            "deleteAccount": "bool"
        }
    )
    account_service.set_interface(account_interface)
    architecture.add_component(account_service)
    
    # Transaction Service Component
    transaction_service = Component("Transaction Service", ComponentType.SERVICE)
    transaction_service.add_responsibility("Process transactions")
    transaction_service.add_responsibility("Validate transaction amounts")
    transaction_service.add_responsibility("Maintain transaction history")
    
    transaction_interface = ComponentInterface(
        name="TransactionServiceAPI",
        methods=["processTransaction", "getTransactionHistory", "reverseTransaction"],
        input_types={
            "processTransaction": "(fromAccount: str, toAccount: str, amount: float)",
            "getTransactionHistory": "(accountId: str, startDate: date, endDate: date)",
            "reverseTransaction": "(transactionId: str)"
        },
        output_types={
            "processTransaction": "Transaction",
            "getTransactionHistory": "List[Transaction]",
            "reverseTransaction": "bool"
        }
    )
    transaction_service.set_interface(transaction_interface)
    architecture.add_component(transaction_service)
    
    # Notification Service Component
    notification_service = Component("Notification Service", ComponentType.SERVICE)
    notification_service.add_responsibility("Send notifications to users")
    notification_service.add_responsibility("Manage notification preferences")
    notification_service.add_responsibility("Support multiple channels (email, SMS, push)")
    
    notification_interface = ComponentInterface(
        name="NotificationServiceAPI",
        methods=["sendNotification", "getNotificationPreferences", "updatePreferences"],
        input_types={
            "sendNotification": "(userId: str, message: str, channel: str)",
            "getNotificationPreferences": "(userId: str)",
            "updatePreferences": "(userId: str, preferences: dict)"
        },
        output_types={
            "sendNotification": "bool",
            "getNotificationPreferences": "NotificationPreferences",
            "updatePreferences": "bool"
        }
    )
    notification_service.set_interface(notification_interface)
    architecture.add_component(notification_service)
    
    # Account Database Component
    account_db = Component("Account Database", ComponentType.DATABASE)
    account_db.add_responsibility("Persist account data")
    account_db.add_responsibility("Provide ACID transactions")
    account_db.add_responsibility("Support queries and indexing")
    architecture.add_component(account_db)
    
    # Transaction Database Component
    transaction_db = Component("Transaction Database", ComponentType.DATABASE)
    transaction_db.add_responsibility("Persist transaction data")
    transaction_db.add_responsibility("Maintain transaction history")
    transaction_db.add_responsibility("Support audit trails")
    architecture.add_component(transaction_db)
    
    # Message Queue Component
    message_queue = Component("Message Queue", ComponentType.QUEUE)
    message_queue.add_responsibility("Reliable message delivery")
    message_queue.add_responsibility("Message persistence")
    message_queue.add_responsibility("Support pub/sub patterns")
    architecture.add_component(message_queue)
    
    # ========================================================================
    # CONNECTORS
    # ========================================================================
    
    # REST API connector: Client → Account Service
    connector1 = Connector(
        name="Client to Account Service API",
        connector_type=ConnectorType.REST_API,
        source_component="External Client",
        target_component="Account Service",
        protocol="HTTP/HTTPS",
        data_format="JSON",
        properties={"method": "REST", "authentication": "OAuth2"}
    )
    # Note: External client is not a component in our architecture
    # This is a boundary connector
    
    # REST API connector: Account Service → Transaction Service
    connector2 = Connector(
        name="Account Service to Transaction Service",
        connector_type=ConnectorType.REST_API,
        source_component="Account Service",
        target_component="Transaction Service",
        protocol="HTTP",
        data_format="JSON",
        properties={"method": "REST", "timeout": "5s"}
    )
    architecture.add_connector(connector2)
    
    # Message Queue connector: Transaction Service → Notification Service
    connector3 = Connector(
        name="Transaction Service to Notification Service",
        connector_type=ConnectorType.MESSAGE_QUEUE,
        source_component="Transaction Service",
        target_component="Notification Service",
        protocol="AMQP",
        data_format="JSON",
        properties={"queue": "transaction-events", "durable": "true"}
    )
    architecture.add_connector(connector3)
    
    # Database connector: Account Service → Account Database
    connector4 = Connector(
        name="Account Service to Account Database",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Account Service",
        target_component="Account Database",
        protocol="PostgreSQL",
        data_format="SQL",
        properties={"connection_pool": "10", "ssl": "true"}
    )
    architecture.add_connector(connector4)
    
    # Database connector: Transaction Service → Transaction Database
    connector5 = Connector(
        name="Transaction Service to Transaction Database",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Transaction Service",
        target_component="Transaction Database",
        protocol="PostgreSQL",
        data_format="SQL",
        properties={"connection_pool": "10", "ssl": "true"}
    )
    architecture.add_connector(connector5)
    
    # Message Queue connector: Notification Service → Message Queue
    connector6 = Connector(
        name="Notification Service to Message Queue",
        connector_type=ConnectorType.MESSAGE_QUEUE,
        source_component="Notification Service",
        target_component="Message Queue",
        protocol="AMQP",
        data_format="JSON",
        properties={"queue": "notification-queue", "durable": "true"}
    )
    architecture.add_connector(connector6)
    
    # ========================================================================
    # DESCRIBE ARCHITECTURE
    # ========================================================================
    
    architecture.describe()
    
    # ========================================================================
    # KEY CONCEPTS
    # ========================================================================
    
    print("\n" + "="*70)
    print("KEY CONCEPTS: Components and Connectors")
    print("="*70)
    print("""
COMPONENTS:
  • Computational units that encapsulate functionality
  • Have clear responsibilities
  • Expose interfaces for interaction
  • Can be services, databases, queues, etc.
  • Examples: Account Service, Transaction Service, Database

CONNECTORS:
  • Communication mechanisms between components
  • Define how components interact
  • Can be synchronous (REST API) or asynchronous (Message Queue)
  • Examples: REST API, Message Queue, Database Connection

ARCHITECTURE = COMPONENTS + CONNECTORS:
  • Components define WHAT exists
  • Connectors define HOW they communicate
  • Together they form the system architecture
  • Good architecture has clear component boundaries
  • Good architecture uses appropriate connectors

COMPONENT INTERFACES:
  • Define what a component can do
  • Hide implementation details
  • Enable component replacement
  • Support testing and mocking
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_components_and_connectors()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Components are computational units with clear responsibilities
✓ Connectors define how components communicate
✓ Architecture = Components + Connectors
✓ Component interfaces hide implementation details
✓ Different connector types serve different purposes
✓ Good architecture uses appropriate connectors for each interaction
    """)


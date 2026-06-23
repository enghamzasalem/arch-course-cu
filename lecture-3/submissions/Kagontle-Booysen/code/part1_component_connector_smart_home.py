#!/usr/bin/env python3
"""
(Smart Home): Components and Connectors

This example demonstrates:
- Components: Computational units that encapsulate functionality
- Connectors: Communication mechanisms between components
- Component interfaces: How components expose their functionality
- Connector types: Different ways components communicate (sync + async)
- Component composition: Building a Smart Home system from components

Key Concept: Architecture = Components + Connectors
"""

from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# BUSINESS SCENARIO: Smart Home Management System
# ============================================================================
# Components: Mobile App, Web App, API Gateway, Identity Service, Device Manager,
#             Automation Service, Notification Service, Event Bus, Databases, IoT Hub
# Connectors: REST API, Pub/Sub (Event Bus), Database Connection, MQTT/WebSocket


# ============================================================================
# COMPONENT: A computational unit with a clear interface
# ============================================================================

class ComponentType(Enum):
    """Types of components"""
    CLIENT = "client"
    SERVICE = "service"
    DATABASE = "database"
    BROKER = "broker"
    GATEWAY = "gateway"
    IOT = "iot"


@dataclass
class ComponentInterface:
    """Interface that a component exposes"""
    name: str
    methods: List[str]
    input_types: Dict[str, str]
    output_types: Dict[str, str]

    def describe(self) -> None:
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

    def set_interface(self, interface: ComponentInterface) -> None:
        """Define the component's interface"""
        self.interface = interface
        print(f"✓ Component '{self.name}' interface defined")

    def add_responsibility(self, responsibility: str) -> None:
        """Add a responsibility to the component"""
        self.responsibilities.append(responsibility)

    def describe(self) -> None:
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
    EVENT_BUS = "event_bus_pubsub"
    MESSAGE_QUEUE = "message_queue"
    DATABASE_CONNECTION = "database_connection"
    REALTIME_IOT = "realtime_iot"


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

    def describe(self) -> None:
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

    def add_component(self, component: Component) -> None:
        """Add a component to the architecture"""
        self.components[component.name] = component
        print(f"✓ Added component: {component.name}")

    def add_connector(self, connector: Connector) -> None:
        """Add a connector to the architecture"""
        if connector.source_component not in self.components:
            raise ValueError(f"Source component '{connector.source_component}' not found")
        if connector.target_component not in self.components:
            raise ValueError(f"Target component '{connector.target_component}' not found")

        self.connectors.append(connector)
        print(f"✓ Added connector: {connector.name}")

    def describe(self) -> None:
        """Describe the complete architecture"""
        print("\n" + "=" * 70)
        print(f"ARCHITECTURE: {self.name}")
        print("=" * 70)

        print(f"\nCOMPONENTS ({len(self.components)}):")
        for component in self.components.values():
            component.describe()

        print(f"\nCONNECTORS ({len(self.connectors)}):")
        for connector in self.connectors:
            connector.describe()

        print("\n" + "=" * 70)
        print("ARCHITECTURE SUMMARY")
        print("=" * 70)
        print(f"Total Components: {len(self.components)}")
        print(f"Total Connectors: {len(self.connectors)}")

        print("\nComponent Types:")
        type_count: Dict[ComponentType, int] = {}
        for component in self.components.values():
            type_count[component.type] = type_count.get(component.type, 0) + 1
        for comp_type, count in type_count.items():
            print(f"  - {comp_type.value}: {count}")

        print("\nConnector Types:")
        connector_type_count: Dict[ConnectorType, int] = {}
        for connector in self.connectors:
            connector_type_count[connector.connector_type] = connector_type_count.get(connector.connector_type, 0) + 1
        for conn_type, count in connector_type_count.items():
            print(f"  - {conn_type.value}: {count}")

    def ascii_view(self) -> None:
        """Quick ASCII view of the component & connector diagram"""
        print("\n" + "=" * 70)
        print("ASCII VIEW: Smart Home Components & Connectors")
        print("=" * 70)
        print(
            r"""
[Mobile App]   [Web App]   [Voice Assistant]
     \           |            /
      \          |           /
       +-------------------+
       |    API Gateway    |
       +----+----+----+----+
            |    |    |
            v    v    v
       [Identity] [Device Manager] --(MQTT/WebSocket)--> [IoT Hub/Devices]
            |
            +-------------------+
                                |
                         (Pub/Sub Events)
                                v
                           [Event Bus]
                           /        \
                          v          v
                    [Automation]  [Notification]

[Identity] ------(SQL)------> [User DB]
[Device Manager] --(SQL/NoSQL)-> [Device DB]
[Automation] ----(SQL/NoSQL)-> [Rules DB]
[Notification] --(SQL/NoSQL)-> [Notif DB]
"""
        )


# ============================================================================
# EXAMPLE: Smart Home Management System Architecture
# ============================================================================

def demonstrate_components_and_connectors_smart_home() -> None:
    """Show components and connectors in a smart home system"""

    print("\n" + "=" * 70)
    print("EXAMPLE: Smart Home Management System Architecture")
    print("=" * 70)

    architecture = SystemArchitecture("Smart Home Management System")

    # ========================================================================
    # COMPONENTS
    # ========================================================================

    # Mobile App (Client)
    mobile = Component("Mobile App", ComponentType.CLIENT)
    mobile.add_responsibility("Send device commands (on/off, lock/unlock)")
    mobile.add_responsibility("Display device status and alerts")
    mobile.add_responsibility("Manage basic routines")
    mobile.set_interface(ComponentInterface(
        name="MobileClientAPI",
        methods=["sendCommand", "viewStatus", "manageRoutine"],
        input_types={
            "sendCommand": "(deviceId: str, command: str)",
            "viewStatus": "(deviceId: str)",
            "manageRoutine": "(routineId: str, updates: dict)"
        },
        output_types={
            "sendCommand": "CommandResult",
            "viewStatus": "DeviceState",
            "manageRoutine": "bool"
        }
    ))
    architecture.add_component(mobile)

    # Web App (Client)
    web = Component("Web App", ComponentType.CLIENT)
    web.add_responsibility("Configure advanced routines and schedules")
    web.add_responsibility("View analytics dashboards")
    web.add_responsibility("Admin settings for home/users")
    web.set_interface(ComponentInterface(
        name="WebClientAPI",
        methods=["configureRoutine", "viewAnalytics", "manageUsers"],
        input_types={
            "configureRoutine": "(routineId: str, rule: dict)",
            "viewAnalytics": "(timeRange: str)",
            "manageUsers": "(updates: dict)"
        },
        output_types={
            "configureRoutine": "bool",
            "viewAnalytics": "Report",
            "manageUsers": "bool"
        }
    ))
    architecture.add_component(web)

    # Voice Assistant Integration (Client)
    voice = Component("Voice Assistant", ComponentType.CLIENT)
    voice.add_responsibility("Convert voice commands into API calls")
    voice.add_responsibility("Return spoken confirmations")
    voice.set_interface(ComponentInterface(
        name="VoiceIntegrationAPI",
        methods=["invokeIntent"],
        input_types={"invokeIntent": "(intent: str, slots: dict)"},
        output_types={"invokeIntent": "VoiceResponse"}
    ))
    architecture.add_component(voice)

    # API Gateway (Gateway)
    gateway = Component("API Gateway", ComponentType.GATEWAY)
    gateway.add_responsibility("Route requests to internal services")
    gateway.add_responsibility("Enforce rate limits and request validation")
    gateway.add_responsibility("Perform token verification (cross-cutting security)")
    gateway.set_interface(ComponentInterface(
        name="GatewayAPI",
        methods=["routeRequest"],
        input_types={"routeRequest": "(path: str, method: str, token: str, payload: dict)"},
        output_types={"routeRequest": "HTTPResponse"}
    ))
    architecture.add_component(gateway)

    # Identity Service (Service)
    identity = Component("Identity Service", ComponentType.SERVICE)
    identity.add_responsibility("Authenticate users (OAuth2/OIDC)")
    identity.add_responsibility("Authorize actions (RBAC/ABAC decisions)")
    identity.add_responsibility("Issue and validate tokens")
    identity.set_interface(ComponentInterface(
        name="IdentityAPI",
        methods=["validateToken", "authorize", "issueToken"],
        input_types={
            "validateToken": "(token: str)",
            "authorize": "(userId: str, action: str, resource: str)",
            "issueToken": "(userId: str)"
        },
        output_types={
            "validateToken": "bool",
            "authorize": "bool",
            "issueToken": "str"
        }
    ))
    architecture.add_component(identity)

    # Device Manager Service (Service)
    device_mgr = Component("Device Manager Service", ComponentType.SERVICE)
    device_mgr.add_responsibility("Maintain device registry and ownership mapping")
    device_mgr.add_responsibility("Send commands and track device state")
    device_mgr.add_responsibility("Publish device events to Event Bus")
    device_mgr.set_interface(ComponentInterface(
        name="DeviceManagerAPI",
        methods=["sendDeviceCommand", "getDeviceState", "registerDevice"],
        input_types={
            "sendDeviceCommand": "(deviceId: str, command: str)",
            "getDeviceState": "(deviceId: str)",
            "registerDevice": "(deviceInfo: dict)"
        },
        output_types={
            "sendDeviceCommand": "CommandResult",
            "getDeviceState": "DeviceState",
            "registerDevice": "bool"
        }
    ))
    architecture.add_component(device_mgr)

    # Automation Service (Service)
    automation = Component("Automation Service", ComponentType.SERVICE)
    automation.add_responsibility("Manage rules and schedules")
    automation.add_responsibility("Subscribe to events and trigger actions")
    automation.add_responsibility("Issue commands via Device Manager")
    automation.set_interface(ComponentInterface(
        name="AutomationAPI",
        methods=["createRule", "evaluateEvent", "triggerAction"],
        input_types={
            "createRule": "(rule: dict)",
            "evaluateEvent": "(event: dict)",
            "triggerAction": "(action: dict)"
        },
        output_types={
            "createRule": "bool",
            "evaluateEvent": "bool",
            "triggerAction": "bool"
        }
    ))
    architecture.add_component(automation)

    # Notification Service (Service)
    notification = Component("Notification Service", ComponentType.SERVICE)
    notification.add_responsibility("Send alerts (push/email/SMS)")
    notification.add_responsibility("Manage notification preferences")
    notification.add_responsibility("Subscribe to security/device events")
    notification.set_interface(ComponentInterface(
        name="NotificationAPI",
        methods=["sendAlert", "updatePreferences"],
        input_types={
            "sendAlert": "(userId: str, alert: dict)",
            "updatePreferences": "(userId: str, prefs: dict)"
        },
        output_types={
            "sendAlert": "bool",
            "updatePreferences": "bool"
        }
    ))
    architecture.add_component(notification)

    # Event Bus / Broker (Broker)
    broker = Component("Event Bus", ComponentType.BROKER)
    broker.add_responsibility("Publish/subscribe for device events")
    broker.add_responsibility("Buffer bursts and support retries")
    broker.add_responsibility("Decouple producers and consumers")
    architecture.add_component(broker)

    # Databases
    user_db = Component("User DB", ComponentType.DATABASE)
    user_db.add_responsibility("Persist users, roles, permissions")
    user_db.add_responsibility("Support indexing and queries")
    user_db.add_responsibility("Audit/security metadata")
    architecture.add_component(user_db)

    device_db = Component("Device DB", ComponentType.DATABASE)
    device_db.add_responsibility("Persist device registry and last-known state")
    device_db.add_responsibility("Support queries for device ownership/state")
    device_db.add_responsibility("Store device metadata")
    architecture.add_component(device_db)

    rules_db = Component("Rules DB", ComponentType.DATABASE)
    rules_db.add_responsibility("Persist automation rules and schedules")
    rules_db.add_responsibility("Support versioning of rules")
    rules_db.add_responsibility("Support queries by deviceId/trigger")
    architecture.add_component(rules_db)

    notif_db = Component("Notif DB", ComponentType.DATABASE)
    notif_db.add_responsibility("Persist notification preferences and delivery logs")
    notif_db.add_responsibility("Support audit trails for alerts")
    notif_db.add_responsibility("Enable retry tracking")
    architecture.add_component(notif_db)

    # IoT Hub / Devices
    iot = Component("IoT Hub / Devices", ComponentType.IOT)
    iot.add_responsibility("Maintain device connectivity")
    iot.add_responsibility("Receive commands and send telemetry/ACKs")
    iot.add_responsibility("Support MQTT/WebSocket channels")
    architecture.add_component(iot)

    # ========================================================================
    # CONNECTORS
    # ========================================================================

    # Clients -> API Gateway
    architecture.add_connector(Connector(
        name="Mobile App to API Gateway",
        connector_type=ConnectorType.REST_API,
        source_component="Mobile App",
        target_component="API Gateway",
        protocol="HTTPS",
        data_format="JSON",
        properties={"sync": "true", "auth": "Bearer Token"}
    ))
    architecture.add_connector(Connector(
        name="Web App to API Gateway",
        connector_type=ConnectorType.REST_API,
        source_component="Web App",
        target_component="API Gateway",
        protocol="HTTPS",
        data_format="JSON",
        properties={"sync": "true", "auth": "Bearer Token"}
    ))
    architecture.add_connector(Connector(
        name="Voice Assistant to API Gateway",
        connector_type=ConnectorType.REST_API,
        source_component="Voice Assistant",
        target_component="API Gateway",
        protocol="HTTPS (Webhook)",
        data_format="JSON",
        properties={"sync": "true"}
    ))

    # Gateway -> Identity / Services
    architecture.add_connector(Connector(
        name="API Gateway to Identity Service",
        connector_type=ConnectorType.REST_API,
        source_component="API Gateway",
        target_component="Identity Service",
        protocol="HTTPS/mTLS",
        data_format="JSON",
        properties={"timeout": "2s", "purpose": "validate+authorize"}
    ))
    architecture.add_connector(Connector(
        name="API Gateway to Device Manager",
        connector_type=ConnectorType.REST_API,
        source_component="API Gateway",
        target_component="Device Manager Service",
        protocol="HTTPS/mTLS",
        data_format="JSON",
        properties={"timeout": "2s"}
    ))
    architecture.add_connector(Connector(
        name="API Gateway to Automation Service",
        connector_type=ConnectorType.REST_API,
        source_component="API Gateway",
        target_component="Automation Service",
        protocol="HTTPS/mTLS",
        data_format="JSON",
        properties={"timeout": "3s"}
    ))
    architecture.add_connector(Connector(
        name="API Gateway to Notification Service",
        connector_type=ConnectorType.REST_API,
        source_component="API Gateway",
        target_component="Notification Service",
        protocol="HTTPS/mTLS",
        data_format="JSON",
        properties={"timeout": "3s"}
    ))

    # Service -> DB connections
    architecture.add_connector(Connector(
        name="Identity Service to User DB",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Identity Service",
        target_component="User DB",
        protocol="PostgreSQL",
        data_format="SQL",
        properties={"ssl": "true", "pool": "10"}
    ))
    architecture.add_connector(Connector(
        name="Device Manager to Device DB",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Device Manager Service",
        target_component="Device DB",
        protocol="SQL/NoSQL",
        data_format="Rows/Documents",
        properties={"pool": "20"}
    ))
    architecture.add_connector(Connector(
        name="Automation Service to Rules DB",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Automation Service",
        target_component="Rules DB",
        protocol="SQL/NoSQL",
        data_format="Rows/Documents",
        properties={"pool": "10"}
    ))
    architecture.add_connector(Connector(
        name="Notification Service to Notif DB",
        connector_type=ConnectorType.DATABASE_CONNECTION,
        source_component="Notification Service",
        target_component="Notif DB",
        protocol="SQL/NoSQL",
        data_format="Rows/Documents",
        properties={"pool": "10"}
    ))

    # Event Bus (Pub/Sub) connectors
    architecture.add_connector(Connector(
        name="Device Manager publishes events",
        connector_type=ConnectorType.EVENT_BUS,
        source_component="Device Manager Service",
        target_component="Event Bus",
        protocol="MQTT/AMQP",
        data_format="JSON (versioned events)",
        properties={"mode": "async", "topic": "device.events"}
    ))
    architecture.add_connector(Connector(
        name="Automation subscribes to events",
        connector_type=ConnectorType.EVENT_BUS,
        source_component="Event Bus",
        target_component="Automation Service",
        protocol="MQTT/AMQP",
        data_format="JSON",
        properties={"mode": "async", "topic": "device.events"}
    ))
    architecture.add_connector(Connector(
        name="Notification subscribes to events",
        connector_type=ConnectorType.EVENT_BUS,
        source_component="Event Bus",
        target_component="Notification Service",
        protocol="MQTT/AMQP",
        data_format="JSON",
        properties={"mode": "async", "topic": "alerts.events"}
    ))

    # Realtime IoT connector
    architecture.add_connector(Connector(
        name="Device Manager to IoT Hub/Devices",
        connector_type=ConnectorType.REALTIME_IOT,
        source_component="Device Manager Service",
        target_component="IoT Hub / Devices",
        protocol="MQTT/WebSocket",
        data_format="Binary/JSON",
        properties={"realtime": "true", "qos": "1"}
    ))

    # ========================================================================
    # DESCRIBE ARCHITECTURE
    # ========================================================================

    architecture.describe()
    architecture.ascii_view()

    # ========================================================================
    # KEY CONCEPTS
    # ========================================================================

    print("\n" + "=" * 70)
    print("KEY CONCEPTS: Components and Connectors (Smart Home)")
    print("=" * 70)
    print("""
COMPONENTS:
  • Computational units that encapsulate functionality
  • Have clear responsibilities and interfaces
  • Examples: API Gateway, Device Manager, Identity Service, Event Bus, Databases

CONNECTORS:
  • Communication mechanisms between components
  • Can be synchronous (REST/HTTPS) or asynchronous (Pub/Sub, MQTT)
  • Examples: REST API, Event Bus (Pub/Sub), Database connection, MQTT/WebSocket

ARCHITECTURE = COMPONENTS + CONNECTORS:
  • Components define WHAT exists in the system
  • Connectors define HOW components communicate
  • Together they define the system architecture

GOOD PRACTICE:
  • Keep gateway thin (routing, policy enforcement) to avoid 'God Component'
  • Use pub/sub to decouple services and improve scalability
  • Define versioned event contracts to avoid breaking consumers
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_components_and_connectors_smart_home()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
✓ Components are computational units with responsibilities and interfaces
✓ Connectors define how components communicate (sync + async)
✓ Architecture = Components + Connectors
✓ Interfaces hide implementation details and support replacement/testing
✓ Different connector types support different runtime needs
✓ Good architecture keeps boundaries clear and connectors appropriate
    """)

from enum import Enum
import enum


class OrderStatus(str,Enum):
    created = "created"
    assigned = "assigned"
    picked = "picked"
    in_transit = "in_transit"
    delivered = "delivered"

class UserRole(enum.Enum):
    admin = "admin"
    customer = "customer"
    agent = "agent"

class OrderUpdateStatus(enum.Enum):
    created = "created"
    assigned = "assigned"
    picked = "picked"
    in_transit = "in_transit"
    delivered = "delivered"

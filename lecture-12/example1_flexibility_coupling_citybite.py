#!/usr/bin/env python3
"""
CityBite — coupling vs port/adapter (Lecture 12).

Run: python3 example1_flexibility_coupling_citybite.py

Shows why a concrete import blocks extracting Payment into a service later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


# --- Tight coupling: OrderService knows Stripe-shaped details ---


class StripePaymentGateway:
    """Vendor SDK stand-in."""

    def charge_card(self, cents: int, stripe_customer_id: str) -> str:
        return f"ch_{stripe_customer_id}_{cents}"


class OrderServiceTight:
    def __init__(self) -> None:
        self._gw = StripePaymentGateway()

    def checkout(self, cents: int, stripe_customer_id: str) -> str:
        # Hidden coupling: any new gateway requires editing this class.
        return self._gw.charge_card(cents, stripe_customer_id)


# --- Looser: core depends on a port; adapter wraps Stripe ---


@runtime_checkable
class PaymentPort(Protocol):
    def authorize_payment(self, cents: int, customer_ref: str) -> str: ...


class StripePaymentAdapter:
    def __init__(self, inner: StripePaymentGateway) -> None:
        self._inner = inner

    def authorize_payment(self, cents: int, customer_ref: str) -> str:
        return self._inner.charge_card(cents, customer_ref)


@dataclass
class OrderServiceLoose:
    payments: PaymentPort

    def checkout(self, cents: int, customer_ref: str) -> str:
        return self.payments.authorize_payment(cents, customer_ref)


def main() -> None:
    tight = OrderServiceTight()
    print("Tight:", tight.checkout(1299, "cus_abc"))

    loose = OrderServiceLoose(payments=StripePaymentAdapter(StripePaymentGateway()))
    print("Loose:", loose.checkout(1299, "cus_abc"))
    print(
        "\nFlexibility lesson: OrderServiceLoose only knows PaymentPort — "
        "you can swap in FakePayment for tests or HTTP adapter for microservice."
    )


if __name__ == "__main__":
    main()

from decimal import Decimal

from django.db import models


class Account(models.Model):
    class Kind(models.TextChoices):
        ISA = "isa", "Stocks ISA"
        INVEST = "invest", "Invest"
        OTHER = "other", "Other"

    name = models.CharField(max_length=100, unique=True)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.OTHER)
    base_currency = models.CharField(max_length=3, default="GBP")

    def __str__(self):
        return self.name


class Trade(models.Model):
    class Side(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trades")
    external_id = models.CharField(max_length=64, help_text="Broker's order/row ID, used to skip duplicates")
    executed_at = models.DateTimeField()
    side = models.CharField(max_length=4, choices=Side.choices)
    order_type = models.CharField(max_length=40, help_text="Raw broker action, e.g. 'Market buy', 'Stop sell'")
    ticker = models.CharField(max_length=20)
    isin = models.CharField(max_length=12, blank=True)
    name = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=10)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    price_currency = models.CharField(max_length=3)
    total = models.DecimalField(max_digits=14, decimal_places=2, help_text="Order value in account currency")
    realised_result = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, help_text="Broker-reported P&L on sells"
    )
    fx_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    class Meta:
        ordering = ["-executed_at"]
        constraints = [
            models.UniqueConstraint(fields=["account", "external_id"], name="unique_trade_per_account"),
        ]

    def __str__(self):
        return f"{self.executed_at:%Y-%m-%d} {self.side} {self.quantity} {self.ticker}"


class CashMovement(models.Model):
    class Kind(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        DIVIDEND = "dividend", "Dividend"
        INTEREST = "interest", "Interest"
        OTHER = "other", "Other"

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cash_movements")
    external_id = models.CharField(max_length=64)
    executed_at = models.DateTimeField()
    kind = models.CharField(max_length=12, choices=Kind.choices)
    raw_action = models.CharField(max_length=60)
    ticker = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["-executed_at"]
        constraints = [
            models.UniqueConstraint(fields=["account", "external_id"], name="unique_cash_per_account"),
        ]

    def __str__(self):
        return f"{self.executed_at:%Y-%m-%d} {self.kind} {self.amount}"

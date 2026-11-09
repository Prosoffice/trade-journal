from decimal import Decimal

from django.db.models import Count, Q, QuerySet, Sum
from django.db.models.functions import TruncMonth

from .models import CashMovement, Trade


def summary(trades: QuerySet[Trade], cash: QuerySet[CashMovement]) -> dict:
    closed = trades.filter(side=Trade.Side.SELL, realised_result__isnull=False)
    totals = closed.aggregate(
        realised=Sum("realised_result"),
        wins=Count("id", filter=Q(realised_result__gt=0)),
        losses=Count("id", filter=Q(realised_result__lt=0)),
    )
    zero = Decimal("0")
    return {
        "trade_count": trades.count(),
        "realised": totals["realised"] or zero,
        "wins": totals["wins"],
        "losses": totals["losses"],
        "fx_fees": trades.aggregate(v=Sum("fx_fee"))["v"] or zero,
        "dividends": cash.filter(kind=CashMovement.Kind.DIVIDEND).aggregate(v=Sum("amount"))["v"] or zero,
        "interest": cash.filter(kind=CashMovement.Kind.INTEREST).aggregate(v=Sum("amount"))["v"] or zero,
    }


def realised_by_ticker(trades: QuerySet[Trade]):
    return (
        trades.filter(side=Trade.Side.SELL, realised_result__isnull=False)
        .values("ticker", "name")
        .annotate(realised=Sum("realised_result"), sells=Count("id"))
        .order_by("-realised")
    )


def realised_by_month(trades: QuerySet[Trade]):
    return (
        trades.filter(side=Trade.Side.SELL, realised_result__isnull=False)
        .annotate(month=TruncMonth("executed_at"))
        .values("month")
        .annotate(realised=Sum("realised_result"), sells=Count("id"))
        .order_by("month")
    )

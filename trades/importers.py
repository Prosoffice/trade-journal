"""Importer for Trading 212 history exports (CSV)."""

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import Account, CashMovement, Trade


@dataclass
class ImportResult:
    trades_created: int = 0
    cash_created: int = 0
    skipped_duplicates: int = 0


def _decimal(value: str | None, default: Decimal | None = None) -> Decimal | None:
    if value is None or value.strip() == "":
        return default
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return default


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip())
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _row_id(row: dict) -> str:
    """Use the broker's ID; rows without one (e.g. dividends) get a stable hash."""
    if row.get("ID"):
        return row["ID"].strip()
    fingerprint = "|".join(row.get(k, "") for k in ("Action", "Time (UTC)", "Ticker", "Total"))
    return "h-" + hashlib.sha1(fingerprint.encode()).hexdigest()[:20]


def _cash_kind(action: str) -> str:
    lowered = action.lower()
    if lowered == "deposit":
        return CashMovement.Kind.DEPOSIT
    if lowered == "withdrawal":
        return CashMovement.Kind.WITHDRAWAL
    if lowered.startswith("dividend"):
        return CashMovement.Kind.DIVIDEND
    if "interest" in lowered:
        return CashMovement.Kind.INTEREST
    return CashMovement.Kind.OTHER


def import_trading212_csv(file_obj, account: Account) -> ImportResult:
    """Import every row of a Trading 212 export. Safe to re-run on overlapping exports."""
    result = ImportResult()
    reader = csv.DictReader(file_obj)

    with transaction.atomic():
        for row in reader:
            action = (row.get("Action") or "").strip()
            if not action:
                continue
            external_id = _row_id(row)
            lowered = action.lower()

            if lowered.endswith("buy") or lowered.endswith("sell"):
                _, created = Trade.objects.get_or_create(
                    account=account,
                    external_id=external_id,
                    defaults=dict(
                        executed_at=_timestamp(row["Time (UTC)"]),
                        side=Trade.Side.BUY if lowered.endswith("buy") else Trade.Side.SELL,
                        order_type=action,
                        ticker=row.get("Ticker", "").strip(),
                        isin=row.get("ISIN", "").strip(),
                        name=row.get("Name", "").strip(),
                        quantity=_decimal(row.get("No. of shares"), Decimal("0")),
                        price=_decimal(row.get("Price / share"), Decimal("0")),
                        price_currency=(row.get("Currency (Price / share)") or "").strip(),
                        total=_decimal(row.get("Total"), Decimal("0")),
                        realised_result=_decimal(row.get("Result")),
                        fx_fee=_decimal(row.get("Currency conversion fee"), Decimal("0")),
                    ),
                )
                if created:
                    result.trades_created += 1
                else:
                    result.skipped_duplicates += 1
            else:
                _, created = CashMovement.objects.get_or_create(
                    account=account,
                    external_id=external_id,
                    defaults=dict(
                        executed_at=_timestamp(row["Time (UTC)"]),
                        kind=_cash_kind(action),
                        raw_action=action,
                        ticker=(row.get("Ticker") or "").strip(),
                        amount=_decimal(row.get("Total"), Decimal("0")),
                    ),
                )
                if created:
                    result.cash_created += 1
                else:
                    result.skipped_duplicates += 1

    return result

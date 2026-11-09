from decimal import Decimal
from pathlib import Path

from django.test import TestCase
from django.urls import reverse

from .analytics import realised_by_ticker, summary
from .importers import import_trading212_csv
from .models import Account, CashMovement, Trade

SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "sample_export.csv"


class ImportTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(name="Sample ISA", kind=Account.Kind.ISA)

    def _import(self):
        with SAMPLE.open(encoding="utf-8-sig", newline="") as fh:
            return import_trading212_csv(fh, self.account)

    def test_imports_trades_and_cash(self):
        result = self._import()
        self.assertEqual(result.trades_created, 4)
        self.assertEqual(result.cash_created, 4)
        self.assertEqual(Trade.objects.filter(side=Trade.Side.SELL).count(), 2)
        self.assertEqual(CashMovement.objects.filter(kind=CashMovement.Kind.DIVIDEND).count(), 1)

    def test_reimport_skips_duplicates(self):
        self._import()
        result = self._import()
        self.assertEqual(result.trades_created, 0)
        self.assertEqual(result.cash_created, 0)
        self.assertEqual(result.skipped_duplicates, 8)

    def test_summary_numbers(self):
        self._import()
        data = summary(Trade.objects.all(), CashMovement.objects.all())
        self.assertEqual(data["realised"], Decimal("20.00"))
        self.assertEqual((data["wins"], data["losses"]), (1, 1))
        self.assertEqual(data["dividends"], Decimal("0.80"))
        self.assertEqual(data["fx_fees"], Decimal("1.47"))
        tickers = {row["ticker"]: row["realised"] for row in realised_by_ticker(Trade.objects.all())}
        self.assertEqual(tickers, {"ACME": Decimal("40.00"), "GLBX": Decimal("-20.00")})

    def test_dashboard_renders(self):
        self._import()
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "ACME")
        self.assertContains(response, "£20.00")

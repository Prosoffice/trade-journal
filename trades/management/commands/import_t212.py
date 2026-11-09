from django.core.management.base import BaseCommand

from trades.importers import import_trading212_csv
from trades.models import Account


class Command(BaseCommand):
    help = "Import a Trading 212 history export (CSV) into an account."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--account", required=True, help="Account name, created if it doesn't exist")
        parser.add_argument("--kind", choices=[k for k, _ in Account.Kind.choices], default=Account.Kind.OTHER)

    def handle(self, *args, **options):
        account, _ = Account.objects.get_or_create(name=options["account"], defaults={"kind": options["kind"]})
        with open(options["csv_path"], encoding="utf-8-sig", newline="") as fh:
            result = import_trading212_csv(fh, account)
        self.stdout.write(
            self.style.SUCCESS(
                f"{account}: {result.trades_created} trades, {result.cash_created} cash rows, "
                f"{result.skipped_duplicates} duplicates skipped"
            )
        )

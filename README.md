# Trade Journal

A self-hosted trading journal for retail investors who use Trading 212. Import your history exports and see where your money actually came from: realised P&L by ticker and by month, win/loss counts, dividends, interest and the FX fees you've been paying.

I built it because reviewing my own two years of trades by hand, across an ISA and an Invest account, was slow and error-prone. This does the first pass for me.

## Features

- Import Trading 212 CSV exports, from the web UI or the command line
- Multiple accounts (e.g. Stocks ISA and Invest), each imported separately
- Safe re-imports: overlapping exports are de-duplicated using the broker's row IDs
- Dashboard: realised P&L, wins/losses, dividends, interest, FX fees
- Realised P&L by ticker and by month
- Django admin for browsing and filtering every trade and cash movement

## Built with

Python 3.12+, Django 5.1, SQLite by default (Postgres via `DATABASE_URL`).

## Running it locally

```bash
git clone https://github.com/Prosoffice/trade-journal.git
cd trade-journal
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional: defaults work for local use
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000, create an account in the admin, then use **Import CSV**.

Or import from the command line:

```bash
python manage.py import_t212 path/to/export.csv --account "Stocks ISA" --kind isa
```

To try it without your own data, import the made-up sample:

```bash
python manage.py import_t212 sample_data/sample_export.csv --account Sample --kind isa
```

## Getting your export

In the Trading 212 app: **History → Export**, choose a date range (max 12 months per file) and CSV. Repeat for each account. Overlapping ranges are fine.

## Your data stays yours

The journal runs locally and nothing is sent anywhere. `.gitignore` excludes every CSV except the made-up file in `sample_data/`, so real exports can't be committed by accident.

## Tests

```bash
python manage.py test
```

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Licence

MIT. See [LICENSE](LICENSE).

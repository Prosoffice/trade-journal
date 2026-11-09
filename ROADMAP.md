# Roadmap

Rough order of what I plan to build next.

## Positions and cost basis
- [ ] Compute positions and cost basis myself (FIFO lots) instead of relying only on the broker's `Result` column
- [ ] Holding period per closed lot, and an open-positions view
- [ ] Merge partial fills (same ticker, side and second) into a single order

## Journaling
- [ ] Notes on any trade: thesis, what I expected, exit reason, reflection
- [ ] Tags (e.g. earnings play, averaging down, profit taking, panic sell) and a conviction score
- [ ] Filter the dashboard by tag to see which kinds of decisions actually make money

## Insights
- [ ] Cumulative P&L chart and monthly P&L chart
- [ ] Holding-period distribution, and win rate and average P&L by holding period
- [ ] Average win vs average loss, biggest drawdown per position
- [ ] FX fee breakdown by month and by currency
- [ ] Date-range and account filters on every view

## Data
- [ ] Export journal entries and stats to CSV
- [ ] Importer interface so other brokers' exports can be added
- [ ] Manual price entry (then an optional price feed) for open-position values

## Engineering
- [ ] GitHub Actions: tests and linting on every push
- [ ] Docker Compose setup with Postgres
- [ ] Type hints and docstrings across the importer and analytics

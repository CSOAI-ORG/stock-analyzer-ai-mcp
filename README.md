# Stock Analyzer Ai

> By [MEOK AI Labs](https://meok.ai) — Analyze stocks with financial ratios, comparisons, and sector performance data.

MEOK AI Labs — stock-analyzer-ai-mcp MCP Server. Analyze stocks with basic metrics and trend summaries.

## Installation

```bash
pip install stock-analyzer-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install stock-analyzer-ai-mcp
```

## Tools

### `analyze_stock`
Analyze a stock with key metrics and generate a buy/hold/sell recommendation.

**Parameters:**
- `ticker` (str)
- `price` (float)
- `pe` (float)
- `eps` (float)
- `dividend_yield` (float)
- `market_cap_b` (float)
- `revenue_growth` (float)

### `calculate_ratios`
Calculate key financial ratios: P/E, P/B, P/S, dividend yield, debt-to-equity, and more.

**Parameters:**
- `price` (float)
- `eps` (float)
- `book_value` (float)
- `revenue_per_share` (float)
- `dividend` (float)
- `shares_outstanding_m` (float)
- `total_debt_b` (float)
- `total_equity_b` (float)

### `compare_stocks`
Compare multiple stocks side by side. Each item needs 'ticker', 'price', 'pe', and optionally 'growth', 'dividend_yield'.

**Parameters:**
- `stocks` (str)

### `get_sector_performance`
Get sector performance data and representative tickers. Leave sector empty for all sectors.

**Parameters:**
- `sector` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/stock-analyzer-ai-mcp](https://github.com/CSOAI-ORG/stock-analyzer-ai-mcp)
- **PyPI**: [pypi.org/project/stock-analyzer-ai-mcp](https://pypi.org/project/stock-analyzer-ai-mcp/)

## License

MIT — MEOK AI Labs

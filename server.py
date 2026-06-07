#!/usr/bin/env python3
"""
MEOK AI Labs — stock-analyzer-ai-mcp MCP Server. Analyze stocks with basic metrics and trend summaries."""

import json
from datetime import datetime, timezone
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
import sys, os
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

SECTOR_DATA = {
    "technology": {"avg_pe": 28, "avg_growth": 15, "risk": "high", "tickers": ["AAPL", "MSFT", "GOOG", "NVDA", "META"]},
    "healthcare": {"avg_pe": 22, "avg_growth": 10, "risk": "medium", "tickers": ["JNJ", "UNH", "PFE", "ABBV", "MRK"]},
    "finance": {"avg_pe": 14, "avg_growth": 8, "risk": "medium", "tickers": ["JPM", "BAC", "GS", "V", "MA"]},
    "consumer": {"avg_pe": 24, "avg_growth": 7, "risk": "medium", "tickers": ["AMZN", "WMT", "PG", "KO", "PEP"]},
    "energy": {"avg_pe": 12, "avg_growth": 5, "risk": "high", "tickers": ["XOM", "CVX", "COP", "SLB", "EOG"]},
    "utilities": {"avg_pe": 18, "avg_growth": 3, "risk": "low", "tickers": ["NEE", "DUK", "SO", "D", "AEP"]},
    "real_estate": {"avg_pe": 35, "avg_growth": 4, "risk": "medium", "tickers": ["PLD", "AMT", "CCI", "SPG", "O"]},
}

mcp = FastMCP("stock-analyzer-ai", instructions="Analyze stocks with financial ratios, comparisons, and sector performance data.")


@mcp.tool()
def analyze_stock(ticker: str, price: float, pe: float = 0, eps: float = 0, dividend_yield: float = 0, market_cap_b: float = 0, revenue_growth: float = 0, api_key: str = "") -> str:
    """Analyze a stock with key metrics and generate a buy/hold/sell recommendation."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    # Determine PE if not provided
    if pe <= 0 and eps > 0:
        pe = round(price / eps, 2)

    # Rating logic
    signals = []
    score = 0
    if pe > 0:
        if pe < 15: signals.append("Low P/E (value)"); score += 2
        elif pe < 25: signals.append("Moderate P/E"); score += 1
        else: signals.append("High P/E (growth/overvalued)"); score -= 1

    if dividend_yield > 3: signals.append("Strong dividend"); score += 1
    elif dividend_yield > 1: signals.append("Moderate dividend"); score += 0.5

    if revenue_growth > 20: signals.append("High growth"); score += 2
    elif revenue_growth > 10: signals.append("Moderate growth"); score += 1
    elif revenue_growth < 0: signals.append("Revenue declining"); score -= 2

    cap_class = "mega-cap" if market_cap_b > 200 else "large-cap" if market_cap_b > 10 else "mid-cap" if market_cap_b > 2 else "small-cap"
    if market_cap_b > 0:
        signals.append(f"{cap_class}")

    rating = "strong buy" if score >= 4 else "buy" if score >= 2 else "hold" if score >= 0 else "sell"

    return json.dumps({
        "ticker": ticker.upper(),
        "price": price,
        "pe_ratio": pe,
        "eps": eps,
        "dividend_yield": f"{dividend_yield}%",
        "revenue_growth": f"{revenue_growth}%",
        "market_cap": f"${market_cap_b}B" if market_cap_b > 0 else "N/A",
        "cap_classification": cap_class if market_cap_b > 0 else "unknown",
        "signals": signals,
        "rating": rating,
        "confidence": "high" if len(signals) >= 4 else "medium" if len(signals) >= 2 else "low",
    }, indent=2)


@mcp.tool()
def calculate_ratios(price: float, eps: float = 0, book_value: float = 0, revenue_per_share: float = 0, dividend: float = 0, shares_outstanding_m: float = 0, total_debt_b: float = 0, total_equity_b: float = 0, api_key: str = "") -> str:
    """Calculate key financial ratios: P/E, P/B, P/S, dividend yield, debt-to-equity, and more."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    ratios = {}
    if eps > 0:
        ratios["pe_ratio"] = round(price / eps, 2)
        ratios["earnings_yield"] = f"{round(eps / price * 100, 2)}%"
    if book_value > 0:
        ratios["pb_ratio"] = round(price / book_value, 2)
    if revenue_per_share > 0:
        ratios["ps_ratio"] = round(price / revenue_per_share, 2)
    if dividend > 0:
        ratios["dividend_yield"] = f"{round(dividend / price * 100, 2)}%"
        if eps > 0:
            ratios["payout_ratio"] = f"{round(dividend / eps * 100, 1)}%"
    if total_equity_b > 0 and total_debt_b > 0:
        ratios["debt_to_equity"] = round(total_debt_b / total_equity_b, 2)
    if shares_outstanding_m > 0:
        ratios["market_cap"] = f"${round(price * shares_outstanding_m / 1000, 2)}B"

    # Valuation assessment
    pe = ratios.get("pe_ratio", 0)
    pb = ratios.get("pb_ratio", 0)
    assessment = "undervalued" if pe > 0 and pe < 12 and pb > 0 and pb < 1.5 else \
                 "fairly valued" if pe > 0 and pe < 25 else \
                 "overvalued" if pe > 30 else "insufficient data"

    return json.dumps({"price": price, "ratios": ratios, "valuation_assessment": assessment}, indent=2)


@mcp.tool()
def compare_stocks(stocks: list[dict], api_key: str = "") -> str:
    """Compare multiple stocks side by side. Each item needs 'ticker', 'price', 'pe', and optionally 'growth', 'dividend_yield'."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    comparison = []
    for stock in stocks:
        ticker = stock.get("ticker", "???")
        price = stock.get("price", 0)
        pe = stock.get("pe", 0)
        growth = stock.get("growth", 0)
        div_yield = stock.get("dividend_yield", 0)

        score = 0
        if 0 < pe < 15: score += 3
        elif 0 < pe < 25: score += 1
        elif pe >= 25: score -= 1
        if growth > 15: score += 2
        elif growth > 5: score += 1
        if div_yield > 2: score += 1

        comparison.append({
            "ticker": ticker.upper(),
            "price": price,
            "pe": pe,
            "growth": f"{growth}%",
            "dividend_yield": f"{div_yield}%",
            "composite_score": score,
        })

    # Rank by composite score
    comparison.sort(key=lambda x: -x["composite_score"])
    for i, c in enumerate(comparison):
        c["rank"] = i + 1

    return json.dumps({
        "comparison": comparison,
        "top_pick": comparison[0]["ticker"] if comparison else None,
        "note": "Composite score based on P/E, growth, and dividend yield. Not financial advice.",
    }, indent=2)


@mcp.tool()
def get_sector_performance(sector: str = "", api_key: str = "") -> str:
    """Get sector performance data and representative tickers. Leave sector empty for all sectors."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    if sector and sector.lower() in SECTOR_DATA:
        data = SECTOR_DATA[sector.lower()]
        return json.dumps({
            "sector": sector.lower(),
            "average_pe": data["avg_pe"],
            "average_growth": f"{data['avg_growth']}%",
            "risk_level": data["risk"],
            "representative_tickers": data["tickers"],
        }, indent=2)

    # All sectors summary
    sectors = []
    for name, data in sorted(SECTOR_DATA.items(), key=lambda x: -x[1]["avg_growth"]):
        sectors.append({
            "sector": name,
            "avg_pe": data["avg_pe"],
            "avg_growth": f"{data['avg_growth']}%",
            "risk": data["risk"],
            "top_tickers": data["tickers"][:3],
        })

    return json.dumps({
        "sectors": sectors,
        "highest_growth": sectors[0]["sector"] if sectors else None,
        "lowest_risk": min(SECTOR_DATA, key=lambda k: {"low": 0, "medium": 1, "high": 2}[SECTOR_DATA[k]["risk"]]),
    }, indent=2)


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/00wfZjcgAeUW4c5cyQ8k90K"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}

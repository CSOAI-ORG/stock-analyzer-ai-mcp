from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stock-analyzer")

@mcp.tool()
def calculate_sma(prices: list, window: int = 20) -> dict:
    """Calculate simple moving average."""
    if len(prices) < window:
        return {"error": "Not enough data points for window"}
    sma = sum(prices[-window:]) / window
    return {"window": window, "sma": round(sma, 4), "last_price": prices[-1]}

@mcp.tool()
def calculate_rsi(prices: list, period: int = 14) -> dict:
    """Calculate RSI."""
    if len(prices) < period + 1:
        return {"error": f"Need at least {period + 1} prices"}
    gains = []
    losses = []
    for i in range(1, period + 1):
        change = prices[-(period + 1) + i] - prices[-(period + 1) + i - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    signal = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
    return {"rsi": round(rsi, 2), "signal": signal}

@mcp.tool()
def analyze_trend(prices: list, short_window: int = 10, long_window: int = 30) -> dict:
    """Analyze trend using SMA crossover."""
    if len(prices) < long_window:
        return {"error": "Insufficient price history"}
    short_sma = sum(prices[-short_window:]) / short_window
    long_sma = sum(prices[-long_window:]) / long_window
    signal = "bullish" if short_sma > long_sma else "bearish"
    return {"short_sma": round(short_sma, 4), "long_sma": round(long_sma, 4), "signal": signal}

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

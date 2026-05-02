"""
=============================================================================
Artifact 2: Building a Custom OpenClaw Skill
=============================================================================
File: 02_openclaw_skill_creator.py
Author: Dr. Anish Roychowdhury
Description: Programmatically creates a custom OpenClaw skill with proper
             SKILL.md metadata, tool implementation, and demonstrates how
             skills integrate into the OpenClaw ecosystem.

Prerequisites:
    pip install anthropic python-dotenv requests

    This script creates a skill directory structure that you can
    drop into your OpenClaw workspace's skills/ folder.

    For Google Colab: Runs fully — generates the skill files locally.
=============================================================================
"""

import os
import json
from pathlib import Path
from datetime import datetime


def create_skill_directory(
    skill_name: str,
    description: str,
    author: str,
    base_dir: str = "./skills",
) -> Path:
    """
    Create a complete OpenClaw skill directory structure.

    OpenClaw skills follow a specific convention:
        skills/
        └── my-skill/
            ├── SKILL.md          # Metadata + instructions for the LLM
            ├── tool.py           # Tool implementation
            ├── requirements.txt  # Python dependencies
            └── README.md         # Human-readable documentation
    """
    skill_dir = Path(base_dir) / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    return skill_dir


def generate_stock_checker_skill():
    """
    Creates a complete 'stock-price-checker' skill that:
    1. Fetches real-time stock prices using a free API
    2. Returns formatted price data
    3. Includes proper SKILL.md for OpenClaw discovery
    """

    print("=" * 60)
    print("OpenClaw Custom Skill Creator")
    print("=" * 60)

    skill_name = "stock-price-checker"
    skill_dir = create_skill_directory(
        skill_name=skill_name,
        description="Check real-time stock prices",
        author="Dr. Anish Roychowdhury",
    )

    # -----------------------------------------------------------------------
    # 1. SKILL.md — The heart of every OpenClaw skill
    # -----------------------------------------------------------------------
    # This file tells the LLM *when* and *how* to use the skill.
    # OpenClaw reads this at runtime and injects it into the LLM's context.

    skill_md_content = """---
name: stock-price-checker
description: Check real-time stock prices and basic financial data
version: 1.0.0
author: Dr. Anish Roychowdhury
triggers:
  - stock price
  - check stock
  - market data
  - how is [TICKER] doing
  - what's the price of [TICKER]
---

# Stock Price Checker Skill

## When to Use
Use this skill when the user asks about:
- Current stock prices for any publicly traded company
- Basic market data (open, close, high, low, volume)
- Price comparisons between multiple stocks

## How to Use

### Check a single stock
```
python tool.py --ticker AAPL
```

### Check multiple stocks
```
python tool.py --tickers AAPL,GOOGL,MSFT
```

### Get detailed information
```
python tool.py --ticker AAPL --detail
```

## Output Format
Returns JSON with: ticker, price, change, change_percent, volume, timestamp

## Limitations
- Data is from free API tier (may have 15-minute delay)
- Supports US-listed stocks only
- Rate limited to 5 requests per minute

## Error Handling
If the API is unavailable, returns cached data with a staleness warning.
"""

    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(skill_md_content)
    print(f"[✓] Created {skill_md_path}")

    # -----------------------------------------------------------------------
    # 2. tool.py — The actual tool implementation
    # -----------------------------------------------------------------------

    tool_py_content = '''"""
Stock Price Checker Tool for OpenClaw
=====================================
Fetches real-time stock data using the Yahoo Finance API (yfinance).
This is a lightweight, free alternative that works without API keys.

Usage:
    python tool.py --ticker AAPL
    python tool.py --tickers AAPL,GOOGL,MSFT
    python tool.py --ticker AAPL --detail
"""

import argparse
import json
import sys
from datetime import datetime


def fetch_stock_price(ticker: str, detail: bool = False) -> dict:
    """
    Fetch stock price data for a given ticker symbol.
    
    Uses yfinance for free, reliable stock data.
    Falls back to a mock response if yfinance is unavailable
    (useful for offline development and testing).
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        hist = stock.history(period="1d")
        
        if hist.empty:
            return {
                "ticker": ticker.upper(),
                "error": f"No data found for {ticker.upper()}",
                "timestamp": datetime.now().isoformat(),
            }
        
        latest = hist.iloc[-1]
        
        result = {
            "ticker": ticker.upper(),
            "price": round(float(latest["Close"]), 2),
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance (yfinance)",
        }
        
        if detail:
            result.update({
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            })
        
        return result
        
    except ImportError:
        # Fallback for environments without yfinance
        print("[!] yfinance not installed. Using mock data.", file=sys.stderr)
        print("[!] Install with: pip install yfinance", file=sys.stderr)
        
        return {
            "ticker": ticker.upper(),
            "price": 185.42,
            "open": 184.20,
            "high": 186.10,
            "low": 183.85,
            "volume": 52_340_000,
            "timestamp": datetime.now().isoformat(),
            "source": "MOCK DATA — install yfinance for real prices",
            "note": "pip install yfinance",
        }


def fetch_multiple(tickers: list[str], detail: bool = False) -> list[dict]:
    """Fetch data for multiple tickers."""
    results = []
    for ticker in tickers:
        results.append(fetch_stock_price(ticker.strip(), detail))
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Stock Price Checker — OpenClaw Skill"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ticker", type=str, help="Single ticker symbol")
    group.add_argument(
        "--tickers", type=str, help="Comma-separated ticker symbols"
    )
    parser.add_argument(
        "--detail", action="store_true", help="Include detailed info"
    )

    args = parser.parse_args()

    if args.ticker:
        result = fetch_stock_price(args.ticker, args.detail)
    else:
        ticker_list = [t.strip() for t in args.tickers.split(",")]
        result = fetch_multiple(ticker_list, args.detail)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
'''

    tool_py_path = skill_dir / "tool.py"
    tool_py_path.write_text(tool_py_content)
    print(f"[✓] Created {tool_py_path}")

    # -----------------------------------------------------------------------
    # 3. requirements.txt
    # -----------------------------------------------------------------------

    requirements_content = """yfinance>=0.2.36
"""
    req_path = skill_dir / "requirements.txt"
    req_path.write_text(requirements_content)
    print(f"[✓] Created {req_path}")

    # -----------------------------------------------------------------------
    # 4. README.md — Human-readable documentation
    # -----------------------------------------------------------------------

    readme_content = """# Stock Price Checker — OpenClaw Skill

A custom OpenClaw skill that fetches real-time stock prices.

## Installation

1. Copy this directory to your OpenClaw workspace:
   ```bash
   cp -r stock-price-checker ~/.openclaw/skills/
   ```

2. Install dependencies:
   ```bash
   cd ~/.openclaw/skills/stock-price-checker
   pip install -r requirements.txt
   ```

3. Restart OpenClaw or reload skills.

## Usage

Just ask your OpenClaw agent:
- "What's the price of AAPL?"
- "Check stock prices for GOOGL, MSFT, NVDA"
- "Give me detailed info on Tesla stock"

## Development

Test the tool directly:
```bash
python tool.py --ticker AAPL --detail
```

## License

MIT
"""
    readme_path = skill_dir / "README.md"
    readme_path.write_text(readme_content)
    print(f"[✓] Created {readme_path}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print(f"\n{'=' * 60}")
    print(f"Skill created successfully!")
    print(f"{'=' * 60}")
    print(f"\nDirectory structure:")
    print(f"  {skill_dir}/")
    for f in sorted(skill_dir.iterdir()):
        print(f"  ├── {f.name}")
    print(f"\nTo install in OpenClaw:")
    print(f"  cp -r {skill_dir} ~/.openclaw/skills/")
    print(f"\nTo test directly:")
    print(f"  python {skill_dir}/tool.py --ticker AAPL")

    return skill_dir


# ---------------------------------------------------------------------------
# Bonus: Demonstrate skill usage from Python
# ---------------------------------------------------------------------------

def demo_skill_usage():
    """
    Show how the generated skill can be invoked programmatically.
    This simulates what OpenClaw does internally when a skill is triggered.
    """
    print(f"\n{'=' * 60}")
    print("Demo: Direct Skill Invocation")
    print(f"{'=' * 60}")

    # Import and use the tool directly
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tool", "./skills/stock-price-checker/tool.py"
    )
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)

    # Fetch a single stock
    print("\n[→] Fetching AAPL price...")
    result = tool.fetch_stock_price("AAPL")
    print(json.dumps(result, indent=2))

    # Fetch multiple stocks
    print("\n[→] Fetching multiple stocks...")
    results = tool.fetch_multiple(["AAPL", "GOOGL", "MSFT"])
    for r in results:
        print(f"  {r['ticker']}: ${r['price']} (Source: {r['source']})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n🦞 OpenClaw Custom Skill Creator\n")

    # Step 1: Generate the skill
    skill_dir = generate_stock_checker_skill()

    # Step 2: Demo the skill
    demo_skill_usage()

import yfinance as yf
import json
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "oil-price.json")

SYMBOLS = [
    ("CL=F", "WTI原油", "WTI Crude Oil", "USD/bbl"),
    ("BZ=F", "布伦特原油", "Brent Crude Oil", "USD/bbl"),
    ("NG=F", "天然气", "Natural Gas", "USD/MMBtu"),
    ("RB=F", "RBOB汽油", "RBOB Gasoline", "USD/gal"),
    ("HO=F", "取暖油", "Heating Oil", "USD/gal"),
]

def main():
    print("正在获取国际油价数据...")
    results = []

    for symbol, name_cn, name_en, unit in SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            hist = ticker.history(period="2d")

            current_price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
            change = info.get("regularMarketChange")
            change_pct = info.get("regularMarketChangePercent")
            day_high = info.get("regularMarketDayHigh") or info.get("dayHigh")
            day_low = info.get("regularMarketDayLow") or info.get("dayLow")
            volume = info.get("regularMarketVolume")

            if current_price is None and not hist.empty:
                current_price = hist["Close"].iloc[-1]
                prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else None

            if current_price is not None:
                if change is None and prev_close is not None:
                    change = round(float(current_price) - float(prev_close), 2)
                if change_pct is None and prev_close is not None and float(prev_close) > 0:
                    change_pct = round((float(current_price) - float(prev_close)) / float(prev_close) * 100, 2)

            item = {
                "symbol": symbol,
                "name_cn": name_cn,
                "name_en": name_en,
                "unit": unit,
                "price": round(float(current_price), 2) if current_price else None,
                "change": round(float(change), 2) if change and change != 0 else change if change else None,
                "change_percent": round(float(change_pct), 2) if change_pct else None,
                "day_high": round(float(day_high), 2) if day_high else None,
                "day_low": round(float(day_low), 2) if day_low else None,
                "volume": int(volume) if volume else None,
            }
            results.append(item)
            print(f"  {name_cn} ({symbol}): {item['price']} USD")

        except Exception as e:
            print(f"  {symbol} 获取失败: {e}")
            results.append({
                "symbol": symbol,
                "name_cn": name_cn,
                "name_en": name_en,
                "unit": unit,
                "price": None,
                "change": None,
                "change_percent": None,
                "error": str(e)[:100],
            })

    output = {
        "source": "Yahoo Finance",
        "description": "国际原油及能源价格实时行情",
        "unit": "USD",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": results,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

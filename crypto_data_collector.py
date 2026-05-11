#!/usr/bin/env python3
"""
Crypto Microstructure Audit - Phase X
Data Collection: BTC/USDT and ETH/USDT perpetual futures (Binance)
Coverage: Last 14 days, all active hours
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

# Binance Futures API endpoint
BASE_URL = "https://fapi.binance.com"

def fetch_klines(symbol, interval="1m", days_back=14):
    """
    Fetch klines (candlestick) data from Binance Futures.
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        interval: Candle interval (e.g., "1m" for 1 minute)
        days_back: How many days back to fetch
    
    Returns:
        DataFrame with OHLCV data
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days_back)
    
    start_ts = int(start_time.timestamp() * 1000)
    end_ts = int(end_time.timestamp() * 1000)
    
    all_klines = []
    current_ts = start_ts
    
    # Binance limits: 1500 candles per request
    # For 1m candles over 14 days: 20,160 candles needed, so ~14 requests
    
    while current_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_ts,
            "endTime": end_ts,
            "limit": 1500
        }
        
        try:
            resp = requests.get(f"{BASE_URL}/fapi/v1/klines", params=params, timeout=10)
            resp.raise_for_status()
            klines = resp.json()
            
            if not klines:
                break
            
            all_klines.extend(klines)
            current_ts = klines[-1][6] + 1  # Move to next candle after last one
            
            print(f"  Fetched {len(klines)} candles for {symbol}, now at {datetime.fromtimestamp(current_ts/1000)}")
            time.sleep(0.5)  # Rate limit: ~1200 requests per minute
            
        except Exception as e:
            print(f"  Error fetching {symbol}: {e}")
            break
    
    # Convert to DataFrame
    # Binance klines format: [open_time, open, high, low, close, volume, close_time, quote_asset_volume, num_trades, taker_buy_base, taker_buy_quote, ignore]
    df = pd.DataFrame(all_klines)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                  'quote_volume', 'num_trades', 'taker_buy_volume', 'taker_buy_quote', 'ignore']
    
    # Convert to numeric
    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'num_trades', 'taker_buy_volume']:
        df[col] = pd.to_numeric(df[col])
    
    # Convert timestamps
    df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
    df = df.drop(['open_time', 'close_time', 'ignore'], axis=1)
    
    return df

def fetch_funding_rates(symbol, days_back=14):
    """
    Fetch funding rate history from Binance Futures.
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days_back)
    
    start_ts = int(start_time.timestamp() * 1000)
    end_ts = int(end_time.timestamp() * 1000)
    
    all_rates = []
    current_ts = start_ts
    
    while current_ts < end_ts:
        params = {
            "symbol": symbol,
            "startTime": current_ts,
            "endTime": end_ts,
            "limit": 1000
        }
        
        try:
            resp = requests.get(f"{BASE_URL}/fapi/v1/fundingRate", params=params, timeout=10)
            resp.raise_for_status()
            rates = resp.json()
            
            if not rates:
                break
            
            all_rates.extend(rates)
            current_ts = rates[-1]['fundingTime'] + 1
            
            print(f"  Fetched {len(rates)} funding rate entries for {symbol}")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  Error fetching funding rates for {symbol}: {e}")
            break
    
    df = pd.DataFrame(all_rates)
    if not df.empty:
        df['fundingRate'] = pd.to_numeric(df['fundingRate'])
        df['timestamp'] = pd.to_datetime(df['fundingTime'], unit='ms')
        df = df[['timestamp', 'fundingRate']]
    
    return df

def fetch_order_book_depth(symbol):
    """
    Fetch current order book depth for spread calculation.
    """
    try:
        params = {"symbol": symbol, "limit": 5}  # Top 5 bid/ask levels
        resp = requests.get(f"{BASE_URL}/fapi/v1/depth", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Error fetching orderbook for {symbol}: {e}")
        return None

def main():
    print("=" * 70)
    print("CRYPTO MICROSTRUCTURE AUDIT - DATA COLLECTION")
    print("=" * 70)
    print()
    
    symbols = ["BTCUSDT", "ETHUSDT"]
    
    all_data = {}
    
    for symbol in symbols:
        print(f"\nFetching data for {symbol}...")
        print("-" * 70)
        
        # Fetch 1-minute candles (14 days = 20,160 candles)
        print(f"Fetching 1-minute klines (14 days)...")
        klines_df = fetch_klines(symbol, interval="1m", days_back=14)
        
        # Fetch funding rates (8-hourly for perpetuals)
        print(f"Fetching funding rates...")
        funding_df = fetch_funding_rates(symbol, days_back=14)
        
        # Fetch current orderbook
        print(f"Fetching current orderbook depth...")
        ob = fetch_order_book_depth(symbol)
        
        # Calculate mid price, bid-ask spread
        if klines_df is not None and not klines_df.empty:
            klines_df['mid_price'] = (klines_df['high'] + klines_df['low']) / 2
            klines_df['volatility'] = klines_df['close'].pct_change().rolling(60).std() * np.sqrt(1440)  # Annualized
            
            # Calculate bid-ask spread (estimate from high-low as proxy)
            # This is rough; Binance doesn't provide bid-ask in klines
            # We'll estimate based on typical perpetual market microstructure
            klines_df['estimated_spread_bps'] = ((klines_df['high'] - klines_df['low']) / klines_df['mid_price']) * 10000
            
            # Trade frequency (trades per candle, use num_trades)
            klines_df['trades_per_minute'] = klines_df['num_trades']
            
            all_data[symbol] = {
                'klines': klines_df,
                'funding': funding_df,
                'orderbook': ob
            }
            
            print(f"\n✓ {symbol} data collected:")
            print(f"  - Klines: {len(klines_df)} candles ({klines_df['timestamp'].min()} to {klines_df['timestamp'].max()})")
            print(f"  - Funding rates: {len(funding_df)} entries")
            print(f"  - Date range: {(klines_df['timestamp'].max() - klines_df['timestamp'].min()).days} days")
        else:
            print(f"  ✗ Failed to fetch klines for {symbol}")
    
    # Save raw data
    print("\n" + "=" * 70)
    print("SAVING DATA...")
    print("=" * 70)
    
    output_dir = "/Users/rrg/.openclaw/workspace"
    
    for symbol, data in all_data.items():
        # Save klines
        klines_file = f"{output_dir}/crypto_phase_x_{symbol}_klines.csv"
        data['klines'].to_csv(klines_file, index=False)
        print(f"✓ Saved: {klines_file}")
        
        # Save funding rates
        if not data['funding'].empty:
            funding_file = f"{output_dir}/crypto_phase_x_{symbol}_funding.csv"
            data['funding'].to_csv(funding_file, index=False)
            print(f"✓ Saved: {funding_file}")
        
        # Save orderbook snapshot
        if data['orderbook']:
            ob_file = f"{output_dir}/crypto_phase_x_{symbol}_orderbook_snapshot.json"
            with open(ob_file, 'w') as f:
                json.dump(data['orderbook'], f, indent=2)
            print(f"✓ Saved: {ob_file}")
    
    print("\n" + "=" * 70)
    print("DATA COLLECTION COMPLETE")
    print("=" * 70)
    
    return all_data

if __name__ == "__main__":
    data = main()

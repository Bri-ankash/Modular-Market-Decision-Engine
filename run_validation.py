import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from mmde_engine import market_data, decision_engine

def test_timeframes(symbol='XAUUSD'):
    timeframes = ['H1', 'H4', 'D1']
    results = {}

    print(f"\n🚀 Testing Timeframe Consistency for {symbol}")
    print("=" * 50)

    for tf in timeframes:
        print(f"Fetching {tf} data...")
        data = market_data.fetch(symbol, tf, limit=50)
        
        print(f"Running analysis for {tf}...")
        res = decision_engine.run(
            candles=data['candles'],
            symbol=symbol,
            params={'interval': tf}
        )
        
        results[tf] = res
        print(f"✅ {tf} Analysis Complete: {res['action']} at {res['confidence_pct']} confidence.")
        print(f"   Entry: {res['entry_zone']} | SL: {res['stop_loss']} | TP1: {res['take_profit'][0]}")
        print("-" * 50)

    # Comparison Check
    h1_sl = results['H1']['stop_loss']
    d1_sl = results['D1']['stop_loss']
    
    if h1_sl != d1_sl:
        print("\n✨ SUCCESS: Stop Loss levels are DIFFERENT across timeframes.")
        print(f"   H1 SL: {h1_sl}")
        print(f"   D1 SL: {d1_sl}")
    else:
        print("\n❌ WARNING: Stop Loss levels are the same. Check logic.")

if __name__ == "__main__":
    test_timeframes()

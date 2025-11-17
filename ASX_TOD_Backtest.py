import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt
from ASX_Mining_TOD import MiningTimeOfDayAnalyzer
from asx_top_mining_tickers import TOP_ASX_MINING

def get_stock_prices(ticker):
    analyzer = MiningTimeOfDayAnalyzer()
    analyzer.mining_stocks = {ticker: ''}
    data = analyzer.fetch_stock_intraday_data(ticker)
    
    if data and '5min' in data:
        df = data['5min'].copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()]
        if 'Close' in df.columns:
            return df[['Close']].copy()
    return None

def find_daily_patterns(prices):
    if prices is None or prices.empty:
        return None, None
    
    work_df = prices.copy()
    work_df['returns'] = work_df['Close'].pct_change() * 100
    work_df['hour'] = work_df.index.hour
    work_df['minute'] = work_df.index.minute
    
    time_slots = {}
    for hour in range(10, 16):
        for start_min in [0, 15, 30, 45]:
            end_min = start_min + 15
            if hour == 15 and end_min > 60: break
            
            slot_name = f"{hour:02d}:{start_min:02d}-{hour:02d}:{end_min:02d}"
            in_slot = (work_df['hour'] == hour) & (work_df['minute'] >= start_min) & (work_df['minute'] < end_min)
            slot_returns = work_df[in_slot]['returns'].dropna()
            
            if len(slot_returns) > 5:
                time_slots[slot_name] = slot_returns.mean()
    
    if time_slots:
        best_time = max(time_slots, key=time_slots.get)
        worst_time = min(time_slots, key=time_slots.get)
        return best_time, worst_time
    return None, None

def test_strategy(prices, buy_time, sell_time):
    buy_hour, buy_min = map(int, buy_time.split('-')[1].split(':'))
    sell_hour, sell_min = map(int, sell_time.split('-')[1].split(':'))
    
    daily_trades = []
    for date, day_prices in prices.groupby(prices.index.date):
        buy_price = day_prices[(day_prices.index.hour == buy_hour) & (day_prices.index.minute == buy_min)]
        sell_price = day_prices[(day_prices.index.hour == sell_hour) & (day_prices.index.minute == sell_min)]
        
        if not buy_price.empty and not sell_price.empty:
            return_pct = (sell_price['Close'].iloc[0] - buy_price['Close'].iloc[0]) / buy_price['Close'].iloc[0]
            daily_trades.append({'date': date, 'return': return_pct})
    
    return pd.DataFrame(daily_trades)

def run_analysis(ticker):
    prices = get_stock_prices(ticker)
    if prices is None: 
        return None
    
    best_time, worst_time = find_daily_patterns(prices)
    if not best_time: 
        return None
    
    results = test_strategy(prices, worst_time, best_time)
    
    if not results.empty:
        avg_return = results['return'].mean() * 100
        win_rate = (results['return'] > 0).mean() * 100
        print(f"{ticker}: {len(results)} days | {avg_return:.2f}% avg | {win_rate:.0f}% wins")
    
    return results

def print_summary_dashboard(all_results):
    print("\n" + "="*80)
    print("ASX MINING TIME-OF-DAY TRADING BACKTEST SUMMARY")
    print("="*80)
    
    valid_results = [r for r in all_results if r is not None and not r.empty]
    total_trades = sum(len(r) for r in valid_results)
    profitable_stocks = sum(1 for r in valid_results if r['return'].mean() > 0)
    
    print(f"Total Trades: {total_trades:,}")
    print(f"Profitable Stocks: {profitable_stocks}/{len(valid_results)}")
    
    stock_performance = []
    for i, result in enumerate(all_results):
        if result is not None and not result.empty:
            ticker = TOP_ASX_MINING[i]
            avg_ret = result['return'].mean() * 100
            win_rate = (result['return'] > 0).mean() * 100
            stock_performance.append((ticker, avg_ret, win_rate, len(result)))
    
    stock_performance.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTOP 10 PERFORMERS:")
    print("Ticker   | Avg Return | Win Rate | Trades")
    print("-" * 45)
    for ticker, ret, win, trades in stock_performance[:10]:
        print(f"{ticker:<8} | {ret:>8.2f}% | {win:>6.0f}%  | {trades:>6}")

def create_results_plot(all_results):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='black')
    
    tickers, avg_returns, win_rates = [], [], []
    for i, result in enumerate(all_results):
        if result is not None and not result.empty:
            tickers.append(TOP_ASX_MINING[i].replace('.AX', ''))
            avg_returns.append(result['return'].mean() * 100)
            win_rates.append((result['return'] > 0).mean() * 100)
    
    if not tickers:
        print("No data to plot")
        return
    
    colors = ['green' if r > 0 else 'red' for r in avg_returns]
    ax1.barh(tickers, avg_returns, color=colors, alpha=0.8)
    ax1.set_xlabel('Average Daily Return (%)', color='white')
    ax1.set_title('Mining Stock Performance', color='white', fontsize=14)
    ax1.axvline(0, color='white', linestyle='-', alpha=0.5)
    ax1.tick_params(colors='white')
    ax1.set_facecolor('black')
    
    ax2.scatter(avg_returns, win_rates, c=colors, s=100, alpha=0.8)
    ax2.set_xlabel('Average Return (%)', color='white')
    ax2.set_ylabel('Win Rate (%)', color='white')
    ax2.set_title('Return vs Win Rate', color='white', fontsize=14)
    ax2.axhline(50, color='white', linestyle='--', alpha=0.5)
    ax2.axvline(0, color='white', linestyle='--', alpha=0.5)
    ax2.tick_params(colors='white')
    ax2.set_facecolor('black')
    
    plt.tight_layout()
    plt.savefig('mining_backtest_results.png', facecolor='black', dpi=150)
    plt.show()

def export_detailed_csv(all_results):
    detailed_data = []
    
    for i, result in enumerate(all_results):
        if result is not None and not result.empty:
            ticker = TOP_ASX_MINING[i]
            result_copy = result.copy()
            result_copy['ticker'] = ticker
            result_copy['return_pct'] = result_copy['return'] * 100
            result_copy['cumulative_return'] = (1 + result_copy['return']).cumprod() - 1
            detailed_data.append(result_copy)
    
    if detailed_data:
        final_df = pd.concat(detailed_data, ignore_index=True)
        final_df.to_csv("mining_detailed_backtest.csv", index=False)
        print(f"Exported {len(final_df)} detailed trades to CSV")

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_results = list(executor.map(run_analysis, TOP_ASX_MINING))
    
    print_summary_dashboard(all_results)
    export_detailed_csv(all_results)
    create_results_plot(all_results)
    
    valid_results = [r for r in all_results if r is not None and not r.empty]
    if valid_results:
        profitable_trades = sum(len(r[r['return'] > 0]) for r in valid_results)
        total_trades = sum(len(r) for r in valid_results)
        print(f"\nOverall Strategy Performance:")
        print(f"Profitable Trades: {profitable_trades}/{total_trades} ({profitable_trades/total_trades*100:.1f}%)")
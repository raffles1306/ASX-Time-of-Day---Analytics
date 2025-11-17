import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

awst = pytz.timezone('Australia/Perth')

class MiningTimeOfDayAnalyzer:
    def __init__(self):
        self.mining_stocks = {
            # LITHIUM & BATTERY MATERIALS
            'PLS.AX': 'Pilbara Minerals', 'MIN.AX': 'Mineral Resources', 'IGO.AX': 'IGO Limited',
            'NVX.AX': 'Novonix', 'VUL.AX': 'Vulcan Energy Resources', 'SYA.AX': 'Sayona Mining',
            'LTR.AX': 'Liontown Resources', 'CXO.AX': 'Core Lithium', 'INR.AX': 'Ioneer',
            'EMH.AX': 'European Metals Holdings', 'PSC.AX': 'Prospect Resources', 'GLN.AX': 'Galan Lithium',
            'LKE.AX': 'Lake Resources', 'ASN.AX': 'Anson Resources', 'EUR.AX': 'European Lithium',
            # GOLD MINERS
            'NCM.AX': 'Newcrest Mining', 'NST.AX': 'Northern Star', 'EVN.AX': 'Evolution Mining',
            'WGX.AX': 'Westgold Resources', 'GOR.AX': 'Gold Road Resources', 'RSG.AX': 'Resolute Mining',
            'PRU.AX': 'Perseus Mining', 'RRL.AX': 'Regis Resources', 'SBM.AX': 'St Barbara',
            'RMS.AX': 'Ramelius Resources', 'DEG.AX': 'De Grey Mining', 'WAF.AX': 'West African Resources',
            'PNR.AX': 'PanTerra Gold', 'AQG.AX': 'Alacer Gold', 'KGN.AX': 'Kogan Gold', 'CGF.AX': 'Challenger Gold',
            # IRON ORE & STEEL
            'BHP.AX': 'BHP Billiton', 'RIO.AX': 'Rio Tinto', 'FMG.AX': 'Fortescue Metals',
            'MGX.AX': 'Mount Gibson Iron', 'GRR.AX': 'Grange Resources', 'FEX.AX': 'Fenix Resources',
            'CIA.AX': 'Champion Iron', 'GBG.AX': 'Gindalbie Metals',
            # COPPER & BASE METALS
            'S32.AX': 'South32', 'OZL.AX': 'OZ Minerals', 'SFR.AX': 'Sandfire Resources',
            'C6C.AX': 'Copper Mountain', 'HCU.AX': 'Havilah Resources', 'AIS.AX': 'Aeris Resources',
            'MOD.AX': 'MOD Resources', 'HOT.AX': 'Hot Chili',
            # COAL MINERS
            'WHC.AX': 'Whitehaven Coal', 'NHC.AX': 'New Hope Corporation', 'YAL.AX': 'Yancoal Australia',
            'CNU.AX': 'Cerro Negro', 'SMR.AX': 'Stanmore Coal', 'CKA.AX': 'Cokal Limited',
            # NICKEL MINERS
            'WSA.AX': 'Western Areas', 'MCR.AX': 'Mincor Resources', 'PAN.AX': 'Panoramic Resources',
            'NIC.AX': 'Nickel Mines', 'MRE.AX': 'Minara Resources', 'JPR.AX': 'Jupiter Mines',
            # RARE EARTHS & URANIUM
            'LYC.AX': 'Lynas Rare Earths', 'AR3.AX': 'American Rare Earths', 'HAS.AX': 'Hastings Technology',
            'IXR.AX': 'Ionic Rare Earths', 'VML.AX': 'Vital Metals', 'REE.AX': 'Rare Element Resources',
            'PDN.AX': 'Paladin Energy', 'PEN.AX': 'Peninsula Energy', 'BOE.AX': 'Boss Energy',
            'BMN.AX': 'Bannerman Energy', 'DYL.AX': 'Deep Yellow', 'LOT.AX': 'Lotus Resources',
            # ZINC, LEAD & OTHER METALS
            'ZFX.AX': 'Zinifex Limited', 'CBH.AX': 'CBH Resources', 'KZL.AX': 'Kagara Limited',
            'TNG.AX': 'TNG Limited', 'TMZ.AX': 'Thomson Resources', 'AAC.AX': 'Australian Agricultural',
            # INDUSTRIAL MINERALS & DIVERSIFIED
            'AWC.AX': 'Alumina Limited', 'IPL.AX': 'Incitec Pivot', 'NMT.AX': 'Neometals',
            'SYR.AX': 'Syrah Resources', 'MYX.AX': 'Mayne Pharma', 'SLX.AX': 'Silex Systems',
            # SMALLER MINERS & EXPLORERS
            'AZJ.AX': 'Austar Gold', 'BDR.AX': 'Beadell Resources', 'EMR.AX': 'Emerald Resources',
            'GDI.AX': 'GDI Property', 'KIN.AX': 'Kin Mining', 'LEG.AX': 'Legend Mining',
            'MEI.AX': 'Meteoric Resources', 'NTM.AX': 'Northern Minerals', 'RED.AX': 'Red 5 Limited',
            'WRM.AX': 'White Rock Minerals', 'ABX.AX': 'ABx Group', 'AEF.AX': 'Australian Ethical',
            'ARL.AX': 'Ardea Resources', 'BSX.AX': 'Blackstone Minerals', 'CLA.AX': 'Celsius Resources',
            'CNB.AX': 'Carnaby Resources', 'EME.AX': 'Energy Metals', 'GSN.AX': 'Great Southern Mining',
            'KAI.AX': 'Kairos Minerals', 'LAM.AX': 'Lachlan Star', 'LML.AX': 'Lincoln Minerals',
            'MAN.AX': 'Mandrake Resources', 'NVA.AX': 'Nova Minerals', 'CXZ.AX': 'Corazon Mining'
        }
        self.valid_stocks = {}
        self.all_results = {}

    def filter_mining_stocks(self):
        print(f"Filtering {len(self.mining_stocks)} mining stocks (price > $0.10)...")
        valid_count = 0
        for ticker, name in self.mining_stocks.items():
            try:
                recent_data = yf.download(ticker, period="5d", interval="1d", progress=False)
                if not recent_data.empty:
                    current_price = float(recent_data['Close'].iloc[-1])
                    avg_volume = float(recent_data['Volume'].mean()) if 'Volume' in recent_data.columns else 0
                    if current_price > 0.10:
                        self.valid_stocks[ticker] = {
                            'name': name,
                            'current_price': current_price,
                            'avg_volume': avg_volume
                        }
                        valid_count += 1
                        print(f"  ✓ {ticker}: ${current_price:.3f}")
                    else:
                        print(f"  ✗ {ticker}: ${current_price:.3f} (below $0.10)")
                else:
                    print(f"  ? {ticker}: No data")
            except Exception as e:
                continue
        print(f"\nFound {valid_count} valid stocks")
        return len(self.valid_stocks) > 0

    def fetch_stock_intraday_data(self, ticker):
        try:
            print(f"  Fetching {ticker}...", end="")
            datasets = {}
            datasets['1min'] = yf.download(ticker, period="7d", interval="1m", progress=False)
            datasets['5min'] = yf.download(ticker, period="60d", interval="5m", progress=False)
            datasets['15min'] = yf.download(ticker, period="60d", interval="15m", progress=False)
            datasets['30min'] = yf.download(ticker, period="60d", interval="30m", progress=False)
            datasets['1hour'] = yf.download(ticker, period="730d", interval="1h", progress=False)
            stock_data = {}
            total_points = 0
            for tf, data in datasets.items():
                if not data.empty:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    if data.index.tz is not None:
                        data.index = data.index.tz_convert(awst)
                    else:
                        data.index = data.index.tz_localize('UTC').tz_convert(awst)
                    data.index = data.index.tz_localize(None)
                    trading_data = data[
                        (data.index.hour >= 10) &
                        (data.index.hour <= 15) &
                        (data.index.weekday < 5)
                    ]
                    if len(trading_data) > 20:
                        stock_data[tf] = trading_data
                        total_points += len(trading_data)
            if stock_data:
                print(f" ✓ ({total_points:,} total AWST trading hours data points)")
                return stock_data
            else:
                print(f" ✗ (insufficient data)")
                return None
        except Exception as e:
            print(f" ✗ (error: {str(e)[:30]})")
            return None

    def analyze_stock_tod_patterns(self, ticker, stock_data):
        stock_results = {}
        for timeframe, data in stock_data.items():
            try:
                data_work = data.copy()
                data_work['returns'] = data_work['Close'].pct_change() * 100
                data_work['hour'] = data_work.index.hour
                data_work['minute'] = data_work.index.minute
                data_work = data_work.dropna()
                data_work = data_work[abs(data_work['returns']) < 25]
                if len(data_work) < 20:
                    continue
                time_periods = {
                    '10:00-10:15': data_work[(data_work['hour'] == 10) & (data_work['minute'] <= 15)]['returns'],
                    '10:15-10:30': data_work[(data_work['hour'] == 10) & (data_work['minute'] > 15) & (data_work['minute'] <= 30)]['returns'],
                    '10:30-10:45': data_work[(data_work['hour'] == 10) & (data_work['minute'] > 30) & (data_work['minute'] <= 45)]['returns'],
                    '10:45-11:00': data_work[(data_work['hour'] == 10) & (data_work['minute'] > 45)]['returns'],
                    '11:00-11:15': data_work[(data_work['hour'] == 11) & (data_work['minute'] <= 15)]['returns'],
                    '11:15-11:30': data_work[(data_work['hour'] == 11) & (data_work['minute'] > 15) & (data_work['minute'] <= 30)]['returns'],
                    '11:30-11:45': data_work[(data_work['hour'] == 11) & (data_work['minute'] > 30) & (data_work['minute'] <= 45)]['returns'],
                    '11:45-12:00': data_work[(data_work['hour'] == 11) & (data_work['minute'] > 45)]['returns'],
                    '12:00-12:15': data_work[(data_work['hour'] == 12) & (data_work['minute'] <= 15)]['returns'],
                    '12:15-12:30': data_work[(data_work['hour'] == 12) & (data_work['minute'] > 15) & (data_work['minute'] <= 30)]['returns'],
                    '12:30-12:45': data_work[(data_work['hour'] == 12) & (data_work['minute'] > 30) & (data_work['minute'] <= 45)]['returns'],
                    '12:45-13:00': data_work[(data_work['hour'] == 12) & (data_work['minute'] > 45)]['returns'],
                    '13:00-13:15': data_work[(data_work['hour'] == 13) & (data_work['minute'] <= 15)]['returns'],
                    '13:15-13:30': data_work[(data_work['hour'] == 13) & (data_work['minute'] > 15) & (data_work['minute'] <= 30)]['returns'],
                    '13:30-13:45': data_work[(data_work['hour'] == 13) & (data_work['minute'] > 30) & (data_work['minute'] <= 45)]['returns'],
                    '13:45-14:00': data_work[(data_work['hour'] == 13) & (data_work['minute'] > 45)]['returns'],
                    '14:00-14:15': data_work[(data_work['hour'] == 14) & (data_work['minute'] <= 15)]['returns'],
                    '14:15-14:30': data_work[(data_work['hour'] == 14) & (data_work['minute'] > 15) & (data_work['minute'] <= 30)]['returns'],
                    '14:30-14:45': data_work[(data_work['hour'] == 14) & (data_work['minute'] > 30) & (data_work['minute'] <= 45)]['returns'],
                    '14:45-15:00': data_work[(data_work['hour'] == 14) & (data_work['minute'] > 45)]['returns'],
                    '15:00-15:15': data_work[(data_work['hour'] == 15) & (data_work['minute'] <= 15)]['returns']
                }
                time_stats = []
                for period_name, period_returns in time_periods.items():
                    if not period_returns.empty and len(period_returns) >= 3:
                        avg_volume = 0
                        volume_ratio = 1.0
                        if 'Volume' in data_work.columns:
                            period_mask = self.get_detailed_time_mask(data_work, period_name)
                            if period_mask.any():
                                period_volume = data_work[period_mask]['Volume']
                                avg_volume = period_volume.mean() if not period_volume.empty else 0
                                daily_avg_vol = data_work['Volume'].mean()
                                volume_ratio = avg_volume / max(daily_avg_vol, 1)
                        returns_clean = period_returns.dropna()
                        time_stats.append({
                            'Ticker': ticker,
                            'Timeframe': timeframe,
                            'Time_Period_AWST': period_name,
                            'Avg_Return_%': round(returns_clean.mean(), 5),
                            'Median_Return_%': round(returns_clean.median(), 5),
                            'Std_Dev_%': round(returns_clean.std(), 5),
                            'Min_Return_%': round(returns_clean.min(), 5),
                            'Max_Return_%': round(returns_clean.max(), 5),
                            'Observations': len(returns_clean),
                            'Positive_Returns': len(returns_clean[returns_clean > 0]),
                            'Negative_Returns': len(returns_clean[returns_clean < 0]),
                            'Win_Rate_%': round(len(returns_clean[returns_clean > 0]) / len(returns_clean) * 100, 2),
                            'Avg_Volume': round(avg_volume, 0),
                            'Volume_Ratio_vs_Daily': round(volume_ratio, 3),
                            'Volatility_Rank': 'HIGH' if returns_clean.std() > 2 else 'MEDIUM' if returns_clean.std() > 1 else 'LOW',
                            'Pattern_Strength': 'STRONG' if abs(returns_clean.mean()) > 0.15 else 'MODERATE' if abs(returns_clean.mean()) > 0.08 else 'WEAK',
                            'Trading_Signal': self.get_trading_signal(returns_clean.mean(), len(returns_clean))
                        })
                if time_stats:
                    stock_results[timeframe] = pd.DataFrame(time_stats)
            except Exception as e:
                print(f"    Error analyzing {timeframe}: {e}")
                continue
        return stock_results

    def get_detailed_time_mask(self, data, period_name):
        try:
            start_time, end_time = period_name.split('-')
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            if start_hour == end_hour:
                return (data['hour'] == start_hour) & (data['minute'] > start_min) & (data['minute'] <= end_min)
            else:
                return ((data['hour'] == start_hour) & (data['minute'] > start_min)) | \
                       ((data['hour'] == end_hour) & (data['minute'] <= end_min))
        except:
            return pd.Series([False] * len(data))

    def get_trading_signal(self, avg_return, observations):
        if observations < 5:
            return 'INSUFFICIENT_DATA'
        elif avg_return > 0.2:
            return 'STRONG_BUY'
        elif avg_return > 0.1:
            return 'BUY'
        elif avg_return > 0.05:
            return 'WEAK_BUY'
        elif avg_return < -0.2:
            return 'STRONG_SELL'
        elif avg_return < -0.1:
            return 'SELL'
        elif avg_return < -0.05:
            return 'WEAK_SELL'
        else:
            return 'NEUTRAL'

    def run_comprehensive_analysis(self):
        print("="*80)
        print("ASX MINING SECTOR TIME-OF-DAY COMPREHENSIVE ANALYSIS (AWST)")
        print("="*80)
        print(f"Analysis Start Time: {datetime.now(awst).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        if not self.filter_mining_stocks():
            print("No valid mining stocks found!")
            return
        print(f"\nAnalyzing time-of-day patterns for {len(self.valid_stocks)} mining stocks...")
        successful_stocks = 0
        for ticker in self.valid_stocks.keys():
            stock_data = self.fetch_stock_intraday_data(ticker)
            if stock_data:
                stock_results = self.analyze_stock_tod_patterns(ticker, stock_data)
                if stock_results:
                    self.all_results[ticker] = stock_results
                    successful_stocks += 1
                    total_periods = sum(len(df) for df in stock_results.values())
                    print(f"    ✓ {ticker}: {total_periods} time periods analyzed")
                else:
                    print(f"    ✗ {ticker}: Pattern analysis failed")
            else:
                print(f"    ✗ {ticker}: Data fetch failed")
        print(f"\nSuccessfully analyzed {successful_stocks} stocks")
        if self.all_results:
            excel_file = self.create_comprehensive_excel()
            if excel_file:
                self.print_comprehensive_summary()
        else:
            print("No analysis results generated")

    def create_comprehensive_excel(self):
        timestamp = datetime.now(awst).strftime('%Y%m%d_%H%M%S')
        filename = f"Mining_Sector_TimeOfDay_Comprehensive_{timestamp}.xlsx"
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                exec_summary = []
                for ticker, stock_results in self.all_results.items():
                    stock_info = self.valid_stocks[ticker]
                    all_periods = []
                    for timeframe, df in stock_results.items():
                        for _, row in df.iterrows():
                            all_periods.append({
                                'period': row['Time_Period_AWST'],
                                'return': row['Avg_Return_%'],
                                'observations': row['Observations'],
                                'volume': row['Avg_Volume'],
                                'timeframe': timeframe
                            })
                    if all_periods:
                        best_period = max(all_periods, key=lambda x: x['return'])
                        worst_period = min(all_periods, key=lambda x: x['return'])
                        morning_periods = [p for p in all_periods if p['period'].startswith(('10:', '11:'))]
                        afternoon_periods = [p for p in all_periods if p['period'].startswith(('13:', '14:'))]
                        avg_morning = np.mean([p['return'] for p in morning_periods]) if morning_periods else 0
                        avg_afternoon = np.mean([p['return'] for p in afternoon_periods]) if afternoon_periods else 0
                        morning_dip_strength = 'STRONG' if avg_morning < -0.15 else 'MODERATE' if avg_morning < -0.08 else 'WEAK' if avg_morning < 0 else 'NONE'
                        afternoon_rally_strength = 'STRONG' if avg_afternoon > 0.15 else 'MODERATE' if avg_afternoon > 0.08 else 'WEAK' if avg_afternoon > 0 else 'NONE'
                        total_swing = avg_afternoon - avg_morning
                        exec_summary.append({
                            'Ticker': ticker,
                            'Company': stock_info['name'],
                            'Current_Price_$': stock_info['current_price'],
                            'Avg_Daily_Volume': stock_info['avg_volume'],
                            'Total_Time_Periods_Analyzed': len(all_periods),
                            'Total_Observations': sum(p['observations'] for p in all_periods),
                            'Best_Time_Period_AWST': best_period['period'],
                            'Best_Period_Return_%': round(best_period['return'], 4),
                            'Worst_Time_Period_AWST': worst_period['period'],
                            'Worst_Period_Return_%': round(worst_period['return'], 4),
                            'Intraday_Range_%': round(best_period['return'] - worst_period['return'], 4),
                            'Average_Morning_Return_%': round(avg_morning, 4),
                            'Average_Afternoon_Return_%': round(avg_afternoon, 4),
                            'Morning_Afternoon_Swing_%': round(total_swing, 4),
                            'Morning_Dip_Strength': morning_dip_strength,
                            'Afternoon_Rally_Strength': afternoon_rally_strength,
                            'Pattern_Consistency': len(set(p['period'] for p in all_periods if abs(p['return']) > 0.1)),
                            'Trading_Strategy_Viability': 'HIGH' if total_swing > 0.3 else 'MEDIUM' if total_swing > 0.15 else 'LOW',
                            'Recommended_Entry_Time': worst_period['period'],
                            'Recommended_Exit_Time': best_period['period'],
                            'Expected_Swing_%': round(total_swing, 4),
                            'Risk_Level': 'HIGH' if abs(worst_period['return']) > 0.5 else 'MEDIUM' if abs(worst_period['return']) > 0.2 else 'LOW',
                            'Position_Size_Recommendation': '10%' if total_swing > 0.5 else '5%' if total_swing > 0.25 else '2%',
                            'Data_Quality_Score': 'EXCELLENT' if sum(p['observations'] for p in all_periods) > 1000 else 'GOOD' if sum(p['observations'] for p in all_periods) > 500 else 'FAIR'
                        })
                if exec_summary:
                    exec_df = pd.DataFrame(exec_summary)
                    exec_df = exec_df.sort_values('Morning_Afternoon_Swing_%', ascending=False)
                    exec_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
                for ticker, stock_results in self.all_results.items():
                    for timeframe, df in stock_results.items():
                        sheet_name = f'{ticker.replace(".AX", "")}_{timeframe}'[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                sector_summary = []
                all_time_data = {}
                for ticker, stock_results in self.all_results.items():
                    for timeframe, df in stock_results.items():
                        for _, row in df.iterrows():
                            period = row['Time_Period_AWST']
                            if period not in all_time_data:
                                all_time_data[period] = []
                            all_time_data[period].append({
                                'ticker': ticker,
                                'return': row['Avg_Return_%'],
                                'observations': row['Observations'],
                                'volume': row['Avg_Volume'],
                                'timeframe': timeframe
                            })
                for period, period_data in all_time_data.items():
                    if len(period_data) >= 3:
                        returns = [p['return'] for p in period_data]
                        total_obs = sum(p['observations'] for p in period_data)
                        weighted_return = sum(r * o for r, o in zip(returns, [p['observations'] for p in period_data])) / total_obs
                        sector_summary.append({
                            'Time_Period_AWST': period,
                            'Sector_Weighted_Return_%': round(weighted_return, 5),
                            'Stocks_Confirming_Pattern': len(period_data),
                            'Total_Observations': total_obs,
                            'Return_Standard_Deviation': round(np.std(returns), 4),
                            'Strongest_Stock': max(period_data, key=lambda x: x['return'])['ticker'],
                            'Weakest_Stock': min(period_data, key=lambda x: x['return'])['ticker'],
                            'Sector_Trading_Signal': self.get_trading_signal(weighted_return, len(period_data)),
                            'Pattern_Reliability': 'HIGH' if len(period_data) >= 5 and np.std(returns) < 0.3 else 'MEDIUM' if len(period_data) >= 3 else 'LOW'
                        })
                if sector_summary:
                    sector_df = pd.DataFrame(sector_summary)
                    sector_df = sector_df.sort_values('Sector_Weighted_Return_%', ascending=False)
                    sector_df.to_excel(writer, sheet_name='Sector_TimeOfDay_Summary', index=False)
                best_opportunities = []
                for ticker, stock_results in self.all_results.items():
                    stock_opportunities = []
                    for timeframe, df in stock_results.items():
                        for _, row in df.iterrows():
                            if abs(row['Avg_Return_%']) > 0.08:
                                stock_opportunities.append({
                                    'ticker': ticker,
                                    'timeframe': timeframe,
                                    'period': row['Time_Period_AWST'],
                                    'return': row['Avg_Return_%'],
                                    'observations': row['Observations'],
                                    'signal': row['Trading_Signal']
                                })
                    if stock_opportunities:
                        best_opp = max(stock_opportunities, key=lambda x: abs(x['return']))
                        worst_opp = min(stock_opportunities, key=lambda x: x['return'])
                        swing = best_opp['return'] - worst_opp['return']
                        best_opportunities.append({
                            'Ticker': ticker,
                            'Company': self.valid_stocks[ticker]['name'],
                            'Current_Price_$': self.valid_stocks[ticker]['current_price'],
                            'Best_Entry_Time_AWST': worst_opp['period'],
                            'Entry_Expected_Return_%': round(worst_opp['return'], 4),
                            'Best_Exit_Time_AWST': best_opp['period'],
                            'Exit_Expected_Return_%': round(best_opp['return'], 4),
                            'Total_Expected_Swing_%': round(swing, 4),
                            'Entry_Observations': worst_opp['observations'],
                            'Exit_Observations': best_opp['observations'],
                            'Strategy_Confidence': 'HIGH' if min(worst_opp['observations'], best_opp['observations']) > 20 else 'MEDIUM',
                            'Risk_Reward_Ratio': round(abs(best_opp['return']) / max(abs(worst_opp['return']), 0.01), 2)
                        })
                if best_opportunities:
                    opportunities_df = pd.DataFrame(best_opportunities)
                    opportunities_df = opportunities_df.sort_values('Total_Expected_Swing_%', ascending=False)
                    opportunities_df.to_excel(writer, sheet_name='Best_Opportunities', index=False)
                metadata = pd.DataFrame([{
                    'Analysis_Date_Time_AWST': datetime.now(awst).strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'Sector': 'ASX Mining & Resources Sector',
                    'Exchange': 'ASX (Australian Securities Exchange)',
                    'Timezone': 'AWST (Australian Western Standard Time)',
                    'Trading_Hours_Analyzed': '10:00-15:00 AWST (Weekdays Only)',
                    'Total_Stocks_Screened': len(self.mining_stocks),
                    'Valid_Stocks_Analyzed': len(self.all_results),
                    'Analysis_Type': 'High-Frequency Time-of-Day Impact Analysis',
                    'Minimum_Price_Filter': '$0.10',
                    'Time_Period_Granularity': '15-minute intervals',
                    'Maximum_Data_Range': '730 days (hourly), 60 days (intraday)',
                    'Total_Time_Periods': sum(sum(len(tf_data) for tf_data in stock_data.values()) for stock_data in self.all_results.values()),
                    'Total_Observations': self.calculate_total_observations(),
                    'Analysis_Quality': 'INSTITUTIONAL_GRADE',
                    'Currency': 'AUD',
                    'Data_Source': 'Yahoo Finance'
                }])
                metadata.to_excel(writer, sheet_name='Analysis_Metadata', index=False)
            print(f"Comprehensive Excel analysis saved: {filename}")
            return filename
        except Exception as e:
            print(f"Excel creation error: {e}")
            return None

    def calculate_total_observations(self):
        total = 0
        for stock_results in self.all_results.values():
            for df in stock_results.values():
                total += df['Observations'].sum()
        return total

    def print_comprehensive_summary(self):
        if not self.all_results:
            return
        print(f"\n{'='*100}")
        print(f"MINING SECTOR TIME-OF-DAY ANALYSIS - COMPREHENSIVE SUMMARY")
        print(f"{'='*100}")
        print(f"Analysis Completion Time: {datetime.now(awst).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Total Stocks Analyzed: {len(self.all_results)}")
        print(f"Total Observations: {self.calculate_total_observations():,}")
        print(f"\nSECTOR-WIDE TIME-OF-DAY PATTERNS (AWST):")
        print(f"{'Time Period':<15} {'Avg Return%':<12} {'Stocks':<7} {'Pattern':<12} {'Strength':<10}")
        print(f"{'-'*70}")
        sector_periods = {}
        for ticker, stock_results in self.all_results.items():
            for timeframe, df in stock_results.items():
                for _, row in df.iterrows():
                    period = row['Time_Period_AWST']
                    if period not in sector_periods:
                        sector_periods[period] = []
                    sector_periods[period].append({
                        'return': row['Avg_Return_%'],
                        'observations': row['Observations']
                    })
        sector_summary = []
        for period, data in sector_periods.items():
            if len(data) >= 3:
                returns = [d['return'] for d in data]
                weighted_return = np.mean(returns)
                pattern_type = ('DIP' if weighted_return < -0.05 else
                              'RALLY' if weighted_return > 0.05 else 'NEUTRAL')
                strength = ('STRONG' if abs(weighted_return) > 0.15 else
                           'MODERATE' if abs(weighted_return) > 0.08 else 'WEAK')
                sector_summary.append({
                    'period': period,
                    'return': weighted_return,
                    'stocks': len(data),
                    'pattern': pattern_type,
                    'strength': strength
                })
                print(f"{period:<15} {weighted_return:>10.3f}% {len(data):<7} {pattern_type:<12} {strength:<10}")
        if sector_summary:
            sector_df = pd.DataFrame(sector_summary).sort_values('return')
            worst_time = sector_df.iloc[0]
            best_time = sector_df.iloc[-1]
            print(f"\nSECTOR-WIDE OPTIMAL TIMING:")
            print(f"  WORST TIME (ENTRY): {worst_time['period']} ({worst_time['return']:+.3f}%)")
            print(f"  BEST TIME (EXIT): {best_time['period']} ({best_time['return']:+.3f}%)")
            print(f"  SECTOR SWING: {best_time['return'] - worst_time['return']:.3f}%")
            print(f"  PATTERN RELIABILITY: {min(worst_time['stocks'], best_time['stocks'])} stocks confirm")
        print(f"\nTOP 10 INDIVIDUAL STOCK OPPORTUNITIES:")
        print(f"{'Ticker':<8} {'Entry Time':<12} {'Exit Time':<12} {'Swing%':<8} {'Price':<8} {'Quality':<10}")
        print(f"{'-'*70}")
        individual_opportunities = []
        for ticker, stock_results in self.all_results.items():
            all_returns = []
            for timeframe, df in stock_results.items():
                for _, row in df.iterrows():
                    all_returns.append({
                        'period': row['Time_Period_AWST'],
                        'return': row['Avg_Return_%'],
                        'observations': row['Observations']
                    })
            if all_returns:
                best = max(all_returns, key=lambda x: x['return'])
                worst = min(all_returns, key=lambda x: x['return'])
                swing = best['return'] - worst['return']
                quality = ('EXCELLENT' if min(best['observations'], worst['observations']) > 50 else
                          'GOOD' if min(best['observations'], worst['observations']) > 20 else 'FAIR')
                individual_opportunities.append({
                    'ticker': ticker,
                    'entry_time': worst['period'],
                    'exit_time': best['period'],
                    'swing': swing,
                    'price': self.valid_stocks[ticker]['current_price'],
                    'quality': quality
                })
        top_opportunities = sorted(individual_opportunities, key=lambda x: x['swing'], reverse=True)[:10]
        for opp in top_opportunities:
            print(f"{opp['ticker'].replace('.AX', ''):<8} {opp['entry_time']:<12} {opp['exit_time']:<12} "
                  f"{opp['swing']:>6.2f}% ${opp['price']:>6.2f} {opp['quality']:<10}")
        avg_sector_swing = np.mean([opp['swing'] for opp in individual_opportunities])
        viable_strategies = len([opp for opp in individual_opportunities if opp['swing'] > 0.3])
        print(f"\nSECTOR CONCLUSION:")
        print(f"  Average Stock Swing: {avg_sector_swing:.2f}%")
        print(f"  Viable Trading Strategies: {viable_strategies}/{len(individual_opportunities)} stocks")
        if viable_strategies >= len(individual_opportunities) * 0.4:
            print(f"  SECTOR STRATEGY: VIABLE - Systematic time-of-day trading recommended")
            print(f"  FOCUS: Top {viable_strategies} stocks with >0.3% swing")
        elif viable_strategies > 0:
            print(f"  SECTOR STRATEGY: SELECTIVE - Only trade top {viable_strategies} performers")
        else:
            print(f"  SECTOR STRATEGY: NOT VIABLE - Insufficient consistent patterns")
        print(f"{'='*100}")

    def run_complete_analysis(self):
        self.run_comprehensive_analysis()

if __name__ == "__main__":
    analyzer = MiningTimeOfDayAnalyzer()
    analyzer.run_complete_analysis()
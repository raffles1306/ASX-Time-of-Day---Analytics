import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the mining analysis class
from ASX_Mining_TOD import MiningTimeOfDayAnalyzer

plt.style.use('dark_background')

class MiningTODPlotter:
    def __init__(self):
        self.analyzer = MiningTimeOfDayAnalyzer()
        
    def create_comprehensive_dashboard(self):
        """Create one large comprehensive dashboard with all mining plots"""
        print("Running ASX mining TOD analysis and creating comprehensive dashboard...")
        
        # Run the analysis
        if not self.analyzer.filter_mining_stocks():
            print("No valid mining stocks found")
            return
        
        print(f"Analyzing {len(self.analyzer.valid_stocks)} mining stocks...")
        
        # Get analysis results
        successful = 0
        for ticker in self.analyzer.valid_stocks.keys():
            stock_data = self.analyzer.fetch_stock_intraday_data(ticker)
            if stock_data:
                stock_results = self.analyzer.analyze_stock_tod_patterns(ticker, stock_data)
                if stock_results:
                    self.analyzer.all_results[ticker] = stock_results
                    successful += 1
        
        if not self.analyzer.all_results:
            print("No analysis results generated")
            return
        
        print(f"Analysis complete: {successful} mining stocks processed")
        
        # Create MEGA dashboard - 6 plots in one large figure
        fig = plt.figure(figsize=(30, 20), facecolor='black')
        
        # Extract data for plotting
        sector_periods = {}
        stock_swings = {}
        
        # Aggregate data
        for ticker, stock_results in self.analyzer.all_results.items():
            stock_periods = []
            
            for timeframe, df in stock_results.items():
                for _, row in df.iterrows():
                    period = row['Time_Period_AWST']
                    return_val = row['Avg_Return_%']
                    
                    # Add to sector data
                    if period not in sector_periods:
                        sector_periods[period] = []
                    sector_periods[period].append(return_val)
                    
                    # Track for stock swing calculation
                    stock_periods.append(return_val)
            
            if stock_periods:
                swing = max(stock_periods) - min(stock_periods)
                stock_swings[ticker] = {
                    'swing': swing,
                    'price': self.analyzer.valid_stocks[ticker]['current_price'],
                    'best_return': max(stock_periods),
                    'worst_return': min(stock_periods)
                }
        
        # 1. Mining Sector Time-of-Day Pattern (Large plot)
        ax1 = plt.subplot(3, 3, (1, 3))
        
        if sector_periods:
            periods = sorted(sector_periods.keys())
            avg_returns = [np.mean(sector_periods[p]) for p in periods]
            
            # Convert periods to numeric for plotting
            time_numeric = []
            for period in periods:
                try:
                    hour, minute = period.split('-')[0].split(':')
                    time_numeric.append(int(hour) + int(minute)/60)
                except:
                    time_numeric.append(12)
            
            # Plot line with color-coded points
            ax1.plot(time_numeric, avg_returns, 'cyan', linewidth=4, alpha=0.9, marker='o', markersize=8)
            
            # Color points by performance
            colors = ['red' if r < -0.05 else 'green' if r > 0.05 else 'gold' for r in avg_returns]
            ax1.scatter(time_numeric, avg_returns, c=colors, s=150, alpha=0.9, edgecolors='white', linewidth=2, zorder=5)
            
            ax1.axhline(0, color='white', alpha=0.7, linestyle='-', linewidth=2)
            ax1.axvspan(10, 11, alpha=0.15, color='red', label='Morning Hour')
            ax1.axvspan(13, 15, alpha=0.15, color='green', label='Afternoon Hours')
            
            # Annotate best and worst times
            best_idx = np.argmax(avg_returns)
            worst_idx = np.argmin(avg_returns)
            
            ax1.annotate(f'PEAK TIME\n{periods[best_idx]}\n{avg_returns[best_idx]:+.3f}%',
                        xy=(time_numeric[best_idx], avg_returns[best_idx]),
                        xytext=(20, 30), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='lime', alpha=0.9),
                        arrowprops=dict(arrowstyle='->', color='white', lw=2),
                        fontsize=12, color='black', fontweight='bold')
            
            ax1.annotate(f'DIP TIME\n{periods[worst_idx]}\n{avg_returns[worst_idx]:+.3f}%',
                        xy=(time_numeric[worst_idx], avg_returns[worst_idx]),
                        xytext=(20, -40), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.9),
                        arrowprops=dict(arrowstyle='->', color='white', lw=2),
                        fontsize=12, color='white', fontweight='bold')
            
            ax1.set_xlabel('Trading Time (AWST)', color='white', fontsize=14)
            ax1.set_ylabel('Mining Sector Average Return (%)', color='white', fontsize=14)
            ax1.set_title('ASX MINING SECTOR TIME-OF-DAY PATTERN', color='white', fontsize=18, fontweight='bold')
            ax1.grid(True, alpha=0.4)
            ax1.legend(fontsize=12)
            
            # Format x-axis
            ax1.set_xticks([10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15])
            ax1.set_xticklabels(['10:00', '10:30', '11:00', '11:30', '12:00', '12:30',
                               '13:00', '13:30', '14:00', '14:30', '15:00'], fontsize=12)
        
        # 2. Mining Stock Swing Ranking
        ax2 = plt.subplot(3, 3, 4)
        
        if stock_swings:
            # Sort by swing magnitude
            sorted_items = sorted(stock_swings.items(), key=lambda x: x[1]['swing'], reverse=True)[:15]
            
            tickers = [item[0].replace('.AX', '') for item in sorted_items]
            swings = [item[1]['swing'] for item in sorted_items]
            
            colors = ['darkgreen' if s > 0.5 else 'green' if s > 0.3 else 'gold' if s > 0.15 else 'orange' 
                     for s in swings]
            
            bars = ax2.barh(range(len(tickers)), swings, color=colors, alpha=0.8)
            ax2.set_yticks(range(len(tickers)))
            ax2.set_yticklabels(tickers, color='white', fontsize=9)
            ax2.set_xlabel('Intraday Swing (%)', color='white', fontsize=12)
            ax2.set_title('TOP MINING STOCKS BY SWING', color='white', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # Add percentages
            for bar, swing in zip(bars, swings):
                ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                        f'{swing:.2f}%', va='center', color='white', fontweight='bold', fontsize=8)
        
        # 3. Best vs Worst Time Scatter
        ax3 = plt.subplot(3, 3, 5)
        
        if stock_swings:
            best_returns = [data['best_return'] for data in stock_swings.values()]
            worst_returns = [data['worst_return'] for data in stock_swings.values()]
            prices = [data['price'] for data in stock_swings.values()]
            
            scatter = ax3.scatter(worst_returns, best_returns, c=prices, s=120, 
                                cmap='viridis', alpha=0.8, edgecolors='white', linewidth=1)
            
            ax3.axhline(0, color='white', alpha=0.5)
            ax3.axvline(0, color='white', alpha=0.5)
            ax3.plot([-1, 1], [-1, 1], 'yellow', linestyle='--', alpha=0.7, linewidth=2)
            
            ax3.set_xlabel('Worst Period Return (%)', color='white', fontsize=12)
            ax3.set_ylabel('Best Period Return (%)', color='white', fontsize=12)
            ax3.set_title('WORST vs BEST PERIODS - MINING STOCKS', color='white', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            
            # Colorbar
            cbar = plt.colorbar(scatter, ax=ax3)
            cbar.set_label('Stock Price ($)', color='white', fontsize=10)
            cbar.ax.tick_params(colors='white')
        
        # 4. Strategy Viability Pie Chart
        ax4 = plt.subplot(3, 3, 6)
        
        if stock_swings:
            swings_list = [data['swing'] for data in stock_swings.values()]
            
            strong_count = len([s for s in swings_list if s > 0.5])
            viable_count = len([s for s in swings_list if 0.3 < s <= 0.5])
            weak_count = len([s for s in swings_list if 0.1 < s <= 0.3])
            poor_count = len([s for s in swings_list if s <= 0.1])
            
            sizes = [strong_count, viable_count, weak_count, poor_count]
            labels = [f'Strong (>0.5%)\n{strong_count} stocks', 
                     f'Viable (0.3-0.5%)\n{viable_count} stocks',
                     f'Weak (0.1-0.3%)\n{weak_count} stocks', 
                     f'Poor (<0.1%)\n{poor_count} stocks']
            colors = ['darkgreen', 'green', 'gold', 'red']
            
            # Only include non-zero segments
            non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
            if non_zero:
                sizes, labels, colors = zip(*non_zero)
                
                ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax4.set_title('MINING STRATEGY VIABILITY', color='white', fontsize=14, fontweight='bold')
        
        # 5. Morning Dip Analysis
        ax5 = plt.subplot(3, 3, 7)
        
        morning_data = {}
        for period, returns in sector_periods.items():
            if period.startswith(('10:', '11:')):  # Morning periods
                morning_data[period] = np.mean(returns)
        
        if morning_data:
            periods = list(morning_data.keys())
            returns = list(morning_data.values())
            
            bars = ax5.bar(range(len(periods)), returns,
                          color=['red' if r < -0.05 else 'orange' if r < 0 else 'green' for r in returns],
                          alpha=0.8)
            
            ax5.set_xticks(range(len(periods)))
            ax5.set_xticklabels([p[-5:] for p in periods], rotation=45, color='white', fontsize=9)
            ax5.set_ylabel('Average Return (%)', color='white')
            ax5.set_title('MINING MORNING ANALYSIS', color='white', fontsize=14, fontweight='bold')
            ax5.axhline(0, color='white', alpha=0.5)
            ax5.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, val in zip(bars, returns):
                ax5.text(bar.get_x() + bar.get_width()/2., 
                        bar.get_height() + (0.01 if val > 0 else -0.03),
                        f'{val:.3f}%', ha='center', va='bottom' if val > 0 else 'top',
                        color='white', fontweight='bold', fontsize=8)
        
        # 6. Afternoon Rally Analysis  
        ax6 = plt.subplot(3, 3, 8)
        
        afternoon_data = {}
        for period, returns in sector_periods.items():
            if period.startswith(('13:', '14:')):  # Afternoon periods
                afternoon_data[period] = np.mean(returns)
        
        if afternoon_data:
            periods = list(afternoon_data.keys())
            returns = list(afternoon_data.values())
            
            bars = ax6.bar(range(len(periods)), returns,
                          color=['green' if r > 0.05 else 'orange' if r > 0 else 'red' for r in returns],
                          alpha=0.8)
            
            ax6.set_xticks(range(len(periods)))
            ax6.set_xticklabels([p[-5:] for p in periods], rotation=45, color='white', fontsize=9)
            ax6.set_ylabel('Average Return (%)', color='white')
            ax6.set_title('MINING AFTERNOON ANALYSIS', color='white', fontsize=14, fontweight='bold')
            ax6.axhline(0, color='white', alpha=0.5)
            ax6.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, val in zip(bars, returns):
                ax6.text(bar.get_x() + bar.get_width()/2., 
                        bar.get_height() + (0.01 if val > 0 else -0.03),
                        f'{val:.3f}%', ha='center', va='bottom' if val > 0 else 'top',
                        color='white', fontweight='bold', fontsize=8)
        
        # 7. Summary Statistics Box
        ax7 = plt.subplot(3, 3, 9)
        ax7.axis('off')
        
        if stock_swings and sector_periods:
            # Calculate summary stats
            avg_swing = np.mean([data['swing'] for data in stock_swings.values()])
            viable_stocks = len([s for s in stock_swings.values() if s['swing'] > 0.3])
            total_stocks = len(stock_swings)
            
            # Find best sector timing
            sector_avg = {period: np.mean(returns) for period, returns in sector_periods.items()}
            best_period = max(sector_avg.keys(), key=lambda x: sector_avg[x])
            worst_period = min(sector_avg.keys(), key=lambda x: sector_avg[x])
            sector_swing = sector_avg[best_period] - sector_avg[worst_period]
            
            # Best individual opportunity
            best_stock = max(stock_swings.keys(), key=lambda x: stock_swings[x]['swing'])
            best_swing = stock_swings[best_stock]['swing']
            
            summary_text = f"""
ASX MINING SECTOR TIME-OF-DAY ANALYSIS
COMPREHENSIVE SUMMARY

SECTOR STATISTICS:
• Mining Stocks Analyzed: {total_stocks}
• Total Observations: {sum(len(df) for stock_results in self.analyzer.all_results.values() for df in stock_results.values()):,}
• Average Stock Swing: {avg_swing:.2f}%
• Sector-Wide Swing: {sector_swing:.3f}%

OPTIMAL TIMING:
• Worst Time (Entry): {worst_period}
• Best Time (Exit): {best_period}
• Expected Sector Swing: {sector_swing:.3f}%

STRATEGY ASSESSMENT:
• Viable Strategies: {viable_stocks}/{total_stocks} stocks
• Success Rate: {viable_stocks/total_stocks*100:.0f}%
• Best Individual Opportunity: {best_stock.replace('.AX', '')}
• Maximum Swing: {best_swing:.2f}%

TRADING RECOMMENDATION:
{'✓ MINING SECTOR STRATEGY VIABLE' if viable_stocks >= total_stocks*0.4 else '△ SELECTIVE APPROACH' if viable_stocks > 0 else '✗ NOT RECOMMENDED'}
{'✓ Systematic timing strategy' if sector_swing > 0.2 else '△ Stock-specific approach' if viable_stocks > 0 else '✗ Avoid time-of-day trading'}

Risk Level: {'HIGH' if avg_swing > 0.8 else 'MEDIUM' if avg_swing > 0.4 else 'LOW'}
Position Size: {'5-10%' if viable_stocks >= total_stocks*0.5 else '2-5%' if viable_stocks > 0 else '1-2%'}
            """
            
            ax7.text(0.05, 0.95, summary_text, transform=ax7.transAxes,
                    fontsize=13, color='white', va='top', ha='left', family='monospace',
                    bbox=dict(boxstyle='round,pad=0.8', facecolor='darkblue', alpha=0.95))
        
        plt.suptitle('ASX MINING SECTOR COMPREHENSIVE TIME-OF-DAY TRADING ANALYSIS DASHBOARD', 
                     fontsize=24, color='white', fontweight='bold', y=0.98)
        plt.tight_layout()
        
        # Save mega dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Mining_TOD_Mega_Dashboard_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"\nMEGA mining dashboard saved: {filename}")
        
        plt.show()
        
        # Print key insights
        self.print_dashboard_summary(stock_swings, sector_periods)
    
    def print_dashboard_summary(self, stock_swings, sector_periods):
        """Print mining dashboard summary"""
        print(f"\n{'='*80}")
        print(f"ASX MINING TOD DASHBOARD SUMMARY")
        print(f"{'='*80}")
        
        if stock_swings:
            # Top 10 mining opportunities
            top_10 = sorted(stock_swings.items(), key=lambda x: x[1]['swing'], reverse=True)[:10]
            
            print(f"TOP 10 MINING OPPORTUNITIES:")
            for i, (ticker, data) in enumerate(top_10, 1):
                print(f"  {i:2d}. {ticker.replace('.AX', ''):<6}: {data['swing']:.2f}% swing (${data['price']:.2f})")
            
            # Sector summary
            viable = len([s for s in stock_swings.values() if s['swing'] > 0.3])
            avg_swing = np.mean([s['swing'] for s in stock_swings.values()])
            
            print(f"\nMINING SECTOR SUMMARY:")
            print(f"  Average Swing: {avg_swing:.2f}%")
            print(f"  Viable Strategies: {viable}/{len(stock_swings)} ({viable/len(stock_swings)*100:.0f}%)")
        
        if sector_periods:
            # Best timing
            sector_avg = {period: np.mean(returns) for period, returns in sector_periods.items()}
            best_time = max(sector_avg.keys(), key=lambda x: sector_avg[x])
            worst_time = min(sector_avg.keys(), key=lambda x: sector_avg[x])
            
            print(f"\nOPTIMAL MINING SECTOR TIMING:")
            print(f"  Entry: {worst_time} ({sector_avg[worst_time]:+.3f}%)")
            print(f"  Exit: {best_time} ({sector_avg[best_time]:+.3f}%)")
            print(f"  Expected: {sector_avg[best_time] - sector_avg[worst_time]:.3f}% swing")
        
        print(f"{'='*80}")

# Execute
if __name__ == "__main__":
    plotter = MiningTODPlotter()
    plotter.create_comprehensive_dashboard()
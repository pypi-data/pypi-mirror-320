import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
import numpy as np
import os
import matplotlib.dates as mdates
import matplotlib
import numpy as np

def rolling_ema(data, window):
    multiplier = 2 / (window + 1)
    ema_values = np.empty(len(data))
    ema_values[:window-1] = np.nan  
    ema_values[window-1] = np.mean(data[:window])
    for i in range(window, len(data)):
        ema_values[i] = (data[i] - ema_values[i - 1]) * multiplier + ema_values[i - 1]

    return ema_values

def rolling_wma(data, window):
    weights = np.arange(1, window + 1)
    return np.convolve(data, weights[::-1], mode='same') / weights.sum()

def load_data(file_path, start_time, end_time):
    df = pd.read_csv(file_path)
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)

    if start_time_ms is not None:
        df = df[df["start_time"] >= start_time_ms]
    if end_time_ms is not None:
        df = df[df["start_time"] < end_time_ms]
        
    df = df.reset_index(drop=True)
    df["price_chg"] = df["close"].pct_change()
    return df

def rolling_mean_normalize(df, rolling_window):
    df["sma"] = df["data"].rolling(window=rolling_window).mean()
    df["ema"] = rolling_ema(df["data"], rolling_window)
    df["wma"] = rolling_wma(df["data"], rolling_window)
    df["min"] = df["data"].rolling(window=rolling_window).min()
    df["max"] = df["data"].rolling(window=rolling_window).max()
    df["processed_data"] = (df["data"] - df["sma"]) / (df["max"] - df["min"] + 1e-9)
    return df

def rolling_zscore(df, rolling_window):
    df["sma"] = df["data"].rolling(window=rolling_window).mean()
    df["ema"] = rolling_ema(df["data"], rolling_window)
    df["wma"] = rolling_wma(df["data"], rolling_window)
    df["stddev"] = df["data"].rolling(window=rolling_window).std()
    df["processed_data"] = (df["data"] - df["sma"]) / df["stddev"]
    return df

def rolling_rsi(df, rolling_window):
    def calculate_rsi(series):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rolling_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rolling_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    df["rsi"] = calculate_rsi(df["data"])
    df["sma"] = df["rsi"].rolling(window=rolling_window).mean()
    df["ema"] = rolling_ema(df["data"], rolling_window)
    df["wma"] = rolling_wma(df["data"], rolling_window)
    df["processed_data"] = (df["rsi"] - 50) / 50 
    return df

def rolling_bollinger_bands(df, rolling_window, multiplier):
    df["sma"] = df["data"].rolling(window=rolling_window).mean()
    df["ema"] = rolling_ema(df["data"], rolling_window)
    df["wma"] = rolling_wma(df["data"], rolling_window)
    df["upper_band"] = df["sma"] + (multiplier * df["data"].rolling(window=rolling_window).std())
    df["lower_band"] = df["sma"] - (multiplier * df["data"].rolling(window=rolling_window).std())
    return df

def calculate_macd(df, short_window, long_window, signal_window=9):
    # Calculate the short-term and long-term EMA
    df["EMA_short"] = rolling_ema(df["data"], short_window)
    df["EMA_long"] = rolling_ema(df["data"], long_window)
    # Calculate MACD line
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    # Calculate Signal line
    df["Signal"] = rolling_ema(df["MACD"], signal_window)
    # Calculate Histogram
    df["Histogram"] = df["MACD"] - df["Signal"]
    return df

def entry_exit_threshold(df, rolling_window, threshold, backtest_mode):
    sma = df["sma"].values
    ema = df["ema"].values
    wma = df["wma"].values
    data = df["processed_data"].values
    position = [np.nan] * rolling_window  
    # entry exit logic
    # mr
    if backtest_mode == "mr": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr sma
    elif backtest_mode == "mr_sma":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == 1) or (
                data[i] <= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr ema
    elif backtest_mode == "mr_ema":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == 1) or (
                data[i] <= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr wma
    elif backtest_mode == "mr_wma":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == 1) or (
                data[i] <= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr 0
    elif backtest_mode == "mr_0":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < -threshold:
                position.append(1)
            # short
            elif data[i] > threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == 1) or (
                data[i] <= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # sma sideline
    elif backtest_mode == "sma_sideline": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > sma[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < sma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # ema sideline
    elif backtest_mode == "ema_sideline": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > ema[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < ema[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # wma sideline
    elif backtest_mode == "wma_sideline": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > wma[i] and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < wma[i] and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # 0 sideline
    elif backtest_mode == "0_sideline": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] > 0 and data[i] < threshold:
                position.append(1)
            # short
            elif data[i] < 0 and data[i] > -threshold:
                position.append(-1)
            # exit logic
            elif (data[i] >= threshold and position[i - 1] == 1) or (
                data[i] <= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum
    elif backtest_mode == "momentum": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum sideline
    elif backtest_mode == "momentum_sideline": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= threshold and position[i - 1] == 1) or (
                data[i] >= -threshold and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum 0
    elif backtest_mode == "momentum_0": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == 1) or (
                data[i] >= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    # momentum sma
    elif backtest_mode == "momentum_sma":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == 1) or (
                data[i] >= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum ema
    elif backtest_mode == "momentum_ema":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == 1) or (
                data[i] >= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum wma
    elif backtest_mode == "momentum_wma":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < -threshold:
                position.append(-1)
            # long
            elif data[i] > threshold:
                position.append(1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == 1) or (
                data[i] >= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    return position

def entry_exit_band(df, rolling_window, backtest_mode):
    upper_band = df["upper_band"].values
    lower_band = df["lower_band"].values
    sma = df["sma"].values
    ema = df["ema"].values
    wma = df["wma"].values
    data = df["data"].values
    position = [np.nan] * rolling_window  

    # mr
    if backtest_mode == "mr": 
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr sma
    elif backtest_mode == "mr_sma":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= sma[i] and position[i - 1] == 1) or (
                data[i] <= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr ema
    elif backtest_mode == "mr_ema":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= ema[i] and position[i - 1] == 1) or (
                data[i] <= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr wma
    elif backtest_mode == "mr_wma":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= wma[i] and position[i - 1] == 1) or (
                data[i] <= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # mr 0
    elif backtest_mode == "mr_0":
        for i in range(rolling_window, len(df)):
            # long
            if data[i] < lower_band[i]:
                position.append(1)
            # short
            elif data[i] > upper_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= 0 and position[i - 1] == 1) or (
                data[i] <= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # 0 sideline
    elif backtest_mode == "0_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > 0 and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < 0 and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # sma sideline
    elif backtest_mode == "sma_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > sma[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < sma[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # ema sideline
    elif backtest_mode == "ema_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > ema[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < ema[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # wma sideline
    elif backtest_mode == "wma_sideline": 
        for i in range(rolling_window, len(data)):
            # long
            if data[i] > wma[i] and data[i] < upper_band[i]:
                position.append(1)
            # short
            elif data[i] < wma[i] and data[i] > lower_band[i]:
                position.append(-1)
            # exit logic
            elif (data[i] >= upper_band[i] and position[i - 1] == 1) or (
                data[i] <= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum
    elif backtest_mode == "momentum": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum sideline
    elif backtest_mode == "momentum_sideline": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= upper_band[i] and position[i - 1] == 1) or (
                data[i] >= lower_band[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum 0
    elif backtest_mode == "momentum_0": 
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= 0 and position[i - 1] == 1) or (
                data[i] >= 0 and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position    
            else:
                position.append(position[i - 1])
    # momentum sma
    elif backtest_mode == "momentum_sma":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= sma[i] and position[i - 1] == 1) or (
                data[i] >= sma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum ema
    elif backtest_mode == "momentum_ema":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= ema[i] and position[i - 1] == 1) or (
                data[i] >= ema[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    # momentum wma
    elif backtest_mode == "momentum_wma":
        for i in range(rolling_window, len(df)):
            # short
            if data[i] < lower_band[i]:
                position.append(-1)
            # long
            elif data[i] > upper_band[i]:
                position.append(1)
            # exit logic
            elif (data[i] <= wma[i] and position[i - 1] == 1) or (
                data[i] >= wma[i] and position[i - 1] == -1
            ):
                position.append(0)
            # follow last position
            else:
                position.append(position[i - 1])
    return position
   
def entry_exit_macd(df, rolling_window1, rolling_window2):
    rolling_window = rolling_window1 if rolling_window1 > rolling_window2 else rolling_window2
    position = [np.nan] * rolling_window  
    macd = df["MACD"].values
    signal = df["Signal"].values
    for i in range(rolling_window, len(df)):
            # long
            if macd[i] >= signal[i]:
                position.append(1)
            # short
            elif macd[i] <= signal[i]:
                position.append(-1)
            # follow last position
            else:
                position.append(position[i - 1])
    return position
   
def generate_report(df, param1, param2, fees, sr_multiplier):
    # Calculate trades and PnL
    df["trades"] = abs(df["pos"] - df["pos"].shift(1))
    df["pnl"] = df["price_chg"] * df["pos"].shift(1) - df["trades"] * fees / 100.0
    df["cumu"] = df["pnl"].cumsum()

    # Sharpe Ratio
    sharp_ratio = df["pnl"].mean() / df["pnl"].std() * np.sqrt(365 * sr_multiplier) if df["pnl"].std() != 0 else 0

    # Maximum drawdown and recovery period
    df["cumu_max"] = df["cumu"].cummax()
    df["drawdown"] = df["cumu"] - df["cumu_max"]
    mdd = df["drawdown"].min()

    recovery_period_days = None  # Default when no recovery occurs
    if mdd < 0:  # Proceed only if a drawdown exists
        # Find the start of the maximum drawdown
        mdd_start_idx = df[df["drawdown"] == mdd].index[0]

        # Find recovery index (if exists)
        recovery_idxs = df[(df.index > mdd_start_idx) & (df["cumu"] >= df.loc[mdd_start_idx, "cumu_max"])].index

        if len(recovery_idxs) > 0:
            recovery_period = recovery_idxs[0] - mdd_start_idx

            # Convert to days
            if isinstance(df.index, pd.DatetimeIndex):
                recovery_period_days = recovery_period.total_seconds() / (3600 * 24)
            else:
                recovery_period_days = recovery_period / 24  # Assume each step in the index represents 1 hour

    # Annualized return and Calmar Ratio
    ar = df["pnl"].mean() * 365 * sr_multiplier
    cr = ar / abs(mdd) if mdd != 0 else float('inf')

    # Total trades
    trades_count = df["trades"].sum()

    # Generate report
    report = {
        "param1": param1,
        "param2": param2,
        "SR": sharp_ratio,
        "CR": cr,
        "MDD": mdd,
        "Recovery Period (days)": recovery_period_days,
        "Trades": trades_count,
        "AR": ar,
        "Trades Ratio": trades_count / len(df),
    }
    return report

def plot_single_diagram(df, report_df):
    matplotlib.use('TkAgg')  # Change this based on your system, e.g., 'Qt5Agg'
    pivot_table = report_df.pivot(
        index="param1", columns="param2", values="SR"
    )
    plt.figure(figsize=(30, 10))
    sns.heatmap(pivot_table, annot=True, cmap="RdYlGn")
    # Plot setup
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Cumulative Return on the left y-axis
    line1, = ax1.plot(df['datetime'], df['cumu'], label='Cumulative Return (Buy and Hold)', color='red')
    ax1.set_ylabel('Cumulative Return', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.legend(loc="upper left")
    ax1.grid(True)

    # Create a secondary y-axis for BTC Close Price
    ax2 = ax1.twinx()
    line2, = ax2.plot(df['datetime'], df['close'], label='Close Price', color='blue')
    ax2.set_ylabel('Close Price', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.legend(loc="lower right")

    # Set the title and x-axis labels
    plt.title('Cumulative Return and Close Price Over Time')
    ax1.set_xlabel('Date')

    # Customize date ticks for readability
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=12))

    # Rotate x-axis labels and apply auto format to prevent overlapping
    fig.autofmt_xdate(rotation=45)

    # Identify MDD points: peak and trough
    trough_index = df["drawdown"].idxmin()  # Index of the trough (lowest drawdown point)
    trough_value = df["cumu"].iloc[trough_index]
    trough_date = df["datetime"].iloc[trough_index]

    peak_index = df["cumu"][:trough_index].idxmax()  # Peak before the trough
    peak_value = df["cumu"].iloc[peak_index]
    peak_date = df["datetime"].iloc[peak_index]

    # Plot the peak and trough
    ax1.scatter(peak_date, peak_value, color='orange', zorder=5, label="Peak (Before MDD)")
    ax1.scatter(trough_date, trough_value, color='green', zorder=5, label="Trough (MDD)")

    # Add vertical lines to mark the MDD period
    ax1.axvline(peak_date, color='orange', linestyle='--', linewidth=1, label="Peak Date")
    ax1.axvline(trough_date, color='green', linestyle='--', linewidth=1, label="Trough Date")

    # Add a legend for the MDD points
    ax1.legend(loc="upper left")

    # Make the plot interactive (hover functionality)
    annot = ax1.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(line, ind):
        """Update annotation based on hover index."""
        x, y = line.get_xdata()[ind["ind"][0]], line.get_ydata()[ind["ind"][0]]
        annot.xy = (x, y)
        annot.set_text(f"Date: {mdates.num2date(x).strftime('%Y-%m-%d %H:%M')}\nValue: {y:.2f}")
        annot.get_bbox_patch().set_alpha(0.8)

    def on_hover(event):
        """Display annotation on hover."""
        vis = annot.get_visible()
        for line in [line1, line2]:
            cont, ind = line.contains(event)
            if cont:
                update_annot(line, ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
                return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_hover)

    plt.tight_layout()
    plt.show()
    
def plot_heatmap(report_df):
    pivot_table = report_df.pivot(
        index="param1", columns="param2", values="SR"
    )
    plt.figure(figsize=(30, 10))
    sns.heatmap(pivot_table, annot=True, cmap="RdYlGn")
    plt.show()   
    
def plot_data_spread(df):
    # Create the figure and primary axis
    fig, ax1 = plt.subplots(figsize=(20, 9))

    # Scatter plot for 'data' on the left y-axis
    ax1.scatter(df['datetime'], df['data'], label='Data Spread', color='red', marker='o', s=3)
    ax1.set_ylabel('Raw Data', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.legend(loc="upper left")
    ax1.grid(True)

    # Create a secondary y-axis for Close Price
    ax2 = ax1.twinx()
    ax2.plot(df['datetime'], df['close'], label='Close Price', color='blue')
    ax2.set_ylabel('Close Price', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.legend(loc="lower right")

    # Set the title and x-axis labels
    plt.title('Data Spread and Close Price over Time')
    ax1.set_xlabel('Date')
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=12))
    fig.autofmt_xdate(rotation=45)

    # Adjust layout to avoid overlap
    plt.tight_layout()

    # Show the plot
    plt.show()

def mean_normalize_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode):
    rolling_mean_normalize(df, rolling_window)
    df["pos"] = entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    report = generate_report(df, rolling_window, threshold, fees, sr_multiplier)
    return report

def mean_normalize(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier):
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"Mean_Normalize-backtest mode: {backtest_mode}")
            for rolling_window in rolling_window_range:
                for threshold in threshold_range:
                    report = mean_normalize_backtesting(
                        df=df,
                        rolling_window=rolling_window,
                        threshold=threshold,
                        fees=fees,
                        sr_multiplier=sr_multiplier,
                        backtest_mode=backtest_mode,
                    )
                    all_report.append(report)
            report_df = pd.DataFrame(all_report)
            file_name = f"Mean_Normalize-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_path = Path(os.path.join(r"result\Mean_Normalize", file_name))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            report_df.to_csv(file_path) 
            plot_heatmap(report_df)
    else:
        all_report = []
        print(f"Mean_Normalize-backtest mode: {backtest_mode_list}")
        report = mean_normalize_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"Mean_Normalize-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\Mean_Normalize", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 
        file_name1 = f"Mean_Normalize-Position-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\Mean_Normalize", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        plot_single_diagram(df, report_df)

def bollinger_bands_backtesting(df, rolling_window, multiplier, fees, sr_multiplier, backtest_mode):
    # models
    rolling_bollinger_bands(df, rolling_window, multiplier)
    df["pos"] = entry_exit_band(df, rolling_window, backtest_mode)
    report = generate_report(df, rolling_window, multiplier, fees, sr_multiplier)
    return report

def bollinger_bands(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier):
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"Bollinger_Bands-backtest mode: {backtest_mode}")
            for rolling_window in rolling_window_range:
                for threshold in threshold_range:
                    report = bollinger_bands_backtesting(
                        df=df,
                        rolling_window=rolling_window,
                        multiplier=threshold,
                        fees=fees,
                        sr_multiplier=sr_multiplier,
                        backtest_mode=backtest_mode,
                    )
                    all_report.append(report)
            report_df = pd.DataFrame(all_report)
            file_name = f"Bollinger_Bands-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_path = Path(os.path.join(r"result\Bollinger_Bands", file_name))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            report_df.to_csv(file_path) 
            plot_heatmap(report_df)
    else:
        all_report = []
        print(f"Bollinger_Bands-backtest mode: {backtest_mode_list}")
        report = bollinger_bands_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            multiplier=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"Bollinger_Bands-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\Bollinger_Bands", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 
        file_name1 = f"Bollinger_Bands-Position-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\Bollinger_Bands", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        plot_single_diagram(df, report_df)
        
def rsi_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode):
    rolling_rsi(df, rolling_window)
    df["pos"] = entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    report = generate_report(df, rolling_window, threshold, fees, sr_multiplier)
    return report

def rsi(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier):
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"RSI-backtest mode: {backtest_mode}")
            for rolling_window in rolling_window_range:
                for threshold in threshold_range:
                    report = rsi_backtesting(
                        df=df,
                        rolling_window=rolling_window,
                        threshold=threshold,
                        fees=fees,
                        sr_multiplier=sr_multiplier,
                        backtest_mode=backtest_mode,
                    )
                    all_report.append(report)
            report_df = pd.DataFrame(all_report)
            file_name = f"RSI-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_path = Path(os.path.join(r"result\RSI", file_name))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            report_df.to_csv(file_path) 
            plot_heatmap(report_df)
    else:
        all_report = []
        print(f"RSI-backtest mode: {backtest_mode_list}")
        report = rsi_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"RSI-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\RSI", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 

        file_name1 = f"RSI-Position-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\RSI", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)

        plot_single_diagram(df, report_df)
        
def zscore_backtesting(df, rolling_window, threshold, fees, sr_multiplier, backtest_mode):
    rolling_zscore(df, rolling_window)
    df["pos"] = entry_exit_threshold(df, rolling_window, threshold, backtest_mode)
    report = generate_report(df, rolling_window, threshold, fees, sr_multiplier)
    return report

def zscore(df, backtest_mode_list, rolling_window_range, threshold_range, fees, sr_multiplier):
    if (isinstance(rolling_window_range,(np.generic, np.ndarray)) and isinstance(threshold_range,(np.generic, np.ndarray))):
        for backtest_mode in backtest_mode_list:
            all_report = []
            print(f"ZScore-backtest mode: {backtest_mode}")
            for rolling_window in rolling_window_range:
                for threshold in threshold_range:
                    report = zscore_backtesting(
                        df=df,
                        rolling_window=rolling_window,
                        threshold=threshold,
                        fees=fees,
                        sr_multiplier=sr_multiplier,
                        backtest_mode=backtest_mode,
                    )
                    all_report.append(report)
            report_df = pd.DataFrame(all_report)
            pivot_table = report_df.pivot(
                index="param1", columns="param2", values="SR"
            )
            file_name = f"ZScore-{backtest_mode}.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
            file_path = Path(os.path.join(r"result\ZScore", file_name))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            report_df.to_csv(file_path) 
            plt.figure(figsize=(30, 10))
            sns.heatmap(pivot_table, annot=True, cmap="RdYlGn")
            plt.show()
    else:
        all_report = []
        print(f"ZScore-backtest mode: {backtest_mode_list}")
        report = zscore_backtesting(
            df=df,
            rolling_window=rolling_window_range,
            threshold=threshold_range,
            fees=fees,
            sr_multiplier=sr_multiplier,
            backtest_mode=backtest_mode_list,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"ZScore-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\ZScore", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path)
        file_name1 = f"ZScore-Position-{backtest_mode_list}.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\ZScore", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        plot_single_diagram(df, report_df)
        
def macd_backtesting(df, rolling_window1, rolling_window2, fees, sr_multiplier):
    calculate_macd(df, rolling_window1, rolling_window2)
    df["pos"] = entry_exit_macd(df, rolling_window1, rolling_window2)
    report = generate_report(df, rolling_window1, rolling_window2, fees, sr_multiplier)
    return report

def macd(df, rolling_window1, rolling_window2, fees, sr_multiplier):
    if (isinstance(rolling_window1,(np.generic, np.ndarray)) and isinstance(rolling_window2,(np.generic, np.ndarray))):
        all_report = []
        print(f"MACD-backtest")
        for rolling1 in rolling_window1:
            for rolling2 in rolling_window2:                
                report = macd_backtesting(
                    df=df,
                    rolling_window1=rolling1,
                    rolling_window2=rolling2,
                    fees=fees,
                    sr_multiplier=sr_multiplier,
                )
                all_report.append(report)
        report_df = pd.DataFrame(all_report)
        pivot_table = report_df.pivot(
            index="param1", columns="param2", values="SR"
        )
        file_name = f"MACD.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\MACD", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path) 
        plt.figure(figsize=(30, 10))
        sns.heatmap(pivot_table, annot=True, cmap="RdYlGn")
        plt.show()
    else:
        all_report = []
        print(f"MACD-backtest")
        report = macd_backtesting(
            df=df,
            rolling_window1=rolling1,
            rolling_window2=rolling2,
            fees=fees,
            sr_multiplier=sr_multiplier,
        )
        all_report.append(report)
        report_df = pd.DataFrame(all_report)
        file_name = f"MACD.csv" # modify file name, e.g f"{backtest_mode}-premium_index.csv" or f"{backtest_mode}-blablabla.csv". only modify blablabla
        file_path = Path(os.path.join(r"result\MACD", file_name))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(file_path)
        file_name1 = f"MACD-Position.csv" # modify file name, e.g f"{backtest_mode_list}-premium_index.csv" or f"{backtest_mode_list}-blablabla.csv". only modify blablabla
        file_path1 = Path(os.path.join(r"result\MACD", file_name1))
        file_path1.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path1)
        plot_single_diagram(df, report_df)
        
def plot_correlation(file_paths, start_time, end_time):
    returns_list = []

    # Load each CSV, calculate periodic returns, and store them in the list
    for i, (file_path, leverage) in enumerate(file_paths):
        try:
            strategy_data = load_data(file_path, start_time=start_time, end_time=end_time)
            
            if 'cumu' not in strategy_data.columns or 'datetime' not in strategy_data.columns:
                raise ValueError(f"'cumu' or 'datetime' column not found in {file_path}")
            
            # Extract cumulative returns and time
            cumulative_returns = strategy_data['cumu'].values
            time = strategy_data['datetime'].values[1:]  # Adjust for periodic returns
            
            # Calculate periodic returns
            periodic_returns = cumulative_returns[1:] / cumulative_returns[:-1] - 1
            
            # Create a DataFrame for periodic returns
            strategy_returns = pd.DataFrame({
                'datetime': time,
                f'Strategy_{i+1}': periodic_returns
            })
            
            returns_list.append(strategy_returns)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    merged_returns = returns_list[0]
    for other in returns_list[1:]:
        merged_returns = pd.merge(merged_returns, other, on='datetime', how='inner')

    # Drop the 'Time' column for correlation computation
    merged_returns.drop(columns=['datetime'], inplace=True)

    # Compute the correlation matrix
    correlation_matrix = merged_returns.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
    plt.title("Correlation Matrix Heatmap")
    plt.show()

def plot_combined_equity(file_paths, start_time, end_time):
    def process_file(file_path, leverage):
        """Process a single file to calculate PnL and cumulative returns."""
        df = load_data(file_path, start_time=start_time, end_time=end_time)
        df['new_pos'] = df['pos'] * leverage
        df['new_trades'] = abs(df['new_pos'] - df['new_pos'].shift(1))
        df['new_pnl'] = df['price_chg'] * df['new_pos'].shift(1) - df['new_trades'] * 0.06 / 100.0
        df['new_cumu'] = df['new_pnl'].cumsum()
        return df[['datetime', 'new_pnl', 'new_cumu', 'close']]  # Include close data

    def calculate_drawdown_and_recovery(cumu_series):
        """Calculate max drawdown and recovery period."""
        cumu_max = cumu_series.cummax()
        drawdown = cumu_series - cumu_max
        mdd = drawdown.min()

        if mdd < 0:
            # Index of the maximum drawdown
            mdd_start_idx = drawdown.idxmin()

            # Find recovery index (if exists)
            recovery_idxs = cumu_series[
                (cumu_series.index > mdd_start_idx) & (cumu_series >= cumu_max[mdd_start_idx])
            ].index

            if len(recovery_idxs) > 0:
                recovery_period = recovery_idxs[0] - mdd_start_idx

                # Convert to days if using DatetimeIndex
                if isinstance(cumu_series.index, pd.DatetimeIndex):
                    recovery_period_days = recovery_period.total_seconds() / (3600 * 24)
                else:
                    recovery_period_days = recovery_period / 24  # Assume 1 step = 1 hour
            else:
                recovery_period_days = None
        else:
            recovery_period_days = None

        return mdd, recovery_period_days

    cumu_list, pnl_list = [], []
    close_list = []  # List to store the close data

    # Process each file
    for i, (file_path, leverage) in enumerate(file_paths):
        try:
            df = process_file(file_path, leverage)
            cumu_list.append(df[['datetime', 'new_cumu']].rename(columns={'new_cumu': f'Cumu_{i + 1}'}))
            pnl_list.append(df[['datetime', 'new_pnl']].rename(columns={'new_pnl': f'PNL_{i + 1}'}))
            close_list.append(df[['datetime', 'close']].rename(columns={'close': f'Close_{i + 1}'}))  # Store close data
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Merge PnL data and calculate total PnL
    pnl_merge = pd.concat(pnl_list, axis=1).drop_duplicates(subset=['datetime'])
    total_pnl = pnl_merge.drop(columns=['datetime']).sum(axis=1)

    # Compute metrics
    sharp_ratio = total_pnl.mean() / total_pnl.std() * np.sqrt(365 * 24) if total_pnl.std() != 0 else 0
    ar = total_pnl.mean() * 365 * 24  # Annualized return
    total_cumu = total_pnl.cumsum()
    mdd, recovery_period = calculate_drawdown_and_recovery(total_cumu)
    cr = ar / abs(mdd) if mdd != 0 else float('inf')

    # Print report
    print({
        "SR": sharp_ratio,
        "CR": cr,
        "MDD": mdd,
        "Recovery Period (days)": recovery_period,
        "AR": ar,
    })

    # Merge cumulative returns and plot
    merged_cumu = cumu_list[0]
    for other in cumu_list[1:]:
        merged_cumu = pd.merge(merged_cumu, other, on=['datetime'], how='inner')
    merged_returns_without_datetime = merged_cumu.drop(columns=['datetime'])

    # Sum the cumulative returns across all strategies
    total_cumulative_returns = merged_returns_without_datetime.sum(axis=1)
    fig, ax1 = plt.subplots(figsize=(20, 8))

    # Plot total cumulative returns and individual strategies on left y-axis
    ax1.plot(merged_cumu['datetime'], total_cumulative_returns, label='Total Cumulative Returns', color='red', linewidth=2)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Cumulative Return")
    ax1.set_title("Total Cumulative Returns and Close Price")
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Create second y-axis for close data (from the first file)
    ax2 = ax1.twinx()
    # Use the 'close' data from the first file (index 0)
    merged_close = close_list[0]

    # Plot close data on right y-axis
    ax2.plot(merged_close['datetime'], merged_close['Close_1'], label='Close', color='blue')
    ax2.set_ylabel("Close Price")
    ax2.legend(loc='upper right')
    
    fig, axa = plt.subplots(figsize=(20, 8))

    for col in merged_cumu.columns:
        if col != 'datetime':
            axa.plot(merged_cumu['datetime'], merged_cumu[col], label=col, linestyle='--')
    axa.set_xlabel("Time")
    axa.set_ylabel("Cumulative Return")
    axa.set_title("Cumulative Returns of Each Strategy and BTC Close")
    axa.legend(loc='upper left')
    axa.grid(True)
    # Create second y-axis for close data (from the first file)
    axb = axa.twinx()
    # Use the 'close' data from the first file (index 0)
    merged_close = close_list[0]

    # Plot close data on right y-axis
    axb.plot(merged_close['datetime'], merged_close['Close_1'], label='Close', color='blue')
    axb.set_ylabel("Close Price")
    axb.legend(loc='upper right')

    plt.tight_layout()
    plt.show()


import pandas as pd
import numpy as np

def predict_future(df: pd.DataFrame, column: str, periods: int = 30) -> pd.DataFrame:
    """Predict by repeating historical pattern with trend adjustment"""
    series = df[column].dropna().values
    n = len(series)
    
    # Get the pattern to repeat (use last N days where N = periods, or full history if shorter)
    pattern_length = min(periods, n)
    pattern = series[-pattern_length:]
    
    # Calculate trend adjustment (shift pattern to start from last value)
    last_value = series[-1]
    pattern_start = pattern[0]
    offset = last_value - pattern_start
    
    # Also add slight trend continuation
    trend = (series[-1] - series[-min(30, n)]) / min(30, n) if n > 1 else 0
    
    # Generate predictions by repeating pattern
    predictions = []
    for i in range(periods):
        idx = i % pattern_length
        base_value = pattern[idx] + offset + (trend * (i + 1) * 0.5)
        predictions.append(base_value)
    
    # Confidence bands
    std = np.std(series[-min(30, n):])
    base = np.array(predictions)
    
    # Future dates
    last_date = df['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)
    
    return pd.DataFrame({
        'date': future_dates,
        'predicted': base,
        'best_case': base + std,
        'worst_case': base - std,
        'confidence_lower': base - std * 0.5,
        'confidence_upper': base + std * 0.5
    })

def get_trend_direction(df: pd.DataFrame, column: str) -> dict:
    """Get trend summary"""
    series = df[column].dropna()
    n = len(series)
    recent = min(30, n)
    slope = (series.iloc[-1] - series.iloc[-recent]) / recent if n > 1 else 0
    pct_change = (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100
    
    return {
        'direction': 'up' if slope > 0 else 'down',
        'slope': round(slope, 4),
        'total_change_pct': round(pct_change, 2)
    }

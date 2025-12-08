import pandas as pd
import numpy as np

def detect_seasonality(df: pd.DataFrame, column: str) -> dict:
    """Detect weekly and monthly patterns"""
    data = df.copy()
    data['dayofweek'] = data['date'].dt.dayofweek
    data['month'] = data['date'].dt.month
    
    # Weekly pattern
    weekly = data.groupby('dayofweek')[column].mean()
    weekly_strength = (weekly.max() - weekly.min()) / weekly.mean() * 100
    
    # Monthly pattern
    monthly = data.groupby('month')[column].mean()
    monthly_strength = (monthly.max() - monthly.min()) / monthly.mean() * 100
    
    return {
        'weekly': {
            'pattern': weekly.to_dict(),
            'strength': round(weekly_strength, 2),
            'peak_day': int(weekly.idxmax()),
            'low_day': int(weekly.idxmin())
        },
        'monthly': {
            'pattern': monthly.to_dict(),
            'strength': round(monthly_strength, 2),
            'peak_month': int(monthly.idxmax()),
            'low_month': int(monthly.idxmin())
        }
    }

def get_seasonal_component(df: pd.DataFrame, column: str) -> pd.Series:
    """Extract seasonal component from data"""
    data = df.copy()
    data['dayofweek'] = data['date'].dt.dayofweek
    weekly_avg = data.groupby('dayofweek')[column].transform('mean')
    overall_avg = data[column].mean()
    return weekly_avg - overall_avg

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_csv(file) -> pd.DataFrame:
    """Load and validate CSV file"""
    df = pd.read_csv(file)
    
    # Find date column
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
        df = df.rename(columns={date_cols[0]: 'date'})
    
    return df

def validate_data(df: pd.DataFrame) -> tuple:
    """Validate dataframe format. Returns (is_valid, message)"""
    if df.empty:
        return False, "Dataset is empty"
    
    if 'date' not in df.columns:
        return False, "No date column found"
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        return False, "No numeric columns found"
    
    return True, f"Valid dataset with {len(numeric_cols)} numeric columns"

def get_numeric_columns(df: pd.DataFrame) -> list:
    """Get list of numeric columns (excluding date)"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def generate_sample_data() -> pd.DataFrame:
    """Generate sample dataset for demo"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    n = len(dates)
    
    # Create realistic patterns
    trend = np.linspace(100, 150, n)
    weekly = 10 * np.sin(np.arange(n) * 2 * np.pi / 7)
    monthly = 15 * np.sin(np.arange(n) * 2 * np.pi / 30)
    noise = np.random.randn(n) * 5
    
    df = pd.DataFrame({
        'date': dates,
        'Product_A': trend + weekly + noise + 100,
        'Product_B': trend * 0.8 + monthly + noise + 80,
        'Product_C': trend * 1.2 + weekly + monthly + noise + 120
    })
    
    # Add some anomalies
    anomaly_idx = np.random.choice(n, 10, replace=False)
    df.loc[anomaly_idx, 'Product_A'] *= 1.5
    
    return df.round(2)

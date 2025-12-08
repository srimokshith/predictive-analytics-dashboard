import pandas as pd
import numpy as np

def detect_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.0) -> pd.DataFrame:
    """Detect anomalies using z-score method"""
    series = df[column]
    mean = series.mean()
    std = series.std()
    
    z_scores = np.abs((series - mean) / std)
    anomalies = df[z_scores > threshold].copy()
    anomalies['z_score'] = z_scores[z_scores > threshold]
    anomalies['deviation'] = ((anomalies[column] - mean) / mean * 100).round(2)
    
    return anomalies[['date', column, 'z_score', 'deviation']]

def get_anomaly_summary(df: pd.DataFrame, column: str, threshold: float = 2.0) -> dict:
    """Get summary of anomalies"""
    anomalies = detect_anomalies(df, column, threshold)
    
    if anomalies.empty:
        return {'count': 0, 'anomalies': []}
    
    return {
        'count': len(anomalies),
        'percentage': round(len(anomalies) / len(df) * 100, 2),
        'max_deviation': anomalies['deviation'].abs().max(),
        'anomalies': anomalies.to_dict('records')
    }

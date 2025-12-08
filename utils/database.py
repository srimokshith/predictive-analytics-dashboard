import sys
sys.path.append('..')
from config.supabase_config import get_supabase_client
import pandas as pd
from datetime import datetime

def save_dataset(name: str, df: pd.DataFrame) -> dict:
    """Save dataset info to Supabase"""
    supabase = get_supabase_client()
    
    data = {
        "name": name,
        "upload_date": datetime.now().isoformat(),
        "columns": list(df.columns),
        "row_count": len(df)
    }
    
    result = supabase.table("datasets").insert(data).execute()
    return result.data[0] if result.data else None

def get_all_datasets() -> list:
    """Get all datasets from Supabase"""
    supabase = get_supabase_client()
    result = supabase.table("datasets").select("*").order("upload_date", desc=True).execute()
    return result.data

def delete_dataset(dataset_id: str) -> bool:
    """Delete a dataset"""
    supabase = get_supabase_client()
    supabase.table("datasets").delete().eq("id", dataset_id).execute()
    return True

def save_predictions(dataset_id: str, predictions: list) -> bool:
    """Save predictions to Supabase"""
    supabase = get_supabase_client()
    
    for pred in predictions:
        pred["dataset_id"] = dataset_id
        pred["created_at"] = datetime.now().isoformat()
    
    supabase.table("predictions").insert(predictions).execute()
    return True

def get_predictions(dataset_id: str) -> list:
    """Get predictions for a dataset"""
    supabase = get_supabase_client()
    result = supabase.table("predictions").select("*").eq("dataset_id", dataset_id).execute()
    return result.data

def save_anomalies(dataset_id: str, anomalies: list) -> bool:
    """Save anomalies to Supabase"""
    supabase = get_supabase_client()
    
    for anomaly in anomalies:
        anomaly["dataset_id"] = dataset_id
    
    supabase.table("anomalies").insert(anomalies).execute()
    return True

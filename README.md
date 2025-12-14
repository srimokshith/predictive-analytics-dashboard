# 📊 Predictive Analytics Dashboard

Interactive dashboard for trend-based predictions, seasonality detection, and anomaly analysis..

## Features
- 📈 Historical data visualization
- 🔮 Trend-based forecasting (7-90 days)
- 📊 Weekly & monthly seasonality patterns
- ⚠️ Anomaly detection with adjustable threshold
- 📊 Multi-product comparison
- 💡 Auto-generated insights
- 🔗 Correlation analysis
- 📥 Export predictions to CSV

## Tech Stack
- **Frontend:** Streamlit + Plotly
- **Backend:** Supabase (PostgreSQL)
- **Hosting:** Render.com

## Local Setup
```bash
cd predictive_analytics_dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment (Render)
1. Push to GitHub
2. Connect repo to Render
3. Set environment variables (SUPABASE_URL, SUPABASE_KEY)
4. Deploy

## Project Structure
```
├── app.py                 # Main application
├── config/
│   └── supabase_config.py # Database connection
├── models/
│   ├── predictor.py       # Trend predictions
│   ├── seasonality.py     # Pattern detection
│   └── anomaly_detector.py# Outlier detection
├── utils/
│   ├── data_loader.py     # CSV handling
│   └── database.py        # CRUD operations
└── assets/
    └── style.css          # Custom styling
```

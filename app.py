import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

from utils.data_loader import load_csv, validate_data, get_numeric_columns, generate_sample_data
from models.predictor import predict_future, get_trend_direction
from models.seasonality import detect_seasonality
from models.anomaly_detector import get_anomaly_summary

st.set_page_config(page_title="Predictive Analytics Dashboard", page_icon="📊", layout="wide")

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Session state
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar
st.sidebar.title("📊 Analytics Dashboard")
st.sidebar.caption("Upload data and explore predictions")

@st.cache_data
def get_sample_data():
    return generate_sample_data()

# Data source
data_source = st.sidebar.radio("Data Source", ["Upload CSV", "Sample Data"], help="Upload your own CSV or use demo data")

if data_source == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV", type=['csv'])
    if uploaded:
        st.session_state.df = load_csv(uploaded)
else:
    if st.sidebar.button("Load Sample Data") or st.session_state.df is not None:
        if st.session_state.df is None:
            st.session_state.df = get_sample_data()

df = st.session_state.df

# Main content
st.title("📈 Predictive Analytics Dashboard")

if df is None:
    st.info("👈 Upload a CSV file or load sample data to get started")
    st.stop()

# Validate
valid, msg = validate_data(df)
if not valid:
    st.error(msg)
    st.stop()

# Column selection
numeric_cols = get_numeric_columns(df)
selected_col = st.sidebar.selectbox("Select Column", numeric_cols, help="Choose which metric to analyze")
forecast_days = st.sidebar.slider("Forecast Days", 7, 90, 30, help="Number of days to predict")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔮 Predictions", "📊 Seasonality", "⚠️ Anomalies"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Records", len(df))
    col2.metric("Average", f"{df[selected_col].mean():.2f}")
    col3.metric("Min", f"{df[selected_col].min():.2f}")
    col4.metric("Max", f"{df[selected_col].max():.2f}")
    
    # Historical chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df[selected_col], name='Historical', 
                             line=dict(color='#00D4FF', width=2),
                             fill='tozeroy', fillcolor='rgba(0,212,255,0.1)'))
    fig.update_layout(
        title=f"{selected_col} - Historical Data",
        xaxis_title="Date", yaxis_title="Value", height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        font=dict(color='#ccd6f6')
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    predictions = predict_future(df, selected_col, forecast_days)
    trend = get_trend_direction(df, selected_col)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Trend", trend['direction'].upper(), f"{trend['total_change_pct']}%")
    col2.metric("Next Day", f"{predictions.iloc[0]['predicted']:.2f}")
    col3.metric(f"Day {forecast_days}", f"{predictions.iloc[-1]['predicted']:.2f}")
    
    # Prediction chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df[selected_col], name='Historical', 
                             line=dict(color='#00D4FF', width=2)))
    fig.add_trace(go.Scatter(x=predictions['date'], y=predictions['predicted'], name='Predicted', 
                             line=dict(color='#00FF88', width=3)))
    fig.add_trace(go.Scatter(x=predictions['date'], y=predictions['best_case'], name='Best Case', 
                             line=dict(color='#00FF88', width=1, dash='dot'), opacity=0.5))
    fig.add_trace(go.Scatter(x=predictions['date'], y=predictions['worst_case'], name='Worst Case', 
                             line=dict(color='#FF6B6B', width=1, dash='dot'), opacity=0.5))
    fig.update_layout(
        title=f"{selected_col} - {forecast_days} Day Forecast", height=450,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        font=dict(color='#ccd6f6'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    season = detect_seasonality(df, selected_col)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Weekly Pattern")
        st.metric("Strength", f"{season['weekly']['strength']}%")
        weekly_data = [season['weekly']['pattern'].get(i, 0) for i in range(7)]
        fig = go.Figure(go.Bar(x=days, y=weekly_data, marker=dict(color=weekly_data, colorscale='Viridis')))
        fig.update_layout(height=300, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📆 Monthly Pattern")
        st.metric("Strength", f"{season['monthly']['strength']}%")
        monthly_data = [season['monthly']['pattern'].get(i, 0) for i in range(1, 13)]
        fig = go.Figure(go.Bar(x=months, y=monthly_data, marker=dict(color=monthly_data, colorscale='Plasma')))
        fig.update_layout(height=300, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)')
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    threshold = st.slider("Anomaly Threshold (Z-score)", 1.5, 4.0, 2.5, 0.5)
    summary = get_anomaly_summary(df, selected_col, threshold)
    
    col1, col2 = st.columns(2)
    col1.metric("Anomalies Found", summary['count'])
    col2.metric("% of Data", f"{summary.get('percentage', 0)}%")
    
    # Chart with anomalies
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df[selected_col], name='Data', 
                             line=dict(color='#00D4FF', width=2)))
    
    if summary['count'] > 0:
        anomaly_df = pd.DataFrame(summary['anomalies'])
        fig.add_trace(go.Scatter(x=anomaly_df['date'], y=anomaly_df[selected_col], mode='markers', 
                                 name='Anomalies', marker=dict(color='#FF6B6B', size=12, symbol='x')))
        st.dataframe(anomaly_df, use_container_width=True)
    
    fig.update_layout(title="Anomaly Detection", height=400, template='plotly_dark',
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)')
    st.plotly_chart(fig, use_container_width=True)

# Export
st.sidebar.markdown("---")
if st.sidebar.button("📥 Export Predictions"):
    predictions = predict_future(df, selected_col, forecast_days)
    csv = predictions.to_csv(index=False)
    st.sidebar.download_button("Download CSV", csv, "predictions.csv", "text/csv")

# Advanced Features - New Tabs
st.markdown("---")
st.subheader("🚀 Advanced Analytics")
adv1, adv2, adv3 = st.tabs(["📊 Compare Products", "💡 Insights", "🔗 Correlation"])

with adv1:
    compare_cols = st.multiselect("Select columns to compare", numeric_cols, default=numeric_cols[:min(3, len(numeric_cols))])
    if len(compare_cols) > 1:
        colors = ['#00D4FF', '#00FF88', '#FF6B6B', '#FFD93D', '#C77DFF']
        fig = go.Figure()
        for i, col in enumerate(compare_cols):
            fig.add_trace(go.Scatter(x=df['date'], y=df[col], name=col, line=dict(color=colors[i % len(colors)], width=2)))
        fig.update_layout(title="Multi-Product Comparison", height=400, template='plotly_dark',
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)',
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        comp_data = {col: {'Mean': df[col].mean(), 'Std': df[col].std(), 'Trend': get_trend_direction(df, col)['total_change_pct']} for col in compare_cols}
        st.dataframe(pd.DataFrame(comp_data).T.round(2))

with adv2:
    trend = get_trend_direction(df, selected_col)
    season = detect_seasonality(df, selected_col)
    anomalies = get_anomaly_summary(df, selected_col)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    insights = [
        f"📈 **Trend:** {selected_col} shows {'an upward' if trend['direction'] == 'up' else 'a downward'} trend with {abs(trend['total_change_pct'])}% change",
        f"📅 **Peak Day:** Highest values typically occur on {days[season['weekly']['peak_day']]}",
        f"📉 **Low Day:** Lowest values typically occur on {days[season['weekly']['low_day']]}",
        f"⚠️ **Anomalies:** {anomalies['count']} unusual data points detected ({anomalies.get('percentage', 0)}% of data)",
    ]
    if season['weekly']['strength'] > 10:
        insights.append(f"🔄 **Strong Weekly Pattern:** {season['weekly']['strength']}% variation between days")
    
    for insight in insights:
        st.markdown(insight)

with adv3:
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, 
                                         colorscale='RdBu', zmid=0, text=corr.values.round(2), texttemplate='%{text}'))
        fig.update_layout(title="Correlation Matrix", height=400, template='plotly_dark',
                          paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need multiple numeric columns for correlation analysis")

"""
Energy Price Forecasting System - Streamlit Dashboard

A Python-only dashboard for energy commodity price forecasting,
model performance analysis, and backtesting.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import requests
import json
from typing import Optional, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Energy Price Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
API_KEY = st.secrets.get("API_KEY", "")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def get_api_headers() -> Dict[str, str]:
    """Get API headers with authentication."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def fetch_forecast(commodity: str, horizon: int, start_date: str) -> Optional[Dict[str, Any]]:
    """Fetch forecast from API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/forecast",
            json={
                "commodity": commodity,
                "horizon": horizon,
                "start_date": start_date
            },
            headers=get_api_headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching forecast: {str(e)}")
        return None


def fetch_historical_data(commodity: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    """Fetch historical data from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/historical",
            params={
                "commodity": commodity,
                "start_date": start_date,
                "end_date": end_date,
                "limit": 1000
            },
            headers=get_api_headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return None


def fetch_models(commodity: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch models from API."""
    try:
        params = {}
        if commodity:
            params["commodity"] = commodity
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/models",
            params=params,
            headers=get_api_headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return None


def fetch_backtest(
    model_id: str,
    start_date: str,
    end_date: str,
    initial_capital: float,
    commission: float,
    slippage: float,
    strategy: str,
    threshold: float
) -> Optional[Dict[str, Any]]:
    """Run backtest via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/backtest",
            json={
                "model_id": model_id,
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": initial_capital,
                "commission": commission,
                "slippage": slippage,
                "strategy": strategy,
                "strategy_params": {"threshold": threshold} if strategy == "threshold" else {}
            },
            headers=get_api_headers(),
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error running backtest: {str(e)}")
        return None


def plot_forecast_vs_historical(forecast_data: Dict, historical_data: Dict):
    """Create forecast vs historical price chart."""
    # Prepare forecast data
    forecast_df = pd.DataFrame(forecast_data["predictions"])
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])
    
    # Prepare historical data
    historical_df = pd.DataFrame(historical_data["data"])
    historical_df["date"] = pd.to_datetime(historical_df["date"])
    
    # Create figure
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=historical_df["date"],
        y=historical_df["price"],
        mode="lines",
        name="Historical",
        line=dict(color="blue", width=2)
    ))
    
    # Forecast prices
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["price"],
        mode="lines+markers",
        name="Forecast",
        line=dict(color="red", width=2, dash="dash")
    ))
    
    # Confidence intervals
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["confidence_upper"],
        mode="lines",
        name="Upper Confidence",
        line=dict(color="rgba(255,0,0,0.2)", width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["confidence_lower"],
        mode="lines",
        name="Lower Confidence",
        line=dict(color="rgba(255,0,0,0.2)", width=0),
        fill="tonexty",
        fillcolor="rgba(255,0,0,0.1)",
        showlegend=True
    ))
    
    fig.update_layout(
        title=f"{forecast_data['commodity']} Price Forecast vs Historical",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        height=500
    )
    
    return fig


def main():
    """Main application."""
    st.markdown('<div class="main-header">📈 Energy Price Forecasting System</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Forecast", "Models", "Backtest", "Historical Data"]
    )
    
    # API Configuration in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("API Configuration")
    api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)
    api_key = st.sidebar.text_input("API Key", value=API_KEY, type="password")
    
    # Update global API settings
    global API_BASE_URL, API_KEY
    API_BASE_URL = api_url
    API_KEY = api_key
    
    # Route to appropriate page
    if page == "Forecast":
        show_forecast_page()
    elif page == "Models":
        show_models_page()
    elif page == "Backtest":
        show_backtest_page()
    elif page == "Historical Data":
        show_historical_page()


def show_forecast_page():
    """Forecast page."""
    st.header("Price Forecast")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        commodity = st.selectbox("Commodity", ["WTI", "BRENT", "NG"], index=0)
    
    with col2:
        horizon = st.slider("Forecast Horizon (days)", 1, 30, 7)
    
    with col3:
        start_date = st.date_input("Start Date", value=date.today())
    
    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            forecast_data = fetch_forecast(
                commodity,
                horizon,
                start_date.isoformat()
            )
            
            if forecast_data:
                st.success("Forecast generated successfully!")
                
                # Display forecast metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Commodity", forecast_data["commodity"])
                
                with col2:
                    st.metric("Horizon", f"{forecast_data['horizon']} days")
                
                with col3:
                    avg_price = sum(p["price"] for p in forecast_data["predictions"]) / len(forecast_data["predictions"])
                    st.metric("Average Forecast Price", f"${avg_price:.2f}")
                
                with col4:
                    price_range = max(p["price"] for p in forecast_data["predictions"]) - min(p["price"] for p in forecast_data["predictions"])
                    st.metric("Price Range", f"${price_range:.2f}")
                
                # Fetch historical data for comparison
                end_date = start_date + timedelta(days=horizon + 30)
                historical_data = fetch_historical_data(
                    commodity,
                    (start_date - timedelta(days=90)).isoformat(),
                    start_date.isoformat()
                )
                
                if historical_data:
                    # Plot forecast vs historical
                    fig = plot_forecast_vs_historical(forecast_data, historical_data)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Forecast table
                st.subheader("Forecast Details")
                forecast_df = pd.DataFrame(forecast_data["predictions"])
                st.dataframe(forecast_df, use_container_width=True)
                
                # Download button
                csv = forecast_df.to_csv(index=False)
                st.download_button(
                    label="Download Forecast (CSV)",
                    data=csv,
                    file_name=f"forecast_{commodity}_{start_date.isoformat()}.csv",
                    mime="text/csv"
                )


def show_models_page():
    """Models page."""
    st.header("Model Performance")
    
    commodity_filter = st.selectbox(
        "Filter by Commodity",
        ["All", "WTI", "BRENT", "NG"],
        index=0
    )
    
    if st.button("Refresh Models", type="primary"):
        with st.spinner("Loading models..."):
            commodity = None if commodity_filter == "All" else commodity_filter
            models_data = fetch_models(commodity)
            
            if models_data and models_data.get("models"):
                st.success(f"Loaded {models_data['total_count']} models")
                
                # Display models in a table
                models_df = pd.DataFrame([
                    {
                        "Model ID": m["model_id"],
                        "Commodity": m["commodity"],
                        "Model Type": m["model_type"],
                        "Version": m["version"],
                        "Stage": m["stage"]
                    }
                    for m in models_data["models"]
                ])
                
                st.dataframe(models_df, use_container_width=True)
                
                # Model metrics visualization
                if len(models_data["models"]) > 0:
                    st.subheader("Model Comparison")
                    
                    # Extract metrics if available
                    metrics_data = []
                    for model in models_data["models"]:
                        if "metrics" in model:
                            metrics_data.append({
                                "Model": model["model_id"],
                                "Commodity": model["commodity"],
                                **model["metrics"]
                            })
                    
                    if metrics_data:
                        metrics_df = pd.DataFrame(metrics_data)
                        st.dataframe(metrics_df, use_container_width=True)
            else:
                st.info("No models found.")


def show_backtest_page():
    """Backtest page."""
    st.header("Backtesting")
    
    # Fetch models for selection
    models_data = fetch_models()
    model_options = {}
    
    if models_data and models_data.get("models"):
        model_options = {m["model_id"]: m["model_id"] for m in models_data["models"]}
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_id = st.selectbox("Model", list(model_options.keys()) if model_options else ["No models available"])
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=90))
        end_date = st.date_input("End Date", value=date.today())
        initial_capital = st.number_input("Initial Capital", min_value=1000.0, value=100000.0, step=1000.0)
    
    with col2:
        commission = st.number_input("Commission", min_value=0.0, max_value=0.1, value=0.001, step=0.0001)
        slippage = st.number_input("Slippage", min_value=0.0, max_value=0.1, value=0.0005, step=0.0001)
        strategy = st.selectbox("Strategy", ["threshold", "momentum", "mean_reversion"])
        threshold = st.number_input("Threshold", min_value=0.0, max_value=1.0, value=0.02, step=0.01)
    
    if st.button("Run Backtest", type="primary"):
        if not model_options:
            st.error("No models available. Please ensure models are loaded.")
        else:
            with st.spinner("Running backtest... This may take a while."):
                backtest_result = fetch_backtest(
                    model_id,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    initial_capital,
                    commission,
                    slippage,
                    strategy,
                    threshold
                )
                
                if backtest_result:
                    st.success("Backtest completed successfully!")
                    
                    # Display metrics
                    metrics = backtest_result.get("metrics", {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Return", f"{metrics.get('total_return', 0) * 100:.2f}%")
                    
                    with col2:
                        st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
                    
                    with col3:
                        st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0) * 100:.2f}%")
                    
                    with col4:
                        st.metric("Win Rate", f"{metrics.get('win_rate', 0) * 100:.2f}%")
                    
                    # Equity curve
                    if "equity_curve" in backtest_result:
                        equity_df = pd.DataFrame({
                            "date": backtest_result["equity_curve"]["dates"],
                            "equity": backtest_result["equity_curve"]["values"]
                        })
                        
                        fig = px.line(equity_df, x="date", y="equity", title="Equity Curve")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Trade history
                    if "trades" in backtest_result and backtest_result["trades"]:
                        st.subheader("Trade History")
                        trades_df = pd.DataFrame(backtest_result["trades"])
                        st.dataframe(trades_df, use_container_width=True)


def show_historical_page():
    """Historical data page."""
    st.header("Historical Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        commodity = st.selectbox("Commodity", ["WTI", "BRENT", "NG"], index=0)
    
    with col2:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
    
    with col3:
        end_date = st.date_input("End Date", value=date.today())
    
    if st.button("Load Historical Data", type="primary"):
        with st.spinner("Loading historical data..."):
            historical_data = fetch_historical_data(
                commodity,
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if historical_data and historical_data.get("data"):
                st.success(f"Loaded {historical_data['total_count']} records")
                
                # Create DataFrame
                df = pd.DataFrame(historical_data["data"])
                df["date"] = pd.to_datetime(df["date"])
                
                # Price chart
                fig = px.line(df, x="date", y="price", title=f"{commodity} Historical Prices")
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Price", f"${df['price'].mean():.2f}")
                
                with col2:
                    st.metric("Min Price", f"${df['price'].min():.2f}")
                
                with col3:
                    st.metric("Max Price", f"${df['price'].max():.2f}")
                
                with col4:
                    st.metric("Volatility", f"{df['price'].std():.2f}")
                
                # Data table
                st.subheader("Data Table")
                st.dataframe(df, use_container_width=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Data (CSV)",
                    data=csv,
                    file_name=f"historical_{commodity}_{start_date.isoformat()}_{end_date.isoformat()}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No historical data found for the selected period.")


if __name__ == "__main__":
    main()


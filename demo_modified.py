from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

END = date.today()
START = date.today() - timedelta(days=365)

st.set_page_config(layout="wide", page_title="Stock Price Analysis")

st.title("Stock Analysis")
ticker = st.sidebar.text_input("Enter stock ticker", value="SPCX")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", START)
end_date = col2.date_input("End Date", END)
mv_avg = st.sidebar.slider("Short Moving Average",
                           min_value=5,
                           max_value=100,
                           value=20,
                           step=1)
mv_avg2 = st.sidebar.slider("Long Moving Average",
                            min_value=5,
                            max_value=100,
                            value=80,
                            step=1)

run_analysis = st.sidebar.button("Run Analysis", type="primary")


def get_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start_date, end_date, progress=False)
        if data.empty:
            return None, f"No data for {ticker}"
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data, f"Successfully downloaded data for {ticker}"
    except Exception as e:
        return None, f"Download failed due to: {e}"


if run_analysis:
    with st.spinner("Fetching data..."):
        data, message = get_stock_data(ticker, start_date, end_date)

    if data is None:
        st.error(message)
    else:
        st.success(message)

        # Calculations, done directly in the script (no class)
        data["change"] = data["Close"] - data["Close"].shift(1)
        data["return"] = np.log(data["Close"]).diff().round(4)
        data = data.dropna()
        data["MA"] = data["Close"].rolling(window=mv_avg).mean()
        data["MA2"] = data["Close"].rolling(window=mv_avg2).mean()

        # Price chart
        fig = px.line(data, x=data.index, y=["Close", "MA", "MA2"],
                      title=f"{ticker} Close and Moving Averages",
                      labels={"value": "Price", "variable": "Series"})
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(data.tail(10))
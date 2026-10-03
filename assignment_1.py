import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta

from stock import Stock

#Page Setup
END = date.today()
START = date.today() - timedelta(days=365)

st.set_page_config(layout="wide", page_title="Stock Price Analysis")
st.title("Stock Analysis")


ticker = st.sidebar.text_input("Enter stock ticker", value="AAPL")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", START)
end_date = col2.date_input("End Date", END)

mv_avg = st.sidebar.slider("Short Moving Average",
                           min_value=5,
                           max_value=200,
                           value=20,
                           step=1)
mv_avg2 = st.sidebar.slider("Long Moving Average",
                            min_value=5,
                            max_value=200,
                            value=100,
                            step=1)
run_analysis = st.sidebar.button("Run Analysis", type="primary")



@st.cache_data
def load_stock(symbol, start, end, ma_window, ma_window2):
    return Stock(symbol, start=start, end=end, ma_window=ma_window, ma_window2=ma_window2)



if run_analysis:
    st.session_state["ran"] = True


tab1, tab2 = st.tabs(["Single Stock Analysis", "Portfolio Comparison"])

#Single Stock Analysis
with tab1:
    if st.session_state.get("ran"):
        with st.spinner("Fetching data..."):
            stock = load_stock(ticker.strip().upper(), start_date, end_date, mv_avg, mv_avg2)

        if stock.data is None:
            st.error(stock.message)
        else:
            st.success(stock.message)


            m1, m2, m3 = st.columns(3)
            m1.metric("Last close", f"{stock.data['Close'].iloc[-1]:.2f}")
            m2.metric("Cumulative return",
                      f"{np.exp(stock.data['return'].sum()) - 1:.2%}")
            m3.metric("Trading days", len(stock.data))

            price_fig = go.Figure()
            price_fig.add_trace(go.Scatter(x=stock.data.index,
                                           y=stock.data["Close"],
                                           name="Close"))
            price_fig.add_trace(go.Scatter(x=stock.data.index,
                                           y=stock.data["MA"],
                                           name=f"{mv_avg}-day MA (short)"))
            price_fig.add_trace(go.Scatter(x=stock.data.index,
                                           y=stock.data["MA2"],
                                           name=f"{mv_avg2}-day MA (long)"))
            price_fig.update_layout(title=f"{stock.symbol} Close and Moving Average",
                                    xaxis_title="Date",
                                    yaxis_title="Price")
            st.plotly_chart(price_fig, use_container_width=True)


            st.plotly_chart(stock.plot_performance(), use_container_width=True)
            st.plotly_chart(stock.plot_return_dist(), use_container_width=True)


            st.subheader("Return statistics")
            st.dataframe(stock.data["return"].describe())
    else:
        st.info("Pick a ticker in the sidebar and click Run Analysis.")

#Portfolio Comparison
with tab2:
    tickers_text = st.text_input("Tickers, separated by commas",
                                 value="AAPL, MSFT, GOOG")
    compare = st.button("Compare")

    if compare:
        st.session_state["compare"] = True

    if st.session_state.get("compare"):
        symbols = [s.strip().upper() for s in tickers_text.split(",") if s.strip()]
        portfolio_fig = go.Figure()

        with st.spinner("Fetching data..."):
            for sym in symbols:
                s = load_stock(sym, start_date, end_date, 10, 50)

                if s.data is None:
                    st.error(f"{sym}: {s.message}")
                    continue


                cum = s.data["return"].cumsum()
                cum = cum - cum.iloc[0]
                portfolio_fig.add_trace(go.Scatter(x=cum.index, y=cum, name=sym))

        if len(portfolio_fig.data) > 0:
            portfolio_fig.update_layout(title="Cumulative Performance Comparison",
                                        xaxis_title="Date",
                                        yaxis_title="Cumulative return",
                                        legend_title="Ticker")
            st.plotly_chart(portfolio_fig, use_container_width=True)
    else:
        st.info("Enter tickers and click Compare.")
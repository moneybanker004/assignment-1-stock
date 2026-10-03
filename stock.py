import numpy as np
import pandas as pd
import plotly.express as px
import yfinance as yf


class Stock:

    def __init__(self, symbol, start=None, end=None, ma_window: int = 10, ma_window2: int = 50):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.ma_window = ma_window
        self.ma_window2 = ma_window2
        self.data, self.message = self.get_data()

    def get_data(self):
        try:
            data = yf.download(tickers=self.symbol,
                                start=self.start, end=self.end,
                                progress=False, multi_level_index=False)
            if data.empty:
                return None, f"No data for {self.symbol}"
            data = self._calc_returns(data)
            data = self._calc_ma(data)
            return data, f"Successfully downloaded for {self.symbol}"
        except Exception as e:
            return None, f"Failed due to {e}"

    def _calc_returns(self, df):
        df['change'] = df['Close'] - df['Close'].shift(1)
        df['return'] = np.log(df['Close']).diff().round(4)
        return df.dropna()

    def _calc_ma(self, df):
        df['MA'] = df['Close'].rolling(window=self.ma_window).mean()
        df['MA2'] = df['Close'].rolling(window=self.ma_window2).mean()
        return df

    def plot_performance(self):
        cum = self.data['return'].cumsum()
        fig = px.line(x=cum.index, y=cum,
                      title=f'Cumulative Performance of {self.symbol}',
                      labels={'x': 'Date', 'y': 'Cumulative Return'})
        return fig

    def plot_return_dist(self):
        mean_return = self.data['return'].mean()
        fig = px.histogram(self.data['return'],
                           nbins=35,
                           title=f'Distribution of Returns for {self.symbol}',
                           labels={'value': 'Return', 'count': 'Frequency'})
        fig.update_traces(marker_line_color='rgb(255, 0, 0)', marker_line_width=0.5)
        fig.add_vline(x=mean_return, line_dash='dash', line_color='red',
                      annotation_text=f'Mean: {mean_return:.4f}',
                      annotation_position='top right')
        return fig


def main():
    test = Stock("AAPL", "2025-09-24", "2026-09-23")
    print(test.data.head(15))
    #print(test.message)
    fig = test.plot_return_dist()
    fig.show()


if __name__ == '__main__':
    main()
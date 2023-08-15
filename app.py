import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime, datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from montecarlo import createPortfolioSim, singleStockSim


# App title
st.markdown('''
# Stock Analyzer
Easy way to check S&P 500 stock permance and forecast portfolio value using Monte Carlo simulation
            
Credits: Yuekai Wang
''')
st.write('---')

# Instructions
st.markdown('''
## Instructions
Explore different performance metrics using the graphs below:

**Graph 1:** This graph displays the past performance of selected stocks and includes a trendline based on your selection.

**Graph 2:** Explore the forecasted individual stock prices using Monte Carlo simulation.

**Graph 3:** Simulate the portfolio value using equal weighting for the selected stocks.

To rerun a simulation, click on the same position on the slider or click the 3 dots button on the top right and then click 'Rerun'.
''')
st.write('---')

# Sidebar
st.sidebar.subheader('Parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2019, 1, 1))
today = datetime.date.today()
end_date = st.sidebar.date_input("End date", today)
trend = st.sidebar.selectbox('Trend',['1W', '1M', '3M', '6M', 'YTD', '1Y', '2Y', '3Y'])


# Calculate start date based on user input
def calculate_start_date(trend, selectedTickerDf):
    today = selectedTickerDf.iloc[-1].name

    if trend.endswith('Y'):
        years = int(trend[:-1])
        # 252 trading days
        start_date = selectedTickerDf.iloc[-252* years].name
    elif trend.endswith('M'):
        months = int(trend[:-1])
        # 21 trading days in a month
        start_date = selectedTickerDf.iloc[-21* months].name
    elif trend.endswith('W'):
        # 5 trading days in a week
        start_date = selectedTickerDf.iloc[-5].name
    else:
        # number of days between year to date and today
        days = (datetime.date.today()-datetime.date(today.year, 1, 1)).days
        weeks = (datetime.date.today()-datetime.date(today.year, 1, 1)).days//7
        weekends = weeks*2
        # print(days, weeks, days-weekends)
        diff = days-weekends -7 # account for long weekend beginning of the year
        start_date = selectedTickerDf.iloc[-diff].name

    return str(start_date)

# Retrieving tickers data
snp_tickers = pd.read_csv('stocktickers.txt')
selectedTicker = st.sidebar.selectbox('Stock ticker', snp_tickers) 
portfolio_stocks = st.sidebar.multiselect('Portfolio', snp_tickers)
selectedTickerData = yf.Ticker(selectedTicker) 
selectedTickerDf = selectedTickerData.history(period='1d', start=start_date, end=end_date) 

# Trend line dates
trend_end_date = str(selectedTickerDf.iloc[-1].name) #latest date
trend_start_date = calculate_start_date(trend, selectedTickerDf)

# Company name
string_name = selectedTickerData.info['longName']
# st.header('**%s**' % string_name)

# Business Summary
# string_summary = selectedTickerData.info['longBusinessSummary']
# st.info(string_summary)

# Ticker data
# st.header('**Ticker data**')
# st.write(selectedTickerDf)

# Bollinger bands
st.header('**%s Performance**' % string_name)
qf=cf.QuantFig(selectedTickerDf,title='Quant Figure',legend='top',name='GS')
qf.add_bollinger_bands()
qf.add_trendline(trend_start_date, trend_end_date)
fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)

# Monte Carlo Simultion for single stock
st.header('**%s Price Simulation**' % selectedTicker)
num_simulations = color = st.select_slider('Select number of simulations',options = range(5,101), key=1)
simulation_results = singleStockSim(selectedTickerDf,  num_simulations)

# Plot Monte Carlo simulation
plt.figure(figsize=(10, 6))
plt.title('Monte Carlo Simulation for Stock Price')
plt.xlabel('Days')
plt.ylabel('Stock Price')
for i in range(num_simulations):
    plt.plot(simulation_results[i, :])
st.pyplot(plt)

# Portfolio Monte Carlo Simulation
st.header('**Portfolio forcast for $10000**')
num_sim_portfolio = color = st.select_slider('Select number of simulations',options = range(5,101), key=2)
if len(portfolio_stocks)>=2:
    joined_stocks = ", ".join(portfolio_stocks)
    st.subheader("Current Portfolio: ")
    st.write(f"{joined_stocks}")
    portfolio_sims = createPortfolioSim(portfolio_stocks, num_sim_portfolio)
    plt.figure(figsize=(10, 6))
    plt.title('Monte Carlo Simulation for Portfolio Value')
    plt.xlabel('Days')
    plt.ylabel('Portfolio Value ($)')
    for i in range(len(portfolio_sims[0])):
        plt.plot(portfolio_sims[:, i])
    st.pyplot(plt)
else:
    plt.figure(figsize=(10, 6))
    plt.title('Choose at least two tickers to generate a portfolio')
    plt.xlabel('Days')
    plt.ylabel('Portfolio Value ($)')
    plt.plot([0,100], [10000,10000])
    st.pyplot(plt)
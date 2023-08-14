import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime

# App title
st.markdown('''
# Stock Performance Checker 
Easy way to check S&P 500 stock permance
''')
st.write('---')

# Sidebar
st.sidebar.subheader('Query parameters')
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
selectedTickerData = yf.Ticker(selectedTicker) 
selectedTickerDf = selectedTickerData.history(period='1d', start=start_date, end=end_date) 

# Trend line dates
trend_end_date = str(selectedTickerDf.iloc[-1].name) #latest date
trend_start_date = calculate_start_date(trend, selectedTickerDf)

# Company name
string_name = selectedTickerData.info['longName']
st.header('**%s**' % string_name)

# Business Summary
string_summary = selectedTickerData.info['longBusinessSummary']
st.info(string_summary)

# Ticker data
st.header('**Ticker data**')
st.write(selectedTickerDf)

# Bollinger bands
st.header('**%s Performance**' % string_name)
qf=cf.QuantFig(selectedTickerDf,title='Quant Figure',legend='top',name='GS')
qf.add_bollinger_bands()
qf.add_trendline(trend_start_date, trend_end_date)
fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)
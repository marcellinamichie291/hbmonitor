import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz
from ta.momentum import RSIIndicator
import requests


access_token=st.secrets['cryptoquant']
headers = {'Authorization': 'Bearer ' + access_token}


url={'mvrv' : 'https://api.cryptoquant.com/v1/btc/market-indicator/mvrv?window=day&limit=2000&from=',
     'sopr_ratio' : 'https://api.cryptoquant.com/v1/btc/market-indicator/sopr-ratio?window=day&limit=2000&from=',
     'puell_multiple' : 'https://api.cryptoquant.com/v1/btc/network-indicator/puell-multiple?window=day&limit=2000&from=',
     'pnl_utxo':'https://api.cryptoquant.com/v1/btc/network-indicator/pnl-utxo?window=day&limit=2000&from=',
     'open_interest': 'https://api.cryptoquant.com/v1/btc/market-data/open-interest?window=day&limit=2000&exchange=all_exchange&from=',
     'funding_rates': 'https://api.cryptoquant.com/v1/btc/market-data/funding-rates?window=day&limit=2000&exchange=all_exchange&from=',

    }


##fetch_data from crypto_quant
def fetch_data(type,df_day):

    today = datetime.now(gettz('Asia/Seoul')).now()
    data_from = (today - timedelta(days=df_day)).strftime("%Y%m%d")
    df_url=url[type]+data_from
    df=requests.get(df_url, headers=headers).json()
    df=df['result']['data']
    df=pd.DataFrame(df).set_index('date',drop=True).sort_index(ascending=True)
    return df



#1.Bitcoin Monitoring

st.title("Page2 : Bitcoin_Score")

#1 P/L

symbol=['mvrv','sopr_ratio','puell_multiple','pnl_utxo']

st.header("1.Onchain_P&L_Score")


result={}
for i in symbol:

    if i==symbol[3]:
        df=fetch_data(i,365*5)[['profit_percent']].rename(columns={'profit_percent':'pnl_utxo'})
    else:
        df=fetch_data(i,365*5)

    df['rank']=df[i].rank(ascending=False) #the lower index, ther higher score
    t0=df[i][-1]
    t_1=df[i][-2]
    diff=t0-t_1

    rank=100*df['rank'][-1]/len(df)

    tmp={
        'VALUE' : '{:,.2f}'.format(t0),
        'DIFF' : '{:,.2f}'.format(diff),
        'SCORE': '{:,.0f}'.format(rank),
    }

    result[i]=tmp

result=pd.DataFrame(result).transpose()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("score",result['SCORE'].astype(float).mean().astype(int))
col2.metric(symbol[0],result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric(symbol[1],result.loc[symbol[1],'VALUE'],result.loc[symbol[1],'DIFF'])
col4.metric(symbol[2],result.loc[symbol[2],'VALUE'],result.loc[symbol[2],'DIFF'])
col5.metric('utxo in profit(%)',result.loc[symbol[3],'VALUE'],result.loc[symbol[3],'DIFF'])


#2.Derivatives
st.header("2.Derivatives") #the higher, the higher risk
symbol=['open_interest','funding_rates']


result={}
for i in symbol:
    df = fetch_data(i, 365 * 5)
    if i==symbol[0]:

        df = pd.DataFrame(RSIIndicator(df['open_interest']).rsi().dropna())
        df['rank'] = df['rsi'].rank(ascending=False)
        rank = 100 * df['rank'][-1] / len(df)
        t0 = df['rsi'][-1]
        t_1 = df['rsi'][-2]
        diff = t0-t_1

    else:

        df=df*100
        df['rank'] = df[i].rank(ascending=False) #the lower index, ther higher score
        rank = 100 * df['rank'][-1] / len(df)
        t0=df[i][-1]
        t_1=df[i][-2]
        diff=t0-t_1
    tmp={
        'VALUE' : '{:,.2f}'.format(t0),
        'DIFF' : '{:,.2f}'.format(diff),
        'SCORE': '{:,.0f}'.format(rank),
    }
    result[i]=tmp

result=pd.DataFrame(result).transpose()

col1, col2, col3 = st.columns(3)
col1.metric("score",result['SCORE'].astype(float).mean().astype(int))
col2.metric("Open interest RSI(14d)",result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric("Funding rates(PERP,8h,bp)",result.loc[symbol[1],'VALUE'],result.loc[symbol[1],'DIFF'])














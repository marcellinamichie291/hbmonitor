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
     'open_interest':'https://api.cryptoquant.com/v1/btc/market-data/open-interest?window=day&limit=2000&exchange=all_exchange&from=',
#     'mv':'https://api.cryptoquant.com/v1/btc/market-data/capitalization?window=day&limit=2000&from=',
#     'estimated_leverage_ratio':'https://api.cryptoquant.com/v1/btc/market-indicator/estimated-leverage-ratio?exchange=binance&window=day&limit=2000&from=',

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

symbol=['mvrv','sopr_ratio','puell_multiple']

st.header("1.Onchain_P&L_Score")


result={}
for i in symbol:
    df=fetch_data(i,365*5)
    df['rank']=df[i].rank(ascending=False)
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
#Col1
col1, col2, col3,col4 = st.columns(4)
col1.metric("score",result['SCORE'].astype(float).mean().astype(int))
col2.metric(symbol[0],result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric(symbol[1],result.loc[symbol[1],'VALUE'],result.loc[symbol[1],'DIFF'])
col4.metric(symbol[2],result.loc[symbol[2],'VALUE'],result.loc[symbol[2],'DIFF'])


#Leverage
st.header("2.Leverage Score") #the higher, the higher risk
symbol=['open_interest']
df=fetch_data(symbol[0],365*5)
df_rsi=pd.DataFrame(RSIIndicator(df['open_interest']).rsi().dropna())
df_rsi['rank']=df_rsi['rsi'].rank(ascending=False)
rank=100*df_rsi['rank'][-1]/len(df_rsi)
p0='{:,.2f}'.format(df_rsi['rsi'][-1])
diff='{:,.2f}'.format(df_rsi['rsi'][-1]-df_rsi['rsi'][-2])

col1, col2 = st.columns(2)
col1.metric("score",int(rank))
col2.metric('open_interest_RSI',p0,diff)














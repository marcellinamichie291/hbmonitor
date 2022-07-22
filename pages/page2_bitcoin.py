import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz
import time

import requests

access_token=st.secrets['cryptoquant']
headers = {'Authorization': 'Bearer ' + access_token}


symbol=['mvrv','sopr_ratio']
url={'mvrv':'https://api.cryptoquant.com/v1/btc/market-indicator/mvrv?window=day&limit=2000&from=',
     'sopr_ratio':'https://api.cryptoquant.com/v1/btc/market-indicator/sopr-ratio?window=day&limit=2000&from=',
#     'nupl':'https://api.cryptoquant.com/v1/btc/network-indicator/nupl?window=day&limit=2000&from=',
#     'oi':'https://api.cryptoquant.com/v1/btc/market-data/open-interest?window=day&limit=2000&exchange=all_exchange&from=',
#     'mv':'https://api.cryptoquant.com/v1/btc/market-data/capitalization?window=day&limit=2000&from=',
#     'est_lv':'https://api.cryptoquant.com/v1/btc/market-indicator/estimated-leverage-ratio?exchange=binance&window=day&limit=2000&from=',

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

st.title("Page2 : Bitcoin Monitoring")
st.header("1.Onchain(PnL) Monitoring")

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
col1, col2, col3 = st.columns(3)
col1.metric("score",result['SCORE'].astype(int).mean())
col2.metric(symbol[0],result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric(symbol[1],result.loc[symbol[1],'VALUE'],result.loc[symbol[1],'DIFF'])














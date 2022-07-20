import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz
import time

import requests

access_token=st.secrets['cryptoquant']
headers = {'Authorization': 'Bearer ' + access_token}

url={'mvrv':'https://api.cryptoquant.com/v1/btc/market-indicator/mvrv?window=day&limit=2000&from=',
     'sopr_ratio':'https://api.cryptoquant.com/v1/btc/market-indicator/sopr-ratio?window=day&limit=2000&from=',
     'nupl':'https://api.cryptoquant.com/v1/btc/network-indicator/nupl?window=day&limit=2000&from=',
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
symbol=['mvrv','sopr_ratio','nupl']
result={}
for i in symbol:
    df=fetch_data(i,365*5)
    value=df.tail(1).values[0][0]
    max=df.max()[0]
    min=df.min()[0]
    tmp={
        'value' : '{:,.2f}'.format(value),
        'max_5y' : '{:,.2f}'.format(max),
        'min_5y' : '{:,.2f}'.format(min),
    }
    result[i]=tmp

st.table(pd.DataFrame(result).transpose())



#st.line_chart(df,width=0, height=0)









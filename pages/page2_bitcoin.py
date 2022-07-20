import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz
import time

import requests

access_token=st.secrets['cryptoquant']
headers = {'Authorization': 'Bearer ' + access_token}

url={'oi':'https://api.cryptoquant.com/v1/btc/market-data/open-interest?window=day&limit=500&exchange=all_exchange&from=',
     'ohlc':'https://api.cryptoquant.com/v1/btc/market-data/price-ohlcv?window=day&limit=500&from=',
     'mv':'https://api.cryptoquant.com/v1/btc/market-data/capitalization?window=day&limit=500&from=',
     'est_lv':'https://api.cryptoquant.com/v1/btc/market-indicator/estimated-leverage-ratio?exchange=binance&window=day&limit=500&from=',

    }


##fetch_data from crypto_quant
def fetch_data(type,df_day):

    today = datetime.now(gettz('Asia/Seoul')).now()
    data_from = (today - timedelta(days=df_day)).strftime("%Y%m%d")

    df_url=url[type]+data_from
    df=requests.get(df_url, headers=headers).json()
    df=df['result']['data']
    df=pd.DataFrame(df).set_index('date',drop=True)
    return df


#1.Bitcoin Monitoring

st.title("Page2 : Bitcoin Monitoring")
st.header("1.PnL Monitoring")
st.write("-MVRV Ratio")
df=fetch_data('mv',100)
st.line_chart(df)






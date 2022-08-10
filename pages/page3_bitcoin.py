import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.tz import gettz
from ta.momentum import RSIIndicator
import requests
import time




access_token=st.secrets['cryptoquant']
headers = {'Authorization': 'Bearer ' + access_token}


url={'mvrv' : 'https://api.cryptoquant.com/v1/btc/market-indicator/mvrv?window=day&limit=2000&from=',
     'sopr_ratio' : 'https://api.cryptoquant.com/v1/btc/market-indicator/sopr-ratio?window=day&limit=2000&from=',
     'puell_multiple' : 'https://api.cryptoquant.com/v1/btc/network-indicator/puell-multiple?window=day&limit=2000&from=',
     'pnl_utxo':'https://api.cryptoquant.com/v1/btc/network-indicator/pnl-utxo?window=day&limit=2000&from=',
     'open_interest': 'https://api.cryptoquant.com/v1/btc/market-data/open-interest?window=day&limit=2000&exchange=all_exchange&from=',
     'funding_rates': 'https://api.cryptoquant.com/v1/btc/market-data/funding-rates?window=day&limit=2000&exchange=all_exchange&from=',
     'dvol':'https://test.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=1D&start_timestamp=1614524400000&end_timestamp=',
     'hashrate' : "https://api.cryptoquant.com/v1/btc/network-data/hashrate?window=day&limit=2000&from=",
     'blockreward' : 'https://api.cryptoquant.com/v1/btc/network-data/blockreward?window=day&limit=2000&from=',

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
st.title("Page3 : Bitcoin_Score")

#1 P/L

symbol=['mvrv','sopr_ratio','puell_multiple','pnl_utxo']
st.header("-Onchain_P&L_Score")



result={}
for i in symbol:
    df=fetch_data(i,365*5)

    if i=='pnl_utxo':
        df=df[['profit_percent']].rename(columns={'profit_percent':'pnl_utxo'})
        df['rank'] = df[i].rank(ascending=False)  # the lower index, ther higher score

    else:
        df=fetch_data(i,365*5)
        df['rank'] = df[i].rank(ascending=False)  # the lower index, ther higher score


    t0 = df[i][-1]
    t_1 = df[i][-2]
    diff = t0 - t_1
    rank = 100 * df['rank'][-1] / len(df)


    tmp={
        'VALUE' : '{:,.2f}'.format(t0),
        'DIFF' : '{:,.2f}'.format(diff),
        'SCORE': '{:,.0f}'.format(rank),
    }

    result[i]=tmp


#Mining_Density
hashrate=fetch_data('hashrate',365*5) #rolling평균이 필요하므로 1년 연장
blockreward=fetch_data('blockreward',365*5)[['blockreward_usd']]
df=hashrate.join(blockreward,how='left')
df['mining_density']=df['hashrate']/df['blockreward_usd']/1000
df=df[['mining_density']]
df['15d_ma']=df['mining_density'].rolling(15).mean()
df['365d_ma']=df['mining_density'].rolling(365).mean()

df['diff_ma']=df['15d_ma']-df['365d_ma'] #(+) -> bear / (-) ->bull
df['rank']=df['diff_ma'].rank(ascending=True)

t0=df['mining_density'][-1]
t1=df['mining_density'][-2]
diff=t0-t1
rank=100*df['rank'][-1]/len(df)


tmp={
        'VALUE' : '{:,.2f}'.format(t0),
        'DIFF' : '{:,.2f}'.format(diff),
        'SCORE': '{:,.0f}'.format(rank),
    }

result['mining_density']=tmp


result=pd.DataFrame(result).transpose()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("score",result['SCORE'].astype(float).mean().astype(int))
col2.metric(symbol[0],result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric(symbol[1],result.loc[symbol[1],'VALUE'],result.loc[symbol[1],'DIFF'])
col4.metric(symbol[2],result.loc[symbol[2],'VALUE'],result.loc[symbol[2],'DIFF'])
col5.metric('utxo in profit(%)',result.loc[symbol[3],'VALUE'],result.loc[symbol[3],'DIFF'])
col6.metric('mining_density',result.loc['mining_density','VALUE'],result.loc['mining_density','DIFF'])


#2.Derivatives
st.header("-Market_Derivatives_Score") #the higher, the higher risk
symbol=['open_interest','funding_rates','dvol']


result={}
for i in symbol:

    if i=='open_interest':
        df = fetch_data(i, 365 * 5)
        df = pd.DataFrame(RSIIndicator(df['open_interest']).rsi().dropna())
        df['rank'] = df['rsi'].rank(ascending=False)
        rank = 100 * df['rank'][-1] / len(df)
        t0 = df['rsi'][-1]
        t_1 = df['rsi'][-2]
        diff = t0-t_1

    elif i=='dvol': #The higher vol, the higher score
        url=url[i]+str(int(time.time())*1000)
        data = requests.get(url).json()
        df = pd.DataFrame(data['result']['data'])[[0, 4]].rename(columns={0:'date',4:i}).set_index('date', drop=True).sort_index(ascending=True)
        df['rank'] = df[i].rank(ascending=True)
        rank = 100 * int(df['rank'].tail(1)) / len(df)

        t0=float(df[i].tail(1))
        t_1=float(df[i].tail(2).head(1))
        diff=t0-t_1

    else:
        df = fetch_data(i, 365 * 5)
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

col1, col2, col3, col4 = st.columns(4)
col1.metric("score",result['SCORE'].astype(float).mean().astype(int))
col2.metric("Open interest RSI(14d)",result.loc[symbol[0],'VALUE'],result.loc[symbol[0],'DIFF'])
col3.metric("Funding rates(PERP,8h)",result.loc[symbol[1],'VALUE']+'bp',result.loc[symbol[1],'DIFF'])
col4.metric("DVOL_EOD",result.loc[symbol[2],'VALUE']+"%",result.loc[symbol[2],'DIFF'])

#3.Onchain_growth_score













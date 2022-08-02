import streamlit as st
import pandas as pd

#dynamoDB
import boto3
from boto3.dynamodb.conditions import Key
service='dynamodb'
region_name='ap-northeast-2'


aws_access_key_id=st.secrets['aws_access']
aws_secret_access_key=st.secrets['aws_secret']


def binance_funding():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('market')
    response = table.query(KeyConditionExpression=Key('name').eq('fut_binancefunding_minute'),Limit=1,ScanIndexForward=False)
    df=response['Items'][0]
    return df

def global_premium():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('market')
    response = table.query(KeyConditionExpression=Key('name').eq('btc_globalpremium_daily'),Limit=1,ScanIndexForward=False)
    df=response['Items']
    timestamp=df[0]['timestamp']
#    df=pd.DataFrame.from_dict(df).set_index(keys='timestamp', drop=True).drop('name', axis=1).astype(float)
    df=pd.DataFrame.from_dict(df).drop(columns=['name','timestamp','Binance_USD'],axis=1).transpose().astype(float)
    base_price=float(df.loc['btc_price_eod'])
    df=df.drop('btc_price_eod',axis=0)
    df['premium']=df[0].apply(lambda x : (x/base_price-1)*100)
    df = df[['premium']].sort_values('premium', ascending=False)
    df['premium']=df['premium'].apply(lambda x : '{:,.1f}%'.format(x))
    return df,timestamp,str(base_price)

def neuralprophet():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('neuralprophet')
    response = table.query(KeyConditionExpression=Key('type').eq('btc_macro_1d_v1'),Limit=1,ScanIndexForward=False)
    df=response['Items'][0]
    result={
        'timestamp':df['timestamp'],
        'Current_BTC_Price':df['base_price'],
        'Forecast_time':df['timestamp_24h'],
        'Forecast_BTC_Price':df['forecast_price'],
#        'Variables':df['variables']
    }
    return result

###########

st.title("Main : Market Monitoring")

tab1, tab2, tab3= st.tabs(["BTC Forecasting",
                            "Funding Rates",
                            "Daily BTC Global Premium"
                            ])

with tab1:
    st.header("BTC Forecasting(by neuralprophet)")
    st.write("\n")
    np = neuralprophet()
    diff = '{:,.1f}'.format(float(np['Forecast_BTC_Price']) - float(np['Current_BTC_Price']))
    forecast = '{:,.1f}'.format(float(np['Forecast_BTC_Price']))
    col1, col2 = st.columns(2)
    col1.metric("BTC Price @ " + np['timestamp'], np['Current_BTC_Price'])
    col2.metric("Forecast @ " + np['Forecast_time'], forecast, diff)

with tab2:
    st.header("Funding Rates")
    bnb_funding=binance_funding()

    df = pd.DataFrame([bnb_funding['binance_delivery']]).transpose()
    df = df.rename(columns={0: 'FF(bp)'})
    df['FF(bp)'] = df['FF(bp)'].apply(lambda x: float(x))
    df = df.sort_values('FF(bp)', ascending=False)

    st.write("<Binance_last update: "+bnb_funding['timestamp']+">")
    st.write("-Best 5")
    st.table(df.head(5).transpose())
    st.write("-Worst 5")
    st.table(df.tail(5).sort_values('FF(bp)',ascending=True).transpose())

with tab3:
    st.header("Daily BTC Global Premium")
    premium=global_premium()
    st.write("< BASE PRICE : Binance "+premium[2]+ " ("+premium[1]+") >")
    st.table(premium[0].transpose())








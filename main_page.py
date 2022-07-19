import streamlit as st
import pandas as pd
from datetime import datetime

#dynamoDB
import boto3
from boto3.dynamodb.conditions import Key
service='dynamodb'
region_name='ap-northeast-2'
aws_access_key_id=st.secrets['access_key']
aws_secret_access_key=st.secrets['secret_key']


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

###########
#1.Binane Funding Rate
bnb_funding=binance_funding()

df = pd.DataFrame([bnb_funding['binance_delivery']]).transpose()
df = df.rename(columns={0: 'FF(bp)'})
df['FF(bp)'] = df['FF(bp)'].apply(lambda x: float(x))
df = df.sort_values('FF(bp)', ascending=False)

st.title("Main : Market Monitoring")
#1
st.header("1.Binance Funding Rates(1mins)")
st.write("<last update: "+bnb_funding['timestamp']+">")
st.write("<Best 5>")
st.write(df.head(5).transpose())
st.write("<Worst 5>")
st.write(df.tail(5).sort_values('FF(bp)',ascending=True).transpose())

#2
st.header("2.Daily BTC Global Premium")

premium=global_premium()
st.write("< BASE PRICE : Binance "+premium[2]+ " ("+premium[1]+") >")
st.write(premium[0].transpose())


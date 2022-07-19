import streamlit as st
import pandas as pd
from datetime import datetime

#dynamoDB
import boto3
from boto3.dynamodb.conditions import Key
service='dynamodb'
region_name='ap-northeast-2'
aws_access_key_id=st.secrets["aws_access"]
aws_secret_access_key=st.secrets["aws_secret"]


def binance_funding():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('market')
    response = table.query(KeyConditionExpression=Key('name').eq('fut_binancefunding_minute'),Limit=1,ScanIndexForward=False)
    df=response['Items'][0]
    return df

###########
#1.Binane Funding Rate
bnb_funding=binance_funding()

df = pd.DataFrame([bnb_funding['binance_delivery']]).transpose()
df = df.rename(columns={0: 'FF(bp)'})
df['FF(bp)'] = df['FF(bp)'].apply(lambda x: float(x))
df = df.sort_values('FF(bp)', ascending=False)

st.title("Main : Market Monitoring")
st.header("1.Binance Funding Rates(1mins)")
st.write("<last update: "+bnb_funding['timestamp']+">")
st.write("<Best 5>")
st.write(df.head(5).transpose())
st.write("<Worst 5>")
st.write(df.tail(5).sort_values('FF(bp)',ascending=True).transpose())


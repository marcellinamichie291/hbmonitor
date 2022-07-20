import streamlit as st
import pandas as pd
from datetime import datetime

#dynamoDB
import boto3
from boto3.dynamodb.conditions import Key
service='dynamodb'
region_name='ap-northeast-2'
aws_access_key_id=st.secrets['aws_access']
aws_secret_access_key=st.secrets['aws_secret']


##Dai Status
def dai_eod():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('onchain')
    response = table.query(KeyConditionExpression=Key('name').eq('eth_dai_risk'),Limit=1,ScanIndexForward=False)
#    print(response)
    df=response['Items'][0]

    result={
        'timestamp': df['timestamp'],
        'Total DAI':'{:,.0f} USD'.format(float(df['dai_issued'])),
        'Total Risky Debt(%)':'{:,.1f}% ({:,.0f} USD)'.format((float(df['dai_risky_debt'])/float(df['dai_issued'])*100),float(df['dai_risky_debt'])),
        'High Risky Debt(%)':'{:,.1f}% ({:,.0f} USD)'.format((float(df['dai_high_risky_debt'])/float(df['dai_issued'])*100),float(df['dai_high_risky_debt'])),
        'Mid Risky Debt(%)':'{:,.1f}% ({:,.0f} USD)'.format((float(df['dai_medium_risky_debt'])/float(df['dai_issued'])*100),float(df['dai_medium_risky_debt'])),
        'Low Risky Debt(%)':'{:,.1f}% ({:,.0f} USD)'.format((float(df['dai_low_risky_debt'])/float(df['dai_issued'])*100),float(df['dai_low_risky_debt'])),}
    return result

def dai_chart():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('onchain')
    response = table.query(KeyConditionExpression=Key('name').eq('eth_dai_risk'),Limit=30,ScanIndexForward=False)
    df=response['Items']

    df = pd.DataFrame.from_dict(df).set_index(keys='timestamp', drop=True).drop('name', axis=1).astype(
        float)

    df['total_risky_debt'] = df['dai_risky_debt'] / df['dai_issued']
    df['high_risky_debt'] = df['dai_high_risky_debt'] / df['dai_issued']
    df['mid_risky_debt'] = df['dai_medium_risky_debt'] / df['dai_issued']
    df['low_risky_debt'] = df['dai_low_risky_debt'] / df['dai_issued']

    df = df[['total_risky_debt', 'high_risky_debt', 'mid_risky_debt', 'low_risky_debt']] * 100

    return df

###########
#1

st.title("Page3 : Ethereum Monitoring")
st.header("1.DAI - Algorithmic stablecoin")
dai=dai_eod()
st.write(dai)
dai_chart=dai_chart()

st.write("<TOTAL RISKY DEBT(%)>")
st.line_chart(dai_chart)





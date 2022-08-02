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




def trx_usdd_eod():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('onchain')
    response = table.query(KeyConditionExpression=Key('name').eq('trx_usdd_risk'),Limit=1,ScanIndexForward=False)
    df=response['Items'][0]
#    print(df)

    result={
        'timestamp': df['timestamp'],
        'Total USDD':'{:,.0f} USD Collateral({:,.2f}%)'.format(float(df['usdd_issued']) , ((float(df['usdd_collateral_usdt']) + float(df['usdd_collateral_usdc']) + float(df['usdd_collateral_trx']) + float(df['usdd_collateral_btc']))/float(df['usdd_issued']))*100),
        'Collaterals' : 'BTC({:,.2f}%) USDT({:,.2f}%) USDC({:,.2f}%) TRX({:,.2f}%) '.format(100*float(df['usdd_collateral_btc'])/float(df['usdd_issued']),100*float(df['usdd_collateral_usdt'])/float(df['usdd_issued']),100*float(df['usdd_collateral_usdc'])/float(df['usdd_issued']),100*float(df['usdd_collateral_trx'])/float(df['usdd_issued'])),
        'Trx Market cap / USDD' : '{:,.0f}%'.format(100*float(df['tron_mv'])/float(df['usdd_issued'])),
        'Curve_TVL' : 'USDD: {:,.0f}USD ({:,.0f}%)  3POOL: {:,.0f}USD ({:,.0f}%)'.format(float(df['curve_usdd_tvl']),100*float(df['curve_usdd_tvl'])/(float(df['curve_usdd_tvl'])+float(df['curve_3crv_tvl'])),float(df['curve_3crv_tvl']),100*float(df['curve_3crv_tvl'])/(float(df['curve_usdd_tvl'])+float(df['curve_3crv_tvl']))),
        'Price' : 'CurveFi(DEX): {:,.4f}   HUOBI(CEX): {:,.4f} '.format(float(df['usdd_curve_dex_price']),float(df['usdd_huobi_cex_price'])),

    }
    return result

def trx_usdd_chart():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('onchain')
    response = table.query(KeyConditionExpression=Key('name').eq('trx_usdd_risk'),Limit=30,ScanIndexForward=False)
    df=response['Items']
    df = pd.DataFrame.from_dict(df).set_index(keys='timestamp', drop=True).drop('name', axis=1).astype(
        float)

    df['collateral ratio']=100*(df['usdd_collateral_btc']+df['usdd_collateral_usdc']+df['usdd_collateral_usdt']+df['usdd_collateral_trx'])/df['usdd_issued']
    df=df[['collateral ratio']]

    return df

#1
st.title("Page5 : Risk on Tron ")
usdd=trx_usdd_eod()
st.header("1.USDD - Algorithmic stablecoin")
st.write(usdd)
usdd_chart=trx_usdd_chart()
st.write("<USDD Collateral ratio(%)>")
st.line_chart(usdd_chart,width=0, height=0,use_container_width=True)
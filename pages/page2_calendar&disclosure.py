import streamlit as st
import pandas as pd
import investpy


#calendar
from dateutil.tz import gettz
from dateutil import relativedelta
import calendar
from datetime import datetime,timedelta

dateDict = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}


#dynamoDB
import boto3
from boto3.dynamodb.conditions import Key
service='dynamodb'
region_name='ap-northeast-2'

aws_access_key_id=st.secrets['aws_access']
aws_secret_access_key=st.secrets['aws_secret']



def economic_calendar():
    # Convert calendar
    now = datetime.now(gettz('Asia/Seoul')).now()  # now를 GMT+9으로 호출
    sat_now = now + relativedelta.relativedelta(weekday=calendar.SATURDAY)  # 이번주 토요일 호출
    if now.day==sat_now.day:
        sat_now+=timedelta(days=7)

    # investpy에 변수 date 선언
    from_date = now.strftime("%d/%m/%Y")
    to_date = sat_now.strftime("%d/%m/%Y")

    df = investpy.news.economic_calendar(time_zone='GMT +9:00',
                                         time_filter='time_only',
                                         countries=None,
                                         importances=None,
                                         categories=None,
                                         from_date=from_date,
                                         to_date=to_date)

    data = df[(df['zone'] == 'united states') & (df['importance'].isin(['high','medium']))]
    data = data[['date', 'time', 'event', 'actual', 'forecast', 'previous']].reset_index(drop=True)

    data['date1'] = data['date'].apply(lambda x: x.split("/"))  # 날짜를 한국형으로 변환
    data['date2'] = data['date1'].apply(lambda x: x[2] + "/" + x[1] + "/" + x[0])  # Date2에 날짜를 한국형으로 변환
    data['date2'] = pd.to_datetime(data['date2'])
    data['day'] = data['date2'].apply(lambda x: dateDict[x.weekday()])
    data['date'] = data['date2'].astype(str) + ' ' + data['time'] + '(' + data['day'] + ')'
    data = data[['date', 'event','actual', 'forecast', 'previous']]
    data.set_index(keys=['date'], inplace=True, drop=True)
    return data

def get_upbit_disclosure():
    dynamodb = boto3.resource(service, region_name=region_name,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table('cex_disclosure')
    response = table.query(KeyConditionExpression=Key('cex').eq('upbit'),Limit=10,ScanIndexForward=False)
    df=pd.DataFrame(response['Items'])[['timestamp','title']]
    df['timestamp']=df['timestamp'].apply(lambda x : x.split("T")[0]+' '+(x.split("T")[1].split("+")[0].split(":")[0])+':'+(x.split("T")[1].split("+")[0].split(":")[0]))
    df=df.set_index('timestamp',drop=True)

    return df


st.title("Page2: Disclosure")

tab1,tab2= st.tabs(["Economic Calendar",'Upbit_Disclosure'])


with tab1:
    st.header("Economic Calendar")
    calendar=economic_calendar()
    st.table(calendar)

with tab2:
    st.header("Upbit Disclosure")
    upbit=pd.DataFrame(get_upbit_disclosure())
    st.table(upbit)

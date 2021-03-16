
#please dont overwrite or alter the text #
# ©Refinitiv
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import cx_Oracle
import datetime
import altair as alt
import os
import base64 as bs4
import pandas_profiling as pf
from streamlit_pandas_profiling import st_profile_report
import streamlit.components.v1 as components
import time
from Scripts import *


st.set_page_config(page_title="Data Xplorer 1.0",page_icon=":rocket:",layout='centered',initial_sidebar_state='collapsed')

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.components.v1.iframe("https://treasuryxl.com/wp-content/uploads/2020/08/Partner-Banner-Refinitiv.png",height=180)

# st.image(content.png)
st.title("Data Xplorer 1.0")
st.markdown('For production , Built by production')
st.header('MENU')
focus=st.selectbox("",("curve","loadset","Apex","About!"))
st.sidebar.title('CONFIGURATION PANEL')
environment=st.sidebar.radio("Select your environment",("PROD","BETA","APEX"))

@st.cache
def get_dataset():
    if environment=="PROD":
        prod='oracle+cx_oracle://datamanager:data@oracle.commodities.int.thomsonreuters.com/?service_name=pocb.int.thomsonreuters.com'
    if environment=="APEX":
        prod='oracle+cx_oracle://monitor:monitor@oracle.commodities.int.thomsonreuters.com/?service_name=pocb.int.thomsonreuters.com'
    if environment=="BETA":
        prod='oracle+cx_oracle://datamanager:test@oracle2.beta.commodities.int.thomsonreuters.com/?service_name=pocbt.int.thomsonreuters.com'
    return prod

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def connection():
    try:
        prod=get_dataset()
        engine = create_engine(prod)
        con = engine.connect()
        return con
    except:
        print("Connection could not have been established try again")


if focus=='curve':
    d = st.sidebar.date_input("Data from")
    st.write('Your selected date is:', d)
    d1=str(d)
    c = st.sidebar.date_input("Data to")
    st.write('Your selected date is:', c)
    d2=str(c)

    options = st.sidebar.multiselect('What Data you are looking for ?',['usage', 'loadset_id', 'curve data',"Analysis"],('curve data','loadset_id'))
    # st.sidebar.write('You have selected:', options)

    charts = st.sidebar.multiselect('which chart you want ?',['Scatter plot','bar chart',"heatmap","line chart"],('heatmap'))
    # st.sidebar.write('You have selected:', charts)
    axis_x=st.sidebar.selectbox('please select x axis',['forecast_date:T','value:Q', 'value_date:T',"local_forecast_date:T","local_value_date:T"])
    axis_y=st.sidebar.selectbox('please select y axis',[ 'value:Q','forecast_date:T', 'value_date:T',"local_forecast_date:T","local_value_date:T"])

    curve_number = st.sidebar.text_input('curve',key=1)

    curve_number_space=str(curve_number).strip()

    if not curve_number:
        st.warning('Please input a curve name.')
        st.stop()
        st.success('curve selected.')

    connect=st.sidebar.button('Connect')

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def time_series():
        time1=timeseries.replace("from_date",d1)
        time2=time1.replace("to_date",d2)
        time3=time2.replace("curve_number",curve_number_space)
        return time3

    @st.cache(suppress_st_warning=True)
    def forecast_series():
        time1=forecast.replace("from_date",d1)
        time2=time1.replace("to_date",d2)
        time3=time2.replace("curve_number",curve_number_space)
        return time3

    USAGE1=usage.replace("%s",curve_number_space)
    Loadset=Loadset.replace("%s",curve_number_space)
    type2=type1.replace("ram",curve_number_space)

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def curve_type():
        type_of=pd.read_sql_query(type2,connection())
        typo=type_of['curve_type_id'].values
        return typo

    typo=curve_type()
    # @st.cache(allow_output_mutation=True,hash_funcs={connection: get_dataset()})
    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def type_of_curve(options):

                if typo==1:
                    st.write("please note:This is a Timeseries")
                    curve_data=time_series()
                    data=pd.read_sql_query(curve_data,connection(),parse_dates=['local_value_date','local_value_date','forecast_date','value_date'])
                    # USAGE4=st.dataframe(curve_data1)

                else:
                    st.write("please note:This is a Forecast")
                    curve_data=forecast_series()
                    data=pd.read_sql_query(curve_data,connection(),parse_dates=['local_value_date','local_value_date','forecast_date','value_date'])
                    # USAGE4=st.dataframe(curve_data1)

                return data

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def Curve_Analysis(options):
        for element in options:
            if element=="Analysis":
                d1=type_of_curve(options)
                data=pf.ProfileReport(d1)
                data1=st_profile_report(data)
                return data1


    def chart_func(charts):
        for element in charts:

                if element=="Scatter plot" :
                    curve_data=type_of_curve(options)
                    chart=alt.Chart(curve_data).mark_trail(point=True).encode(x=(axis_x),y=(axis_y),color='value:Q').interactive()
                    chart1=st.altair_chart(chart, use_container_width=True)
                    return chart1

                elif element=="bar chart":
                    curve_data=type_of_curve(options)
                    chart=alt.Chart(curve_data).mark_bar().encode(x=axis_x,y=axis_y,color='value:Q').interactive()
                    text = chart.mark_text(align='left',baseline='middle',dx=3).encode(text='value:Q')
                    chart1=st.altair_chart(chart,use_container_width=True)

                    return chart1

                elif element=="line chart" :
                    curve_data=type_of_curve(options)
                    chart=alt.Chart(curve_data).mark_line(point=True).encode(alt.X(axis_x, scale=alt.Scale(zero=False)),alt.Y(axis_y, scale=alt.Scale(zero=False)),order=axis_x).interactive()
                    chart1=st.altair_chart(chart, use_container_width=True)
                    return chart1

                elif element=="heatmap":
                    curve_data=type_of_curve(options)
                    base = alt.Chart(curve_data).encode(alt.X('value_date:O',timeUnit='hours' ,scale=alt.Scale(paddingInner=0)),alt.Y('value_date:O',timeUnit='monthdate', scale=alt.Scale(paddingInner=0)))
                    heatmap = base.mark_rect().encode(color=alt.Color('count(value_date):Q',scale=alt.Scale(scheme='redblue'),legend=alt.Legend(direction='horizontal')))
                    text = base.mark_text(baseline='middle').encode(text='count(value_date):Q')
                    chart1=st.altair_chart(heatmap + text, use_container_width=True)

                    return chart1




    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def Usage_data(options):
        for element in options:
            if element=="usage":
                USAGE=pd.read_sql_query(USAGE1,connection())
                USAGE2=st.write(USAGE)
                return USAGE2
    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def Loadset_data(options):
        for element in options:
            if element=="loadset_id":
                loadset_name=pd.read_sql_query(Loadset,connection())
                USAGE3=st.write(loadset_name)
                return USAGE3



    download=st.button('Download Curve Data')
    if download:
        for element in options:
            if element=='curve data':
                  'Download Started!'
                  df_download=type_of_curve(options)
                  csv = df_download.to_csv(index=False)
                  b64 = bs4.b64encode(csv.encode()).decode()  # some strings
                  linko= f'<a href="data:file/csv;base64,{b64}" download="curve data.csv">Download csv file</a>'
                  st.markdown(linko, unsafe_allow_html=True)
            else:
                print('No Data To Download')

    if connect:
        with st.spinner('Fetching your data...'):
            time.sleep(5)
            Main_data=st.dataframe(type_of_curve(options))
            Usage_set=Usage_data(options)
            load_Set=Loadset_data(options)
            curve_set1=type_of_curve(options)
            show_chart=chart_func(charts)
            Eveything=Curve_Analysis(options)
            st.success('Data Loaded!')


elif focus=='loadset':

    options = st.sidebar.multiselect('What Data you are looking for ?',['curves', 'Analysis','updated_date','created_date','usage'],('curves'))
    Load_set_number = st.sidebar.text_input('loadset',key=1,max_chars=7)
    if not Load_set_number:
        st.warning('Please input a Loadset name.')
        st.stop()
        st.success('Loadset selected.')
    # st.sidebar.title('CONFIGURATION PANEL')

    connect=st.sidebar.button('Connect')
    Loader1=Loader.replace("ram",Load_set_number)
    Loadset_usage1=Loadset_usage.replace("ram",Load_set_number)

    @st.cache(allow_output_mutation=True)
    def loadset_explained_data(options):
        for element in options:
            if element=="curves":
                USAGE=pd.read_sql_query(Loader1,connection())
                return USAGE

    download=st.button('Download Loadset details')
    if download:
        for element in options:
            if element=='curves':
                  'Download Started!'
                  df_download=loadset_explained_data(options)
                  csv = df_download.to_csv(index=False)
                  b64 = bs4.b64encode(csv.encode()).decode()  # some strings
                  linko= f'<a href="data:file/csv;base64,{b64}" download="loadset details.csv">Download csv file</a>'
                  st.markdown(linko, unsafe_allow_html=True)
            else:
                'No Data To Download'


    @st.cache(allow_output_mutation=True)
    def usage(options):
        for element in options:
            if element=="usage":
                USAGE=pd.read_sql_query(Loadset_usage1,connection())
                USAGE.rename(columns={"curve_id":"CURVE ID","object_id":"FILE ID","timezone":"FILE NAME"},inplace=True)
                return USAGE

    download1=st.button('Download Usage File')
    if download1:
        for element in options:
            if element=='usage':
               'Download Started!'
               df_download=usage(options)
               csv = df_download.to_csv(index=False)
               b64 = bs4.b64encode(csv.encode()).decode()  # some strings
               linko= f'<a href="data:file/csv;base64,{b64}" download="usage.csv">Download csv file</a>'
               st.markdown(linko, unsafe_allow_html=True)
            else:
               'No Data To Download'



    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def describe_loadset(options):
            for element in options:
                if element=="Analysis":
                    data=loadset_explained_data(options)
                    description=pf.ProfileReport(data)
                    data1=st_profile_report(description)
                    return data1

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def chart_funcion(options):
        for element in options:
            if element=='updated_date':
                df=loadset_explained_data(options)
                chart=alt.Chart(df).mark_bar().encode(alt.X('last_updated:T',timeUnit='yearmonthdate'),alt.Y('count(last_updated):Q')).interactive()
                text = chart.mark_text(align='left',baseline='middle',dx=3).encode(text='count(last_updated):Q')
                chart1=st.altair_chart(chart ,use_container_width=True)
                return chart1

            elif element=='created_date':
                df=loadset_explained_data(options)
                chart=alt.Chart(df).mark_bar().encode(alt.X('created_date:T',timeUnit='yearmonthdate'),alt.Y('count(created_date):Q')).interactive()
                chart1=st.altair_chart(chart,use_container_width=True)
                return chart1



    with st.spinner('Fetching your data...'):
        if connect:
            Usage_set=st.write(loadset_explained_data(options))
            chart=chart_funcion(options)
            desciption_set=describe_loadset(options)
            data=sorted(options)
            usage1=st.write(usage(options))
            st.success('Data Loaded!')



elif focus=='Apex':
    # st.sidebar.title('CONFIGURATION PANEL')
    d = st.sidebar.date_input("Data from")
    st.write('Your selected date is:', d)
    d1=str(d)
    c = st.sidebar.date_input("Data to")
    st.write('Your selected date is:', c)
    d2=str(c)
    search = st.sidebar.text_input('loadset',key=1)

    options = st.sidebar.multiselect('What Data you are looking for ?',['tickets',"Analyst","created","search"],('tickets'))
    # st.write('You have selected:', options)

    connect=st.sidebar.button('Connect')

    apex_tickets=apex_tickets.replace("ram1", d1)
    apex_tickets1=apex_tickets.replace("ram2", d2)
    find_tickets2=find_tickets1.replace("ram",search)

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def find_all(options):
        for element in options:
            if element=="tickets":
                Tickets=pd.read_sql_query(apex_tickets1,connection())
                return Tickets


    def find_ticket(options):
        for element in options:
            if element=="search":
                Ticket=pd.read_sql_query(find_tickets2,connection())
                return Ticket


    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def plot(options):
        for element in options:
            if element=="Analyst":
                data=find_all(options)
                chart=alt.Chart(data).mark_bar().encode(x='analyst:O',y='count(analyst):Q',color='analyst:O')
                chart1=st.altair_chart(chart,use_container_width=True)
                return chart1

    @st.cache(allow_output_mutation=True,suppress_st_warning=True)
    def created(options):
        for element in options:
            if element=="created":
                data=find_all(options)
                chart=alt.Chart(data).mark_bar().encode(x='created_date:T',y='count(ticket_id):Q',color='count(ticket_id):Q')
                chart1=st.altair_chart(chart,use_container_width=True)

                return chart1


    download=st.button('Download Excel File')
    if download:
        for element in options:
            if element=='tickets':
                'Download Started!'
                df_download=find_all(options)
                csv = df_download.to_csv(index=False)
                b64 = bs4.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download csv file</a>'
                st.markdown(linko, unsafe_allow_html=True)
            else:
                'No Data To Download'



    with st.spinner('Fetching your data...'):
        if connect==True:
            tickets_created=st.write(find_all(options))
            plot=plot(options)
            created=created(options)
            tickets_find=st.write(find_ticket(options))
            st.success('Data Loaded!')

elif focus=='file_Analyser':

        options = st.sidebar.multiselect('What Data you are looking for ?',["Analysis"],('Analysis'))
        ram=st.file_uploader(label="file",type='xls')
        def fileupload():
                if ram is not None:
                    df=pd.read_excel(ram)
                    st.write(df)
                else:
                    st.write("invalid file")
                return df

        def Curve_Analysis(options):
            for element in options:
                if element=="Analysis":
                    d1=fileupload()
                    data=pf.ProfileReport(d1)
                    data1=st_profile_report(data)
                    return data1

        if st.button("process"):
            data1=Curve_Analysis(options)
            data2=fileupload()



elif focus=='About!':
    st.write('''Welcome to Data Xplorer, this is the version 1.0

                Usage:-

                The use of the tool is to explore and find patterns in the data.

                You can get different visuals of the data  which can be downloaded and is interactive.

                For the graphs you can change the axis to view the visual that fits the data and your eye the most.

                The interface consist of a configuration Panel, the visual area and the data area

                1. The configuration panel:

                This will give you all the setting details , to connect to different environment and graphs and date ranges

                2. The data area:

                This will show you the data you have asked for

                3. The Visual area:

                this will show you different visual you have asked for

                Feedback:-

                We would love to hear your feedback.

                If you have any feedback feel free to share you thoughts and ideas in the below form

                wich will help this tool to grow and come-up with a lot of different features in the future

                the form:-
                https://refinitiv-my.sharepoint.com/:x:/p/abhilashkumar_panda/EWtvETw1Z65Co47DoV4d6mIBWCahEg0nPyMvxZfjrT4KGw?e=PU44B4''')

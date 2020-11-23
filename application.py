from flask import Flask

from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
#import dash_table
import paramiko
import json
import os
import base64
# =============================================================================
# pi_user = os.getenv('pi_user')
# pi_pass = os.environ.get('pi_pass')
# pgres_user = os.getenv('pgres_user')
# pgres_pass = os.environ.get('pgres_pass')
# pi_hostname = os.environ.get('pi_hostname')
# pgres_hostname = os.environ.get('pgres_hostname')
# file = os.environ.get('file')
# =============================================================================

pi_user='pi'
pi_pass='Felicia2020#'
pgres_user='beef'
pgres_pass='Felicia2020#'
pi_hostname='98.210.69.250'
pgres_hostname='water-logger.cmoec5ph6uhr.us-east-1.rds.amazonaws.com'






application = Flask(__name__)

# =============================================================================
# @application.route('/waterlogger/')
# def index():
#     return 'Hello Flask app'
# =============================================================================


def water_query_results(query, connection):
    cursor = connection.cursor()
    cursor.execute(query)
    query_fetch = cursor.fetchall()
    cols = list(map(lambda x: x[0], cursor.description))
    query_fetch=pd.DataFrame(query_fetch, columns=cols)
    return query_fetch




colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}




app = dash.Dash(
    __name__,
    server=application
   # routes_pathname_prefix='/waterlogger/'
)

#image_filename = 'hydrecon_stack.png'
#encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def serve_layout():


    
    
    client =  paramiko.client.SSHClient()
    hostname=pi_hostname
    port=22
    username=pi_user
    password=pi_pass
    
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    client.load_system_host_keys()
    print('loaded client')
    client.connect(hostname, port, username, password)
    
    sftp_client = client.open_sftp()
    
    localFilePath='./detector_output.json'
    sftp_client.get('/home/pi/water_logger/detector_output.json', localFilePath)
        
    sftp_client.close() 
    
    
    with open(localFilePath) as detector_output:
      flow_data = json.load(detector_output)
  
    flow_eval=str(flow_data['flow'])
    
    connection = psycopg2.connect(user = pgres_user,
                                  password = pgres_pass,
                                  host = pgres_hostname,
                                  port = "5432",
                                  database = "raw_logs")

    init_df=water_query_results(f"select* from pulse_detection order by record_date asc", connection)
    init_df["gallons"]=float(0)
    
    m_recent_df=init_df[init_df.record_date==max(init_df.record_date)]
    last_log=str(max(m_recent_df.record_date))
    last_gallon=str(max(m_recent_df.total_pulses/26.7))
    
    
    
    #1800 based on average tested values in 2018, hall effect. 
    #new pulse detection is 13.3 pulses per gallon. We double because there are to reed switches at halfway.
    init_df.gallons=init_df.total_pulses/26.7
    total_gallons=round(sum(init_df.gallons))
  
    
    
    
    timeline_graph = html.Div( children=[
        html.H1(children='Hydrecon', 
            style={
            'textAlign': 'left',
            'font-family': 'Tahoma',
            'color': 'rgb(0, 128, 255)'}),
        
       # html.Button('Stack', id='submit-val', n_clicks=0),

        dcc.Graph(id='example-graph',
              figure={'data': [{'x': init_df.record_date, 'y': init_df.gallons, 'type': 'line', 'name': 'Gallons'}],
                      'layout': {'title': 'Gallons'}}),
        
        html.H3(children=f'Total gallons to date: {total_gallons}',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'}),
        
        html.H4(children=f'Flow rate: {flow_eval}',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'}),
        
        html.H4(children=f'Last_log: {last_log} | {last_gallon} gallon(s)',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'})        
        
# =============================================================================
#         html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
#                  style={
#                         'style':"vertical-align:middle"}),
# =============================================================================
        

        
        ])
    
        
    return timeline_graph
    



app.layout = serve_layout

# run the app.
if __name__ == "__main__":

    
    
    application.debug = True
    application.run()
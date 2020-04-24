from flask import Flask

from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc




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


def water_pgres(user, password):
    connection = psycopg2.connect(user = user,
                                  password = password,
                                  host = "water-logger.cmoec5ph6uhr.us-east-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "raw_logs")
    return connection


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}



app = dash.Dash(
    __name__,
    server=application,
    routes_pathname_prefix='/waterlogger/'
)


def serve_layout():
    
    connection = psycopg2.connect(user = "beef",
                                  password = "Felicia2020#",
                                  host = "water-logger.cmoec5ph6uhr.us-east-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "raw_logs")

    init_df=water_query_results(f"select* from raw_effect_counts order by record_date asc", connection)
    init_df["gallons"]=float(0)
    
    
    #1800 based on average tested values in 2018
    init_df.gallons=init_df.total_count/1800
    total_gallons=round(sum(init_df.gallons))
  
    
    
    
    timeline_graph = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(children='Beef-Cheese Ranch', 
            style={
            'textAlign': 'left',
            'color': colors['text']}),
    
        html.Div(children=f'Total gallons to date: {total_gallons}',            
            style={
            'textAlign': 'left',
            'color': colors['text']}),
        
        dcc.Graph(id='example-graph',
              figure={'data': [{'x': init_df.record_date, 'y': init_df.gallons, 'type': 'line', 'name': 'Gallons'}],
                      'layout': {'title': 'Gallons by Date'}})
        
        ])
        
    return timeline_graph
    
  


app.layout = serve_layout

# run the app.
if __name__ == "__main__":

    
    
    application.debug = True
    application.run()
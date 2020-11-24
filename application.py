from flask import Flask
import dash
import dash_html_components as html
import dash_core_components as dcc
import os
from helpers import* 

pi_pass = os.environ.get('pi_pass')
pgres_pass = os.environ.get('pgres_pass')
pi_hostname = os.environ.get('pi_hostname')


application = Flask(__name__)

# =============================================================================
# @application.route('/waterlogger/')
# def index():
#     return 'Hello Flask app'
# =============================================================================



colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


app = dash.Dash(
    __name__,
    server=application
   #routes_pathname_prefix='/waterlogger/'
)

#image_filename = 'hydrecon_stack.png'
#encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def serve_layout():
    
    flow_data=ssh_file(pi_hostname, pi_pass)
    flow_eval=str(flow_data['flow'])
    
    connection=pgres_com('beef', pgres_pass)
    init_df=pgres_query(f"select* from pulse_detection order by record_date asc", connection).data_frame
    
    
    init_df["gallons"]=float(0)
    m_recent_df=init_df[init_df.record_date==max(init_df.record_date)]
    
    
    last_log=max(m_recent_df.record_date)
    last_log=last_log.strftime("%Y %b %d %H:%M")
    
    
    last_gallon=str(round(max(m_recent_df.total_pulses/26.7)))
    
    #1800 based on average tested values in 2018, hall effect. 
    #New pulse detection is 13.3 pulses per gallon. We double because there are to reed switches at halfway.
    init_df.gallons=init_df.total_pulses/26.7
    total_gallons=round(sum(init_df.gallons))
    
    sums=init_df.resample('D', on='record_date', kind='period').sum()
    sums=sums[sums.total_pulses!=0]
    agd=round(sums.total_pulses.mean()/26.7)
    
    
    
    graph_df=init_df.resample('D', on='record_date', kind='period').sum()
    graph_df=graph_df[graph_df.gallons!=0]
    
    graph_df['record_date']=graph_df.index.to_series().astype(str)
    

    timeline_graph = html.Div( children=[
        html.H1(children='Hydrecon', 
            style={
            'textAlign': 'left',
            'font-family': 'Tahoma',
            'color': 'rgb(0, 128, 255)'}),
        
       # html.Button('Stack', id='submit-val', n_clicks=0),

        dcc.Graph(id='example-graph',
              figure={'data': [{'x': graph_df.record_date, 'y': graph_df.gallons, 'type': 'bar', 'name': 'Gallons'}],
                      'layout': {'title': 'Gallons'}}),
        

        
        html.H3(children=f'Total gallons to date: {total_gallons}',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'}),
        
        html.H4(children=f'Active flow: {flow_eval}',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'}),
        
        html.H4(children=f'Last log: {last_log} | {last_gallon} gallon(s)',            
            style={
            'textAlign': 'right',
            'color': 'rgb(0, 0, 0)'}),
        
        html.H4(children=f'AGD: {agd}',            
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

    
    
    #application.debug = True
    application.run()
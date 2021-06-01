from flask import Flask
import dash
import dash_html_components as html
import dash_core_components as dcc
import os
import datetime
import dash_table
from helpers import* 
import base64

pi_pass = os.environ.get('pi_pass')
pgres_pass = os.environ.get('pgres_pass')
pi_hostname = os.environ.get('pi_hostname')


application = Flask(__name__)

image_filename = 'hydreconstack.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(
    __name__,
    server=application
)

def serve_layout():
    
    flow_data=ssh_file(pi_hostname, pi_pass)
    flow_eval_dict=flow_data[0]
    flow_eval=str(flow_eval_dict['flow'])
        
    

    
    
    connection=pgres_com('beef', pgres_pass)
    init_df=pgres_query(f"select* from pulse_detection order by record_date asc", connection).data_frame
    
    init_df["gallons"]=float(0)
    m_recent_df=init_df[init_df.record_date==max(init_df.record_date)]
    
    active_log = datetime.datetime.strptime(flow_eval_dict['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
    active_log = active_log.strftime("%Y %b %d %H:%M")
    
    last_gallon=str(round(max(m_recent_df.total_pulses/26.7)))
    

    last_pulse=(str(max(m_recent_df.record_date)))
    last_pulse = datetime.datetime.strptime(last_pulse, '%Y-%m-%d %H:%M:%S.%f') 
    last_pulse = last_pulse.strftime("%Y %b %d %H:%M")
    
    #New pulse detection is 13.3 pulses per gallon. We double because there are to reed switches at halfway.
    init_df.gallons=round(init_df.total_pulses/26.7)
    total_gallons=round(sum(init_df.gallons))
    
    sums=init_df.resample('D', on='record_date', kind='period').sum()
    sums=sums[sums.total_pulses!=0]
    agd=round(sums.total_pulses.mean()/26.7)
    
    graph_df=init_df.resample('M', on='record_date', kind='period').sum()
    graph_df=graph_df[graph_df.gallons!=0]
    graph_df['record_date']=graph_df.index.strftime("%Y/%m")
    del graph_df['total_pulses']
    graph_df=graph_df[['record_date', 'gallons']]
    
    info_df={'LTD Gallons':str(total_gallons), 
             'Average Gallons /Day': str(agd), 
             'Detection Active':flow_eval, 
             'SSH log':active_log,
             'Last RPi Pulse Log': last_pulse}
    info_df=pd.DataFrame(info_df.items(), columns=['system', 'value'])
    

                              
    timeline_graph = html.Div(children=[
       

       
        html.H1(children='Hydrecon', 
            style={
            'textAlign': 'left',
            'font-family': 'Tahoma',
            'color': 'rgb(9, 16, 87)'}),
    
        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
        width = "750",
        height = "225",         
        style={"position": "relative"
                
                
            }),
    

        
        dcc.Graph(id='example-graph',
              figure={'data': [{'x': graph_df.record_date, 'y': graph_df.gallons, 'type': 'bar', 'name': 'Gallons'}],
                      'layout': {'title': 'Gallons', 'height': 400, 'width': 675}},
              config={
                    'displayModeBar': False,
                    'displaylogo': False,                                       
                    'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines'] 
                    }),
        
   
         

         
        dash_table.DataTable(
            id='info_table',
            columns=[{"name": i, "id": i} for i in info_df.columns],
            data=info_df.to_dict('records'),
            style_table={
                'whiteSpace': 'normal',
                'width': 600,},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(31,119,180)',
                'fontWeight': 'bold',
                'color': 'white'}
            ),   

        
        html.H4(children=''),
        
         
        

        
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in graph_df.columns],
            data=graph_df.to_dict('records'),
            style_table={
                'whiteSpace': 'normal',
                'width': 600,},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'gray',
                'fontWeight': 'bold'}    
                
            )

        
        ])

    return timeline_graph
    

app.layout = serve_layout

if __name__ == "__main__":

    application.debug = True
    application.run()
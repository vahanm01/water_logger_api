
import psycopg2
import pandas as pd
import paramiko
import json

class pgres_query: 
    def __init__(self, query, connection):
        query_data_dict=list()
        cursor = connection.cursor()
        cursor.execute(query)
        query_fetch = cursor.fetchall()
        cols = list(map(lambda x: x[0], cursor.description))
        col_dict= {k: v for k, v in enumerate(cols)}

        for item in query_fetch:
            temp_dict = dict()
            tuple_item=item
            query_dict={k: v for k, v in enumerate(tuple_item)}
            for k1, v1 in col_dict.items():
                for k2, v2 in query_dict.items():
                    if k1 == k2:
                        temp_dict[v1]=v2
            query_data_dict.append(temp_dict)
            
        connection.close()
        
        self.list_dict=query_data_dict
        self.data_frame=pd.DataFrame(query_fetch, columns=cols)


#PGres connection manager. 
def pgres_com(user, password):
    connection = psycopg2.connect(user = user,
                                  password = password,
                                  host = "water-logger.cmoec5ph6uhr.us-east-1.rds.amazonaws.com",
                                  port = "5432",
                                  database = "raw_logs")
    return connection


def ssh_file(pi_hostname, pi_pass):
    
    client=paramiko.client.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    client.load_system_host_keys()
    client.connect(hostname=pi_hostname, port=22, username='pi', password=pi_pass)
    sftp_client = client.open_sftp()
    
    stdin, stdout, stderr = client.exec_command(' pgrep -f -u pi pulse_counter.py')
    pulse_live=stdout.read().decode("utf-8").strip('\n')
    
    localFilePath='./detector_output.json'
    sftp_client.get('/home/pi/water_logger/detector_output.json', localFilePath)
        
    sftp_client.close() 

    with open(localFilePath) as detector_output:
      flow_data = json.load(detector_output)
      
    return flow_data, pulse_live
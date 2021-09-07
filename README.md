# Hydrecon (https://hydrecon.com/)

Hydrecon is a RPi powered home water monitoring system. 
It is capable of real-time water tracking, as well as recording usage to an external DB.
Using Flask, we are able to ping the RPi and also gather historical data for analytics use cases.

Specs:
RPi Model 3B+
EKM water meter with dual reed switches
https://www.ekmmetering.com/collections/water-meters/products/3-4-water-meter-stainless-steel-high-definition-pulse-output


## Install AWS and EB CLI

Depending on your machine, you can find AWS CLI installation instructions here:
https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

Once installed, configure your AWS enviroment. 
You will need your locale, key id, access key, and default output format.

```bash
aws configure
```
To install EB CLI on your machine, run the command below:

```bash
pip install awsebcli --upgrade --user
```

## Deploying to Elastic Beanstalk
EB requires a dependencies file (requirements.txt). The standard file name is application.py which the service looks for. 
By default, gitignore removes the .elasticbeanstalk dir.
Essentially, you need your application.py and requirements.txt file for EB to deploy an environment. 

Before initializing the new envirnoment, make sure the application.py file is not in debug mode:

```python

#Run app
if __name__ == '__main__':

    application.run()
    
    #Debug is not connected
    #application.run(host='0.0.0.0',port='5001', debug=True)
    
```

Within the project directory, run the following commands to create an EB environment and deploy the API. 


```bash
eb init -p python-3.6 remote-water-measure --region us-east-1
eb create remote-water-measure
```

## Setting EB environment variables
In order to mask our passwords, we set environment variables and read within the Python script.

```bash
eb setenv key=value
```
To read the key/value pairs into your python environment...

```python
import os
var_name = os.environ.get('key')
```

## EB helpful commands

```bash
#to delete your enviroment
eb terminate <environment_name>

#deploy code changes
eb deploy

#upgrade environment to latest version
eb upgrade

#gather logs from environment
eb logs -a 
```

## HTTPS setup

For the EB environment to properly function via HTTPS, we need to request a new SSL cert and upload to AWS Certificate Manager.

IT will need to point our DNS to the EC2 load balancer address of our EB environment:
**hydrecon.com IN CNAME <key from Cert Manager>**

Lastly we add a listener to the load balancer where we terminate HTTP and allow secure connection:

- Load Balancer Protocol = HTTPS (Secure HTTP)
- Load Balancer Port = 443
- Instance Protocol = HTTP
- Instance Port = 80
- Select the uploaded SSL


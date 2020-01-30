import boto3
from botocore.vendored import requests
import sys, os, calendar, json
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


#---------------------------------------------------------------------------------------------------------
# AUTHOR 		: Charith Deshapriya
# USAGE 	   	: Get Signal Sciences agent versions for all the sites to validate agents with old versions. 
# DATE			: Jan 26, 2020
#---------------------------------------------------------------------------------------------------------
#lambda Python2.7
#---------------------------------------------------------------------------------------------------------
#Global variables
#---------------------------------------------------------------------------------------------------------
#----------------------------------------------------
AWS_REGION="us-east-1"
SENDER = "sender@email.com"
RECIPIENT = "recipient@email.com"
to_emails = ['email1,email2,emakil3']

endpoint = 'https://dashboard.signalsciences.net'

#if SigSci username/email has upper case
email=str.lower('sigsci-user@email.com');

#if api user
#password='';

#sigsci corp name
corp_name='corp';

def sendEmail():
	
	ses = boto3.client('ses')
	msg = MIMEMultipart()
	msg['Subject'] = 'The SigSci agents validation '
	msg['From'] = SENDER
	msg['To'] = RECIPIENT
	
	# what a recipient sees if they don't use an email reader
	msg.preamble = 'Multipart message.\n'
	
	# the message body
	part = MIMEText('Hi!... here is the agent versions data from the SigSci, This is an automated notification.')
	msg.attach(part)
	
	# the attachment
	part = MIMEApplication(open('sigsci.csv', 'rb').read())
	part.add_header('Content-Disposition', 'attachment', filename='sigsci.csv')
	msg.attach(part)
	
	result = ses.send_raw_email(
	    Source=msg['From'],
	    Destinations=to_emails,
	    RawMessage={'Data': msg.as_string()}
	)                                                                                                       
	# and send the message
	print result

def lambda_handler(event, context):

	#sigSci token auth
	headers = {
		'Content-type': 'application/json',
		'x-api-user': email,
		'x-api-token': 'XXXX-XXXX-XXXX-sigsci token'
	}


	## Fetch list of sites
	url_getcorp = str.lower(endpoint + ('/api/v0/corps/%s/sites' % (corp_name)))
	response_raw = requests.get(url_getcorp, headers=headers)
	response_s = json.loads(response_raw.text)
	print url_getcorp
	print response_raw
	
	os.chdir('/tmp')
	file = open('sigsci.csv',"a")
	file.write('Agent Name, Agent Version \n')
	
	for request in response_s['data']:
	    #print request
	    site_name = str(request.get('name'))
	    file.write('SiteName::'+site_name.rstrip()+'\n')
		#file.write('-------------------Site---------------------')
		
		#file.write('--------------------------------------------\n')

	    print '===========>' + site_name
	    
	    #build api url for agent data per site 
	    url = str.lower(endpoint + ('/api/v0/corps/%s/sites/%s/agents' % (corp_name, site_name)))
	    print url;
	    
	    response_raw2 = requests.get(url, headers=headers);
	    response_s2 = json.loads(response_raw2.text);
	    
	    for request2 in response_s2['data']:
	    	file.write(request2['agent.name'].rstrip())
	    	file.write(',')
	    	file.write(request2['agent.version'].rstrip())
	    	file.write('\n')
	    	print request2['agent.name'].rstrip()
	    	print request2['agent.version'].rstrip()

	file.close();
	sendEmail();
	with open('sigsci.csv', 'r') as content_file:
		content = content_file.read()
		print content;
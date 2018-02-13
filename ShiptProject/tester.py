from urllib import urlencode
from httplib2 import Http
import json
import sys
import base64


print "Running Endpoint Tester....\n"
address = raw_input("Please enter the address of the server you want to access, \n If left blank the connection will be set to 'http://localhost:5000':   ")
if address == '':
	address = 'http://localhost:5000'

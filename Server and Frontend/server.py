import time
import os
import socket
import ssl
import json
import paho.mqtt.client as mqtt
import threading
import statistics
from flask import Flask, render_template

'''
------------------------- Global Variables to catch the MQTT received data ---------------------------------
'''

data = ''
rec_data = list()
personList = dict()

#TimeStamp
timeSt = ''

#Current time in HH:MM:SS:ms
currentTime = ''

#Radiation Value
RadVal = ''

#Room Occupancy count
OccpCnt = ''

#Employee specific data
EmpName = ''
BloodGrp = ''
Designation = ''
inUID = ''
outUID = ''

#Room Number
RoomNum = ''

#Light Indicators
Light_1 = ''
Light_2 = ''


'''
------------------------ Global Variables to catch the MQTT received data ----------------------------------
'''

'''
-------------------------Actuation Variables----------------------------------------------------------------
'''
emergencyLedActuate = 0
orangeLedActuate = 0
doorActuate = 0
buzzerActuate = 0
uiActuate = 0
greenLed = 1
emergencyLights = 'OFF'
alarm = 'OFF'
door = 'CLOSED'

'''
-------------------------Actuation Variables End------------------------------------------------------------
'''

'''
-------------------------Flag Variables for Program execution control --------------------------------------
'''
flaghigh = 0
flagmid = 0
msg_flag = False
connflag = False
'''
-------------------------Flag Variables for Program execution control end ----------------------------------
'''

'''
-------------------------MQTT related Variables ------------------------------------------------------------
'''
userdata = 'applicationReceiver'

#The messages from Raspberry Pi would be received on topic mqtt_topic_sub
mqtt_topic_sub = 'temp_data'

#The messages from server would be published on topic mqtt_topic_pub
mqtt_topic_pub = 'actuation'
'''
-------------------------MQTT related Variables end --------------------------------------------------------
'''

#Object of Flask created
app = Flask(__name__)

'''
-------------------------AWS connection credentials --------------------------------------------------------
'''
awshost = "a24ii9z98yjl2b-ats.iot.eu-central-1.amazonaws.com"
awsport = 8883
clientid = "Raspberry-pi-thing"
thingName = "Raspberry-pi-policy"
caPath = "C:\\Users\\shrek\\Desktop\\frontend\\AmazonRootCA1 (1).pem"
certPath = "C:\\Users\\shrek\\Desktop\\frontend\\83d8428b03-certificate.pem.crt"
keyPath = "C:\\Users\\shrek\\Desktop\\frontend\\83d8428b03-private.pem.key"
'''
-------------------------AWS connection credentials end ----------------------------------------------------
'''
'''
-------------------------Lists to display the radiation data -----------------------------------------------
'''
#These data structures are used to display the charts for the radiation data. They are rendered in page 
#linecharts.html

currentTime = list()

labels = list()

values = list()

labels2_radiation = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

values2_radiation = list()
'''
-------------------------Lists to display the radiation data end --------------------------------------------
'''

'''
This is the function for the on_connect callback of the paho-mqtt-client. Sets the connflag to True when 
connected to the AWS
'''
def on_connect(client, userdata, flags, rc):
    global connflag
    print ("Connected to AWS")
    connflag = True
    print ("Connection returned result: "+ str(rc))
    
'''
This function is the associated function for the on_message callback. Executed when the messages are received from 
the subscribed channel.

Usage: In this function, we have captured the mqtt messages, converted them from byte to JSON and stored them into 
the relevant data structures. We have performed some basic operations on some of the messages to ensure that we dont
lose the message and miss out on certain basic processing. Then these data structures are used in the relevant places
in the code. This ensures we have the data structures updated with the live mqtt data received.
'''  
def on_message(client, userdata, msg):
	global data, msg_flag, rec_data, timeSt, RadVal, OccpCnt, values, currentTime, values2_radiation, labels, inUID, outUID, personList, Light_1, Light_2
	msg_flag = True
	data = json.loads(msg.payload)
	rec_data = [data['timeStamp'], data['IN_UID'], data['OUT_UID'], data['RoomNumber'], data['OccupancyCount'], data['EmployeeName'], data['BloodGroup'], data['Designation'], data['radiation_value'], data['Light_bulb_one'], data['Light_bulb_two']]
	#rec_data = [data['timeStamp'], data['currentTime'], data['RadiationData'], data['RoomNumber'], data['OccupancyCount'], data['PersonalData']]
	OccpCnt = rec_data[4]
	RadVal = rec_data[8]
	inUID = rec_data[1]
	outUID = rec_data[2]
	EmpName = rec_data[5]
	Light_1 = rec_data[9]
	Light_2 = rec_data[10]
	timeSt = rec_data[0]

	radiationInt = float(RadVal)
	inUID = int(inUID)
	outUID = int(outUID)

	#Get the time part from the timestamp, neglect the date.
	currentTime = timeSt.split(' ')

	#Set Light_1 and Light_2 depending on the data received.
	if Light_1 == '1':
		Light_1 = 'ON'
	else:
		Light_1 = 'OFF'

	if Light_2 == '1':
		Light_2 = 'ON'
	else:
		Light_2 = 'OFF'

	#Add the person in the list if inUID is valid. Remove from the list if outUID is valid.
	if inUID:
		if inUID != 871034722729:
			personList.update({inUID:EmpName})
	elif outUID:
		personList.pop(outUID)

	#Append the radiation value and current time to the lists for 10 values. If the length of the
	#list goes beyond 10 then reset the list.

	if len(values) < 11:
		values.append(radiationInt)
		labels.append(currentTime[1])
	else:
		del values[:]
		del labels[:]

	#Get the mean of 10 radiation values and store in a list. If the length of list goes beyond 7 then
	#reset the list.
	if (len(values)/2) == 5:
		values2_radiation.append(statistics.mean(values))

	if len(values2_radiation) > 7:
		del values2_radiation[:]

'''
This function has the mqtt loop_forever which keeps checking for the messages on the subscribed topic. We have
implemented this function call in a thread to make sure the code does not hang in the loop_forever.
'''
def mqttDataReceive():
	receiver.subscribe(mqtt_topic_sub)
	receiver.loop_forever()

'''
The function parses the highout.txt file generated after we hit the emergency. This file contains the plan for
actuation during emergency. After parsing, the parsed data is used to set the necessary actuation variables.
'''
def parsePlannerHighFile():
	f = open("highout.txt", 'r+')
	lines = f.readlines()
	f.close()

	for i in range(len(lines)):
		if 'led' in lines[i]:
			if 'on' in lines[i]:
				global emergencyLedActuate
				emergencyLedActuate = 1
				

		if 'door' in lines[i]:
			if 'open' in lines[i]:
				global doorActuate
				doorActuate = 1
				

		if 'ui' in lines[i]:
			if 'on' in lines[i]:
				global uiActuate
				uiActuate = 1
				

		if 'buzzer' in lines[i]:
			if 'on' in lines[i]:
				global buzzerActuate
				buzzerActuate = 1
				
'''
This function sets the the UI actuation variables, they change the status on the UI depending on the other 
conditions.
'''
def setEmergencyData():
	global emergencyLights, alarm, door
	if emergencyLedActuate == 1:
		emergencyLights = 'ON'
	else:
		emergencyLights = 'OFF'
	if buzzerActuate == 1:
		alarm = 'ON'
	else:
		alarm = 'OFF'
	if doorActuate == 1:
		door = 'OPEN'
	else:
		door = 'CLOSED'


'''
The function parses the midout.txt file generated after we hit the mid radiation level. This file contains the plan for
actuation during this stage. After parsing, the parsed data is used to set the necessary actuation variables.
'''
def parsePlannerMidFile():
	f = open("midout.txt", 'r+')
	lines = f.readlines()
	f.close()

	for i in range(len(lines)):
		if 'turnonorange' in lines[i]:
			global orangeLedActuate
			orangeLedActuate = 1
			

		if 'buzzer' in lines[i]:
			if 'on' in lines[i]:
				global buzzerActuate
				buzzerActuate = 1
				

'''
In this function, we invoke the Planner.py script which takes the two PDDL files as inputs and generate a plan. 
The invoke action depends on the radiation value. After the plan is generated, the result is published back to 
the Raspberry Pi on the topic mqtt_topic_pub for the actuations. This function is a continuous loop, so is called
in a thread.
'''
def mqttDataPublish():
	while(1):
		if connflag == True:

			if RadVal:
				global flaghigh, flagmid, emergencyLedActuate, doorActuate, uiActuate, buzzerActuate, orangeLedActuate, greenLed
				radiationLevel = int(RadVal)

				#Invoke the Planner.py for high level of radiation and call parsePlannerHighFile()
				if (radiationLevel >= 1200):
					flaghigh = flaghigh + 1
					greenLed = 0
					if flaghigh == 1:
						myCmd = 'python Planner.py highcasedomain.pddl highcaseproblem.pddl highout.txt'
						os.system(myCmd)
						parsePlannerHighFile()
				#Invoke Planner.py for mid level of radiation and call parsePlannerMidFile()
				elif (radiationLevel >= 200 and radiationLevel < 1001):
					flagmid = flagmid + 1
					greenLed = 0
					if flagmid == 1:
						myCmd = 'python Planner.py midcasedomain.pddl midcaseproblem.pddl midout.txt'
						os.system(myCmd)
						parsePlannerMidFile()

					emergencyLedActuate = 0
					doorActuate = 0
					uiActuate = 0
					flaghigh = 0
					buzzerActuate = 0
				else:
					flaghigh = 0
					flagmid = 0
					emergencyLedActuate = 0
					doorActuate = 0
					uiActuate = 0
					orangeLedActuate = 0
					buzzerActuate = 0
					greenLed = 1

				setEmergencyData()

			#Publish the data back to RPi in JSON format.
			pubData = json.dumps({"emergencyLedActuate": emergencyLedActuate,
						"doorActuate": doorActuate,
						"orangeLedActuate": orangeLedActuate,
						"uiActuate": uiActuate,
						"buzzerActuate": buzzerActuate,
						"greenLed": greenLed})
			receiver.publish(mqtt_topic_pub, pubData,0)
			print ("Data published back: {}".format(pubData))
			time.sleep(0.5)
 
'''
The mqtt client object creation and associate the callbacks defined.
'''
receiver = mqtt.Client(userdata)
receiver.on_connect = on_connect
receiver.on_message = on_message

'''
Certificates validation for connecting to AWS.
'''
receiver.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
receiver.connect(awshost, awsport, keepalive=60)

'''
Routes the html page on localhost:5000 in the browser. This is the main UI page. The functions mqttDataReceive and 
mqttDataPublish are called in thread here.
'''
@app.route('/')
def rec_data():	
	t1 = threading.Thread(target=mqttDataReceive)
	t2 = threading.Thread(target=mqttDataPublish)
	t1.start()
	t2.start()
	return render_template('graph3.html')


'''
This route function returns the data which is used by the JavaScript AJAX call to display on the UI.
'''
@app.route('/data', methods=['GET','POST'])
def return_data():
	try:
		print ("RadVal: {}".format(RadVal))
		return (json.dumps({"RadVal":RadVal,
		    "OccpCnt":OccpCnt,
		    "RoomNum":RoomNum,
		    "Light_1":Light_1,
		    "Light_2":Light_2,
		    "emergencyLights":emergencyLights,
		    "alarm":alarm,
		    "door":door,
		    "timeSt":timeSt}))

	except Exception:
		print ("Error Exception")
		return (json.dumps({
			"status": "failure",
			"message": "Invalid request"
		}))

'''
This route renders the html page to display the radiation value charts.
'''
@app.route('/chart', methods=['GET','POST'])
def chart():
	return render_template('linecharts.html', title='Radiation Data', max=2000, labels=labels, values=values, labels2_radiation=labels2_radiation, values2_radiation=values2_radiation)

'''
This route renders the html page to display the list of people in the building.
'''
@app.route('/personaldata', methods=['GET','POST'])
def personaldata():
	return render_template('personaldata.html', personList=personList)

'''
Run the flask application using its object.
'''
if __name__ == '__main__':
	try:
		app.run(debug=True)
		print("Executed try")
	except:
		print ("Exception!!!")

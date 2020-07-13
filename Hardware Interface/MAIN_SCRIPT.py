import RPi.GPIO as GPIO
import datetime
import time
import os
import socket
import ssl
import random
import paho.mqtt.client as mqtt
import json
import threading
import MFRC522       #importing package for "in" rfid reader
import MFRC5221      #importing package for "out" rfid reader
import signal
import spidev
from random import randint
from SimulatedNuclear import NuclearSensor

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
lowLed = 19     # led to indicate low level radiation
HighLed = 6     # led to indicate High level radiation
midLed = 5      # led to indicate mid level  radiation
servo_door = 3   #pin for servo_motor
buzzer = 13      #pin for buzzer
second_light = 12   #pin for second room light
first_light = 26    #pin for first room light

# setting as a output
GPIO.setup(HighLed, GPIO.OUT)
GPIO.setup(midLed, GPIO.OUT)
GPIO.setup(lowLed, GPIO.OUT)
GPIO.setup(servo_door, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(first_light, GPIO.OUT)
GPIO.setup(second_light, GPIO.OUT)


# object for servo motor
pwm = GPIO.PWM(servo_door, 50)        # GPIO 3 for PWM with 50Hz
pwm.start(0)                          # Initialization



backward = 15
forward = 14
first_ir = 17     #PIN FOR IR SENSOR TO DETECT THE PERSON IN FIRST ROOM
second_ir=27      #PIN FOR IR SENSOR TO DETECT THE PERSON IN SECOND ROOM

#SETTING AS A INPUT for IR SENSOR
GPIO.setup(first_ir, GPIO.IN)
GPIO.setup(second_ir, GPIO.IN)

ReadCount = 2
continue_reading = True
currentmillis = 0
previousmillis = 0
device = 0
interval = 2000
emp_data =[]
out_list=[]
entry_status=0
exit_status = 0
count=0
first_status=0
person_entered = 2
second_status=0
backward_status = 0
forward_status = 0
Light_1_status = 0
Light2on=0
Light1on=0
Light_2_status = 0
Light_3_status = 0
L2status=0
i=0
j=0
connflag = 0
mqtt_topic_pub = "temp_data"
mqtt_topic_sub = "actuation"
subscribed_data=[]
extract_data=[]
emp_data_rec = []
out_data_rec=[]
emergencyLed = 0
doorAction = 0
orangeLed = 0
buzzerAction = 0
outID=0
IOstatus=0
CM=0
PM =0
count=0
second_uid = 0
emergency_status=2

#uid of RFID TAGS
user1_id = 48881407472
user2_id = 251131271887
user3_id = 871034722729


i=0

def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# FUNCTION FOR OPENING AND CLOSING THE DOOR IN NORMAL CONDITION
def open_door():
    a=0
    while(a<8):                          #open the door
        a=a+2
        pwm.ChangeDutyCycle(a)
        time.sleep(0.1)
    time.sleep(1)
    a=7
    while(a>0):                           #close the door
        a=a-2
        pwm.ChangeDutyCycle(a)
        time.sleep(0.1)

#FUNCTION FOR OPENING AND CLOSING THE DOOR IN EMERGENCY CONDITION
def door_emergency():
    b=0
    while(b<8):                          #open the door
        b=b+2
        pwm.ChangeDutyCycle(b)
        time.sleep(0.1)
    time.sleep(10)
    b=8
    while(b>0):                           #close the door
        b=b-2
        pwm.ChangeDutyCycle(b)
        time.sleep(0.1)
    

   
#FUNCTION FOR READING THE UID,NAME, BLOOD GROUP, AND DESIGNATION FROM "IN" READER
def InReader():
    global emp_data
    global entry_status
    emp_data = [0,0,0,0]
    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

     # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    stat = status

    if (status) == MIFAREReader.MI_OK:
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        ID = n

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        #Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        #Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        status1 = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 9, key, uid)
        status2 = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 10, key, uid)
        name = ''
        blood = ''
        designation = ''
        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            sector = MIFAREReader.MFRC522_Read(8)  #storing name in sector 8

            if sector:
                name = ''.join(chr(i) for i in sector)       #reading name of the person

                
        if status == MIFAREReader.MI_OK:
            sector = MIFAREReader.MFRC522_Read(9)  #storing blood_group in sector 9
            if sector:
                 blood = ''.join(chr(j) for j in sector) #reading the blood group


                
        if status == MIFAREReader.MI_OK:
            sector = MIFAREReader.MFRC522_Read(10)  #storing designation in sector 10
            if sector:
                 designation = ''.join(chr(k) for k in sector)  #reading the designation

            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print ("Authentication error")
            
        
        if(stat==0):
            if (ID == 251131271887 or ID == 48881407472):      #CHECKING FOR THE VALID UIDs
                entry_status = 1
        emp_data = [ID, name, blood,designation]
        
                     
    
    return emp_data    #returning all information of the person

           
#FUNCTION FOR READING THE UID FROM "OUT" READER
def OutReader():
    global exit_status
    global out_list
    global second_uid
    out_list = 0
    second_uid = 0
    (second_status,second_TagType) = MIFAREReader1.MFRC522_Request(MIFAREReader1.PICC_REQIDL)
    (second_status,uid2) = MIFAREReader1.MFRC522_Anticoll()
    stat1 = second_status
   
    if second_status == MIFAREReader1.MI_OK:
        m = 0
        for i in range(0, 5):
            m = m * 256 + uid2[i]
        second_uid = m
        key1 = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader1.MFRC522_SelectTag(uid2)

        #  Authenticate
        second_status = MIFAREReader1.MFRC522_Auth(MIFAREReader1.PICC_AUTHENT1A, 8, key1, uid2)
       
        # Check if authenticated
        if second_status == MIFAREReader1.MI_OK:
            second_sector = MIFAREReader1.MFRC522_Read(8)
            MIFAREReader1.MFRC522_StopCrypto1()
            
        else:
            print ("Authentication error")
        InOutstatus = 0    
        if(stat1 == 0):
            exit_status = 1
        if exit_status ==1:
            return (second_uid)
        else:
            return 1


#FUNCTION TO COUNT NO OF PERSON PRESENT IN THE ROOM
def count_person():
        global count
        global i
        global j
        global k
        global exit_status
        global entry_status
        global forward_status
        global first_status
        global backward_status
        global second_status
        global Light_1_status
        global Light_2_status
        global Light_3_status
        global L2status
        global Light2on
        i = GPIO.input(first_ir)      # READING FROM FIRST IR SENSOR
        j = GPIO.input(second_ir)     #READING FROM SECOND IR SENSOR
        if exit_status == 1:
            backward_status = 1
        if entry_status == 1:
            forward_status = 1
            
        if forward_status == 1:
            if i == 0:
                first_status = 1
            if first_status == 1:  # COUNT OF THE PERSONS PRESENT IN THE ROOM INCREASES WHEN PERSON WHO IS HAVING THE ACCESS CUTS THE FIRST ir sensor
                count = count + 1
                forward_status = 0
                first_status = 0
                entry_status = 0
                Light_1_status = 1
                Light1on=1
                Light_2_status = 0
                
                    
        if Light_1_status == 1:   #check if person goes to second room.If presense detected then turn on the light
            if j == 0:
                 Light2on = 1
                 send_data()
                 GPIO.output(second_light,GPIO.HIGH)
                 time.sleep(10)
                 GPIO.output(second_light,GPIO.LOW)
                 Light2on=0
                 send_data()
           
        if backward_status == 1:        #logic to show decrement in no of occupants
           if i == 0:
               second_status = 1
           if second_status == 1:
               count = count -1
               backward_status = 0
               second_status = 0
               exit_status = 0
               #print("open door")
               open_door()
               if count < 0:
                   count = 0
               #print ('no of person',count)
               #print ('person out')
               
        if count == 0:            #when no one is present inside the room, all status are set to zero
            Light_1_status = 0
            Light_2_status = 0
            Light2on=0
            Light1on=0
        
        return (count,Light_1_status,Light_2_status)


#this fucntion will execute when connection to aws server gets established
def on_connect(client, userdata, flags, rc):
    global connflag
    print ("Connected to AWS")
    connflag = 1
    print ("Connection returned result: "+ str(rc))


# receiving the data from the server
def on_message(client, userdata, msg):
    global subscribed_data
    global extract_data
    global emergencyLed
    global doorAction
    global orangeLed
    global buzzerAction

    subscribed_data=json.loads(msg.payload)
    extract_data= [subscribed_data['emergencyLedActuate'],subscribed_data['doorActuate'],subscribed_data['orangeLedActuate'],subscribed_data['uiActuate'],subscribed_data['buzzerActuate'],]
    emergencyLed = int(extract_data[0])
    doorAction = int(extract_data[1])
    orangeLed = int(extract_data[2])
    buzzerAction = int(extract_data[3])

#function for debugging purpose
def get_data():
    return random.uniform(20,25)

#send the data to the server
def send_data():
    
    payload = '{"timeStamp": '+'"'+str(timeStamp)+'","IN_UID": '+'"'+str(emp_data_rec[0])+'","OUT_UID": '+'"'+str(outID)+'", "RoomNumber": '+'"'+str(100)+'", "OccupancyCount": '+'"'+str(occupancy_count)+'", "EmployeeName": '+'"'+str(emp_data_rec[1])+'","BloodGroup": '+'"'+str(emp_data_rec[2])+'","Designation": '+'"'+str(emp_data_rec[3])+'","radiation_value": '+'"'+str(s.number)+'","Light_bulb_one": '+'"'+str(Light_1_status)+'","Light_bulb_two": '+'"'+str(Light2on)+'"}'
    myclient.publish("temp_data", payload, 0)
    print (payload)
    
#certificates for AWS
awshost = "a24ii9z98yjl2b-ats.iot.eu-central-1.amazonaws.com"         #Endpoint
awsport = 8883
clientid = "Raspberry-pi-thing" #Thing name
thingName = "Raspberry-pi-policy"
caPath = "/home/pi/Downloads/AmazonRootCA1 (1).pem"
certPath = "/home/pi/Downloads/83d8428b03-certificate.pem.crt"
keyPath = "/home/pi/Downloads/83d8428b03-private.pem.key"

myclient = mqtt.Client()
myclient.on_connect = on_connect
myclient.on_message = on_message

myclient.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
myclient.connect(awshost, awsport, keepalive=60)
myclient.loop_start()
myclient.subscribe(mqtt_topic_sub)


#class for simulation of the radiation sensor
class Simulator:
    def __init__(self):
        self.delay = 1
        self.number = 0
        self.extend = 10
        self.num = 0
        self.CM = 0
        self.PM = 0
 
    def start(self):
        ns = NuclearSensor(1,11000,90,['low','medium','very_high'])
        self.number = ns.cps()  #generate pulses per second (counts per second=CPS) CPS IS ONE OF THE UNITS OF RADIATION
        
        time.sleep(1)
        if self.number < 11:
            GPIO.output(lowLed,GPIO.HIGH)
            GPIO.output(midLed,GPIO.LOW)
            GPIO.output(HighLed,GPIO.LOW)
        send_data()
        if 'very_high' in ns.senseType:     #generating higher number of the pulses FOR 10 SECONDS
            if self.number > 1200:
                for i in range(9):
                    timeStamp = datetime.datetime.now()
                    self.number = ns.Generate(1200,2000)
                    time.sleep(1)
                    send_data()
                    
                    
        if 'medium' in ns.senseType:     #GENERATING MEDIUM NUMBER OF THE PULSES FOR 5 SECONDS
            if self.number > 200:
                for i in range(4):
                    self.num = 0
                    timeStamp = datetime.datetime.now()
                    self.number = ns.Generate(200,1000)
                    time.sleep(1)
                    send_data()
                
s = Simulator()        #OBJECT FOR SIMULATOR CLASS

def radiationThread():  #THREAD FOR SIMULATOR CLASS
    while 1:
        s.start()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

MIFAREReader1 = MFRC5221.MFRC522()         #OBJECT FOR "OUT" READER
# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()           #OBJECT FOR "IN" READER

        

try:
    thread = threading.Thread(target=radiationThread)
    thread.start()
    GPIO.output(HighLed,GPIO.LOW)
    GPIO.output(midLed,GPIO.LOW)
    GPIO.output(buzzer, GPIO.LOW)
    GPIO.output(lowLed, GPIO.LOW)
    GPIO.output(first_light, GPIO.LOW)
    GPIO.output(second_light, GPIO.LOW)

    while (1):
        if connflag == 1:      #CHECK FOR THE CONNECTION WITH THE SERVER
            second_uid = OutReader()   #READ UID FROM OUT READER
            if second_uid==None:
                outID = 0
            else:
                outID = second_uid
            emp_data_rec = InReader() # READING THE DATA FROM "IN" READER
            data = get_data()
            timeStamp = datetime.datetime.now()

            
            if emergencyLed == 1:    #CHECKING FOR THE HIGHER LEVEL OF RADIATION. "emergencyLed" is the output of the AI planner
                

                GPIO.output(HighLed,GPIO.HIGH)   #high radiation- turn on RED led
                GPIO.output(midLed,GPIO.LOW)
                GPIO.output(lowLed,GPIO.LOW)
                if buzzerAction == 1:            #turn on the buzzer.."buzzerAction" is output of the AI planner
                    GPIO.output(buzzer,GPIO.HIGH)
                GPIO.output(first_light,GPIO.HIGH)     # turn on lights in the first and second room during the emergency condtion
                GPIO.output(second_light,GPIO.HIGH)
                Light2on=1
                Light1on=1
                Light_1_status=1
                if emergency_status !=0:
                    emergency_status = 1
                if emergency_status ==1:
                    if  doorAction == 1:    #"doorAction" is the output of the AI planner
                        door_emergency()   #open the door
                    emergency_status = 0
                block_everything = 1
            else:
                Light2on =0
                Light1on = 0
                block_everything = 0
                emergency_status = 2
                GPIO.output(HighLed,GPIO.LOW) 
                GPIO.output(second_light,GPIO.LOW)
                GPIO.output(buzzer,GPIO.LOW)
            if block_everything == 1:
                pass
            elif block_everything == 0:
                occupancy_count, Light_1_status_1,Light_2_status_1 = count_person()   #receiving occupancy count and other status
                data = get_data()
                Light1on = Light_1_status_1
                
                if orangeLed == 1:          #if medium level of radtion condition hits. "orangeLed" is OUTPUT OF THE AI PLANNER
                    GPIO.output(midLed,GPIO.HIGH)   #turn on mid level led
                    GPIO.output(HighLed,GPIO.LOW)
                    GPIO.output(lowLed,GPIO.LOW)
                else:
                    GPIO.output(midLed,GPIO.LOW)
                 
                
                if emp_data_rec[0] == user1_id or emp_data_rec[0] == user2_id:    #checking for authorized user and open the door
                    open_door()
                elif emp_data_rec[0] == user3_id:    #if unauthorized person tries to access, then blink the midlevel for 8 times
                    for i in range (8):
                        GPIO.output(midLed,GPIO.HIGH)
                        time.sleep(0.5)
                        GPIO.output(midLed, GPIO.LOW)
                        time.sleep(0.5)
                    
                if Light_1_status_1 == 1:  #if person enters in the first room(main room)
                    GPIO.output(first_light,GPIO.HIGH)
                
                if Light_2_status_1 == 1 and Light_1_status_1 == 0:  #if person enters second room ( storage room )
                    GPIO.output(first_light,GPIO.HIGH)
                    GPIO.output(second_light,GPIO.HIGH)
                    
                elif occupancy_count>1:
                    if Light_2_status_1 == 1:
                        GPIO.output(second_light,GPIO.HIGH)
                        GPIO.output(first_light,GPIO.HIGH)
                     
                if occupancy_count == 0:                                 #turn_off all Lights when no one is in the room
                    GPIO.output(first_light,GPIO.LOW)
                    GPIO.output(second_light,GPIO.LOW)
           
             
        else:
            print("Waiting for connection")
        
except KeyboardInterrupt:
  pwm.stop()
  GPIO.cleanup()
  





















'''
#This loop keeps checking for chips. If one is near it will get the UID and authenticate
try:
    while continue_reading:
        OutReader()
        InReader()

      
        if exit_status == 1:
            backward_status = 1
            i= GPIO.input(first_ir)
       
        if entry_status == 1:
            forward_status = 1
            i= GPIO.input(first_ir)
      
        
        if forward_status == 1:
         
            if i == 0:
                first_status = 1
                
            if first_status == 1:
               count = count + 1
               print('no of person', count)
               print('person in')
               forward_status = 0
               first_status = 0
               entry_status = 0
                    
                    
        if backward_status == 1:
           if i == 0:
               second_status = 1
           if second_status == 1:
               count = count -1
               backward_status = 0
               second_status = 0
               exit_status = 0
               if count < 0:
                   count = 0
               print ('no of person',count)
               print ('person out')
       
except KeyboardInterrupt:
        GPIO.cleanup()
'''

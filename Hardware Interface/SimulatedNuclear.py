import random
import time
from random import randint

class NuclearSensor:
    SensorName="GM_TUBE"    #name of the sensor
    TubeType = "zp1200"     #type of the sensor
    unit = "CPS"          #unit of the sensor
    def __init__(self,minCount,maxCount,DeadTime,SensorClass):
        self.minCount = minCount
        self.maxCount = maxCount
        self.DeadTime = DeadTime
        self.SensorClass = SensorClass
        self.senseType = 'low'
        self.currentMillis = 0
        self.previousMillis = 0
        self.interval = 100
        self.count = 0
        count = 0
    def cps(self):
         Stype = self.SenseType()
         if 'very_high' in Stype:
             self.count = self.Generate(1200,2000)    #generate pulses between 1200-2000
             return self.count
         elif 'medium' in Stype:                      #generate pulses between 200-1000
             self.count = self.Generate(200,1000)
             return self.count
         elif 'low' in Stype:                         #generate pulses between 1-10
             self.count =self.Generate(1,10)
             return self.count
            
    def SenseType(self):
        self.senseType = random.choices(self.SensorClass, weights=[1500,5,10])    #defining probability for low, medium and very high pulses respect.
        return self.senseType
        
    def Generate(self, Countmin, Countmax):
        value = randint(Countmin,Countmax)
        time.sleep(0.1)
        return value 

import time
import serial
import re
import sys
import paho.mqtt.client as mqtt

ser = serial.Serial(port='/dev/ttyACM0',baudrate = 19200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
flag = 1
WINDOW = 60
sensorList1 = []
sensorList2 = []



def commandCallBack(client, userdata, message):
   global flag 
   msg = str(message.payload, "utf-8")
   print ("command received")
   if (msg== 'start'):
      flag = 1
   elif (msg == 'end'):
      flag = 0
def originCallBack (client, userdata, message):
   global sensorList1 
   global sensorList2
   global oX
   global oY
   msg = str(message.payload, "utf-8")
   if (msg == 'set'):
      if len(sensorList1) != 0 and len(sensorList2) !=0:
         oX = sensorList1[-1]
         oY = sensorList2[-1]
         print (oX)
         print (oY)
         print ("origin set")
      
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("pololu-13/record")
    client.subscribe("pololu-13/origin")
    client.subscribe("pololu-13/move")
    client.message_callback_add("pololu-13/record", commandCallBack)
    client.message_callback_add("pololu-13/origin", originCallBack)
    
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

def readSerial():
  global sensorList1 
  global sensorList2 
  results = []
  x=ser.readline()
  #print (x)
  try:
   data = x.decode ("ascii")
  except UnicodeDecodeError:
   return 
  try:
   results = re.split('[+ \r \n]',data)
  except ValueError:
   return 
  #print (results)
  try:
   sensorList1.append(int (results[0]))
   #sensorList2.append(int (results[1]))
   sensorList1 = sensorList1[-1*WINDOW:]
   #sensorList2 = sensorList2[-1*WINDOW:]
  except ValueError:
   return 
   
  
def signalProcessing(client):
  global sensorList1
  global sensorList2
  global oX
  global oY
  """if len(sensorList1) > 10 and len(sensorList2) >10:
   #print (sensorList1[-1] - oX)
   print (sensorList1[-1])
   print (sensorList2[-1])
   print ("*************")
   if sensorList1[-1] - sensorList1[-10] > 1:
      client.publish("pololu-13/move",'w')
   elif sensorList1[-1] - sensorList1[-10]< -1:
      client.publish("pololu-13/move",'s')
   else:
      print ("XXXXXX")
   #print (sensorList2[-1] - oY)
   if sensorList2[-1] - sensorList2[-3] > 1:
      client.publish("pololu-13/move",'a')
   elif sensorList2[-1] - sensorList2[-3] < -1:
      client.publish("pololu-13/move",'d')
   else:
      print ("XXXXXX")"""
  if len(sensorList1) == WINDOW:
  	deviat = sum(sensorList1[-20:]) - sum(sensorList1[0:20])
  	if deviat > 200:
  		print ("W")
  		print (deviat)
  		client.publish("pololu-13/move",'w')
  	elif deviat < -200:
  		print ("S")
  		print (deviat)
  		client.publish("pololu-13/move",'s')
  	else:
  		print ("------------")
      
  
def main ():
  global flag
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  while(True):
    if flag == 1:
         readSerial()
         signalProcessing(client)

    
main ()

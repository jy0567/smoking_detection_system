import serial
import os
from twilio.rest import Client
from picamera import PiCamera
from time import sleep
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import threading

#Database
import requests, json
from influxdb import InfluxDBClient as influxdb

#arduino connecting
port = '/dev/ttyACM0'
brate = 9600

global seri
seri = serial.Serial(port, baudrate = brate, timeout=None)
print(seri.name)

#sms
account_sid = 'ACae2d626835186e8a2a307620dc47af78'
auth_token = '30733c014c4a096ec1f839ae50e30cc3'
client = Client(account_sid, auth_token)

#criteria of sensor
level_fire = 200
level_smoke = 140

global check 
check = False

def check_smoke(result):
	res = float(result)
	if res >= level_smoke: #fire or smoke
		if res >= level_fire: #send fire message
			print("fire, ", res)
			
			message = client.messages.create(
				body='A fire broke out!! Need to act quickly!!!',
				from_='+14254752226',
				to='+821083846247'
			)
			print("msg ok")
			
			#camera
			camera = PiCamera()

			camera.start_preview()

			kstDate = datetime.now() + timedelta(hours=9)
			date = kstDate.strftime("%y%m%d_%H:%M")
			
			imageName = '/home/pi/Images/'+date+'.jpg'
			camera.capture(imageName)
			camera.stop_preview()
			camera.close()
			
			
			#email
			smtp = smtplib.SMTP('smtp.gmail.com',587)
			smtp.starttls()
			smtp.login('201844016@itc.ac.kr', 'hnhtfvruuqdboqtq')

			msg = MIMEMultipart()

			msg['Subject'] = '[caution] A fire broke out! Occurrence Date: '+date
			msg['To'] = 'xogur1423@naver.com'
			text = MIMEText('send photo')
			msg.attach(text)
			file_name=imageName
			with open(file_name, 'rb')as file_FD:
				etcPart = MIMEApplication(file_FD.read())
				etcPart.add_header('Content-Disposition','attachment', filename=file_name)
				msg.attach(etcPart)
				smtp.sendmail('201844016@itc.ac.kr','xogur1423@naver.com', msg.as_string())

			smtp.quit()
			print("email ok")
		elif res >= level_smoke and res < level_fire: #send smoke message
			print("smoke, ", res)

			message = client.messages.create(
			  body='Smoking detected! Please check.',
			  from_='+14254752226',
			  to='+821083846247'
			)
			print("msg ok")
			
			#camera
			camera = PiCamera()

			camera.start_preview()

			kstDate = datetime.now() + timedelta(hours=9)
			date = kstDate.strftime("%y%m%d_%H:%M")
			
			imageName = '/home/pi/Images/'+date+'.jpg'
			camera.capture(imageName)
			camera.stop_preview()
			camera.close()
			
			
			#email
			smtp = smtplib.SMTP('smtp.gmail.com',587)
			smtp.starttls()
			smtp.login('201844016@itc.ac.kr', 'hnhtfvruuqdboqtq')

			msg = MIMEMultipart()

			msg['Subject'] = '[caution] Smoking detected! Occurrence Date: '+date
			msg['To'] = 'xogur1423@naver.com'
			text = MIMEText('send photo')
			msg.attach(text)
			file_name=imageName
			with open(file_name, 'rb')as file_FD:
				etcPart = MIMEApplication(file_FD.read())
				etcPart.add_header('Content-Disposition','attachment', filename=file_name)
				msg.attach(etcPart)
				smtp.sendmail('201844016@itc.ac.kr','xogur1423@naver.com', msg.as_string())

			smtp.quit()
			print("email ok")
		#delay & close serial
		global check
		global seri
		check = True
		if check == True:
			seri.close()
			sleep(3)
			seri = serial.Serial(port, baudrate = brate, timeout=None)
			check = False
			print("seri close ok")

while True:
	try:
		#when there are values of sensor
		if seri.readable():
			ret = seri.readline()
			ret = ret[:len(ret)-1].decode()
			print(ret) 
			if ret.find(" ppm") > -1: 
				ret = ret.replace(' ppm', '') 
				ret = ret.replace(' ', '')
				res = ret.split(":")[1]
				print("res: "+ res)
				
				#check value of sensor & send a message
				check_smoke(res)
				
				#Database
				kstDate = datetime.now() + timedelta(hours=9)
				date = kstDate.strftime("%y%m%d_%H:%M")
				data = [{
				    'measurement' : 'pir',        
				    'tags':{
					'VisionUni' : '2410',
				    },
				    'fields':{
					"date": date,
					"concentration" : res
				    }
				}]
				dbClient = None

				#db connect
				try:
					dbClient = influxdb('localhost',8086,'root','root','pir') #connecting to influx db #ip, port, id, pw
					print("db con ok")
				except Exception as e:
				    print ("Exception" + str(e))

				#db input data 
				if client is not None:
					try:
						dbClient.write_points(data) #write
						print("running influxdb OK")
					except Exception as e:
						print ("!!Exception write " + str(e))
					finally:
						dbClient.close()
				#Database
		
		
	except serial.serialutil.SerialException:
		print('no conneting. \n')
		break

	except KeyboardInterrupt:
		print('interrupt. \n')
		break
